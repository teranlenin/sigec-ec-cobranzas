"""Vista Streamlit para reportería de entrenamiento (sin efectos externos)."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as streamlit_runtime

from .metrics import build_daily_series, build_report
from .simulation import DEFAULT_DATA_DIR, LABEL, _jsonl_read, append_cycle, load_dataset

_FRAGMENT = (streamlit_runtime.fragment(run_every=300)
             if hasattr(streamlit_runtime, "fragment") else (lambda function: function))


def _money(value: Any) -> str:
    return "N/D" if value is None else f"USD {value:,.2f}"


def _pct(value: Any) -> str:
    return "N/D" if value is None else f"{value:.2f}%"


@_FRAGMENT
def render_reporting_dashboard(st, px, data_dir: Path | str = DEFAULT_DATA_DIR) -> None:
    """Renderiza el módulo en el objeto Streamlit de la app principal."""
    data_dir = Path(data_dir)
    st.header("📈 Reportería periódica de cartera — simulación")
    st.warning(
        f"{LABEL}. Este módulo usa fixtures locales y canales no enviados; "
        "no es una integración ni una reportería de cartera real."
    )
    st.caption("La vista vuelve a leer los datos cada cinco minutos mientras está abierta. La generación de eventos requiere el comando local explícito o el botón de ciclo único.")
    if not (data_dir / "cases.csv").exists() or not (data_dir / "events.jsonl").exists():
        st.error("No existe el paquete de datos sintéticos de reportería.")
        st.code("python 'Gestión de cobranzas efectivas/scripts/generate_reporting_data.py' --mode initialize")
        return

    try:
        cases, events = load_dataset(data_dir)
        validation = __import__("reporting.simulation", fromlist=["validate_dataset"]).validate_dataset(data_dir)
        cycles = _jsonl_read(data_dir / "cycles.jsonl")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.error(f"No se pudo cargar o validar el reporte sintético: {exc}")
        return

    event_dates = [date.fromisoformat(event["occurred_at"][:10]) for event in events
                   if event.get("event_type") != "case_seeded_simulated"]
    max_date = max(event_dates) if event_dates else date.today()
    min_date = min(event_dates) if event_dates else max_date
    default_start = max(min_date, max_date - timedelta(days=6))

    with st.expander("Control de ciclo sintético local", expanded=False):
        st.caption("El modo en bucle CLI genera un ciclo cada cinco minutos y avanza un día de reloj simulado por ciclo. No activa tareas en segundo plano automáticamente.")
        st.code("python 'Gestión de cobranzas efectivas/scripts/generate_reporting_data.py' --mode loop --interval-seconds 300", language="powershell")
        if st.button("Ejecutar ahora un ciclo sintético único", key="run_reporting_cycle"):
            cycle_result = append_cycle(data_dir, event_count=30)
            st.success(f"Ciclo {cycle_result['cycle_id']}: {cycle_result['appended_events']} eventos agregados; duplicado={cycle_result['duplicate']}.")
            st.rerun()

    with st.form("synthetic_reporting_filters"):
        left, right, manager_col = st.columns([1, 1, 1])
        with left:
            selected_start = st.date_input("Inicio del período", value=default_start,
                                           min_value=min_date, max_value=max_date)
        with right:
            selected_end = st.date_input("Fin del período", value=max_date,
                                         min_value=min_date, max_value=max_date)
        managers = ["Todos"] + sorted({case["manager_id"] for case in cases})
        with manager_col:
            selected_manager = st.selectbox("Gestor sintético", managers)
        submitted = st.form_submit_button("Actualizar reportería")
    if selected_start > selected_end:
        st.error("El inicio del período no puede ser posterior al fin.")
        return

    manager_filter = None if selected_manager == "Todos" else selected_manager
    report = build_report(cases, events, selected_start, selected_end, manager_id=manager_filter)
    last_cycle = max(cycles, key=lambda row: row.get("generated_at", "")) if cycles else {}
    st.caption(
        f"Período simulado: {selected_start}–{selected_end} · America/Bogota · "
        f"casos: {report['case_count']:,} · versión: reporting-synthetic-v3 · "
        f"último ciclo local: {last_cycle.get('cycle_id', 'N/D')} · "
        f"validación: {validation['cases']:,} casos / {validation['events']:,} eventos"
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Saldo inicial del período", _money(report["opening_balance_usd"]))
    k2.metric("Saldo al cierre simulado", _money(report["closing_balance_usd"]))
    k3.metric("Pagos simulados", _money(report["payments_usd"]),
              help="Pagos ficticios del período; no son recuperaciones reales.")
    k4.metric("Tasa de recuperación", _pct(report["recovery_rate_pct"]),
              help="Pagos del período / saldo al inicio del período.")
    k5.metric("Compromisos vencidos", str(report["commitments_due_count"]),
              help="Pendientes y cancelados se muestran aparte; la tasa de cumplimiento usa kept/(kept+missed).")

    tab_exec, tab_gestor, tab_activity, tab_quality = st.tabs([
        "Resumen supervisor", "Detalle de gestor", "Actividad y compromisos", "Calidad y trazabilidad",
    ])

    with tab_exec:
        a, b, c = st.columns(3)
        a.metric("Casos con pagos totales", str(report["full_payment_case_count"]))
        b.metric("Casos con pagos parciales", str(report["partial_payment_case_count"]))
        c.metric("Reducción atribuible a pagos", _money(report["balance_reduction_usd"]))
        st.caption("La reducción del saldo se explica aquí solo por pagos sintéticos. No se simulan quitas, condonaciones ni cargos.")

        daily_df = pd.DataFrame(build_daily_series(
            cases, events, selected_start, selected_end, manager_id=manager_filter
        ))
        if not daily_df.empty:
            trend_left, trend_right = st.columns(2)
            trend_left.plotly_chart(
                px.bar(daily_df, x="date", y="payments_usd", title="Pagos simulados por día (USD)"),
                width="stretch",
            )
            trend_right.plotly_chart(
                px.line(daily_df, x="date", y="closing_balance_usd", markers=True,
                        title="Saldo sintético al cierre diario (USD)"),
                width="stretch",
            )

        aging = report["aging_cases_at_end"]
        if aging:
            aging_df = pd.DataFrame([{"Tramo analítico DPD": bucket, "Casos": count}
                                     for bucket, count in aging.items()])
            fig_aging = px.bar(aging_df, x="Tramo analítico DPD", y="Casos",
                               title="Casos por tramo de mora simulado (al cierre)",
                               color="Tramo analítico DPD")
            st.plotly_chart(fig_aging, width="stretch")
        if report["manager_breakdown"]:
            manager_df = pd.DataFrame([
                {"Gestor sintético": name, "Casos": values["cases"],
                 "Pagos simulados USD": values["payments_usd"],
                 "Tasa de recuperación %": values["recovery_rate_pct"]}
                for name, values in report["manager_breakdown"].items()
            ])
            st.dataframe(manager_df, width="stretch", hide_index=True)

    with tab_gestor:
        if manager_filter is None:
            st.info("Selecciona un gestor sintético en el filtro superior para revisar su cartera de entrenamiento.")
        else:
            manager_report = report["manager_breakdown"].get(manager_filter)
            if not manager_report:
                st.info("Sin casos para el gestor sintético y período seleccionados.")
            else:
                a, b, c = st.columns(3)
                a.metric("Casos asignados en fixture", str(manager_report["cases"]))
                b.metric("Pagos simulados", _money(manager_report["payments_usd"]))
                c.metric("Tasa sobre saldo inicial", _pct(manager_report["recovery_rate_pct"]))
                st.caption("Vista didáctica; no es una medición de desempeño laboral ni permite comparar gestores reales.")
                manager_cases = {case["case_id"] for case in cases if case["manager_id"] == manager_filter}
                manager_events = [event for event in events if event.get("case_id") in manager_cases
                                  and selected_start.isoformat() <= event["occurred_at"][:10] <= selected_end.isoformat()]
                display_events = [{
                    "Fecha simulada": event["occurred_at"],
                    "Caso": event["case_id"],
                    "Tipo": event["event_type"],
                    "Canal simulado": event.get("channel", "—"),
                    "Estado": event.get("commitment_status", event.get("outcome", event.get("verification_status", "—"))),
                    "Ref. sintética": event["source_ref"],
                } for event in manager_events]
                st.dataframe(pd.DataFrame(display_events), width="stretch", hide_index=True)

    with tab_activity:
        c1, c2 = st.columns(2)
        channel_counts = report["channel_counts_simulated"]
        if channel_counts:
            channel_df = pd.DataFrame([{"Canal simulado": key, "Intentos no enviados": value}
                                       for key, value in channel_counts.items()])
            c1.plotly_chart(px.bar(channel_df, x="Canal simulado", y="Intentos no enviados",
                                   title="Actividad de canal ficticia"), width="stretch")
        else:
            c1.info("Sin intentos de canal simulados en este período.")
        statuses = report["commitments_due_by_status"]
        if statuses:
            status_df = pd.DataFrame([{"Estado al corte": key, "Compromisos": value}
                                      for key, value in statuses.items()])
            c2.plotly_chart(px.bar(status_df, x="Estado al corte", y="Compromisos",
                                   title="Compromisos con vencimiento en el período"), width="stretch")
        else:
            c2.info("Sin compromisos con vencimiento en el período.")
        st.metric("Tasa de cumplimiento de compromisos resueltos", _pct(report["commitment_kept_rate_pct"]))
        st.caption(f"Estados vencidos: {json.dumps(statuses, ensure_ascii=False)}. Los compromisos pendientes y cancelados no se clasifican como incumplidos.")
        st.write("**Actualizaciones de contacto ficticias por campo:**", report["contact_updates_by_field"] or "Sin eventos")
        st.write("**Hallazgos sintéticos de investigación:**", report["research_findings_count"])

    with tab_quality:
        st.write("**Cambios de datos por estado de verificación:**", report["contact_updates_by_verification"] or "Sin eventos")
        st.write("**Conteos por transición de tramo:**", report["aging_transition_counts"] or "Sin transiciones")
        st.write("**Resultados simulados de canal:**", report["channel_outcomes_simulated"] or "Sin eventos")
        if report["contact_updates_count"]:
            update_rows = [event for event in events if event.get("event_type") == "contact_data_update_simulated"
                           and event["case_id"] in {case["case_id"] for case in cases
                                                    if not manager_filter or case["manager_id"] == manager_filter}
                           and selected_start.isoformat() <= event["occurred_at"][:10] <= selected_end.isoformat()]
            safe_updates = [{"fecha": row["occurred_at"], "caso": row["case_id"],
                             "campo": row.get("field_name"),
                             "token_anterior": row.get("old_value_token"),
                             "token_nuevo": row.get("new_value_token"),
                             "verificación": row.get("verification_status"),
                             "fuente": row["source_ref"]} for row in update_rows]
            st.dataframe(pd.DataFrame(safe_updates), width="stretch", hide_index=True)
        st.markdown("**Definiciones y limitaciones:**")
        for limitation in report["limitations"]:
            st.markdown(f"- {limitation}")
        st.markdown("**No se usa:** PII, atributos sensibles, neuroperfiles, scoring de solvencia o reglas jurídicas.")

    st.download_button(
        "Descargar resumen del período (JSON)",
        data=json.dumps(report, ensure_ascii=False, indent=2),
        file_name=f"reporte_sintetico_{selected_start}_{selected_end}.json",
        mime="application/json",
    )
