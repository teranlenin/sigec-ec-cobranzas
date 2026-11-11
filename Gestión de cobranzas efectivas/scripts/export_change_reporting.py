#!/usr/bin/env python3
"""Exporta reportería explicativa HTML/Excel del fixture sintético v3."""
from __future__ import annotations

import argparse
import collections
import html
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data" / "reporting_synthetic_v3"
parser = argparse.ArgumentParser(description="Exporta los entregables HTML y Excel del fixture sintético v3.")
parser.add_argument("--output-dir", type=Path, default=DATA / "reports" / "entrega_cambios_2026-11-10",
                    help="Carpeta nueva de salida; por seguridad no debe existir.")
OUT = parser.parse_args().output_dir
if OUT.exists():
    raise FileExistsError(f"No se sobrescribe una entrega existente: {OUT}")
OUT.mkdir(parents=True)

sys.path.insert(0, str(PROJECT))
from reporting.metrics import build_report  # noqa: E402
from reporting.simulation import LABEL, load_dataset, validate_dataset  # noqa: E402

CAUTION = "SIMULACIÓN — NO ENVIAR · NO USAR EN PRODUCCIÓN"
START = date(2026, 11, 3)
END = date(2026, 11, 11)
PERIODS = [
    {"id": "P1", "name": "Periodo 1 · 03–06 nov", "start": date(2026, 11, 3),
     "end": date(2026, 11, 6), "note": "Ventana comparable de 4 días; actividad del baseline."},
    {"id": "P2", "name": "Periodo 2 · 07–10 nov", "start": date(2026, 11, 7),
     "end": date(2026, 11, 10), "note": "Ventana comparable de 4 días; presenta concentración de cambios de estado el 10-Nov."},
    {"id": "P3", "name": "Periodo 3 · 11 nov", "start": date(2026, 11, 11),
     "end": date(2026, 11, 11), "note": "Un día de reloj futuro simulado, generado el 10-Nov; no es actividad real."},
]
TYPE_INFO = {
    "payment_recorded_simulated": ("Pago registrado", "Pago ficticio que reduce el saldo del modelo y se asigna a capital, interés y otros."),
    "commitment_created_simulated": ("Compromiso creado", "Nuevo compromiso simulado; no equivale a pago recibido."),
    "commitment_status_changed_simulated": ("Estado de compromiso actualizado", "Evento de transición de estado; conteos de eventos, no compromisos únicos."),
    "channel_attempt_simulated": ("Intento de canal (no enviado)", "Registro didáctico; entrega marcada como no enviada, no acredita contacto."),
    "contact_data_update_simulated": ("Dato de contacto tokenizado actualizado", "Actualización de marcador sintético; el detalle omite los valores anterior/nuevo."),
    "research_finding_simulated": ("Hallazgo ficticio de investigación", "Hallazgo de entrenamiento, pendiente de validación humana."),
    "dispute_opened_simulated": ("Disputa abierta para revisión", "Evento sintético que requiere revisión humana en el ejercicio."),
    "internal_review_simulated": ("Revisión interna requerida", "Derivación simulada; no representa decisión ni resultado real."),
}
TYPE_LABEL = {k: v[0] for k, v in TYPE_INFO.items()}
STATE_LABEL = {
    "accepted": "Aceptado (simulado)", "kept": "Cumplido (simulado)",
    "missed": "Incumplido (simulado)", "pending": "Pendiente (simulado)",
    "cancelled": "Cancelado (simulado)", "open": "Abierto (simulado)",
}
CHANNEL_LABEL = {
    "email": "Correo (no enviado)", "phone_call": "Llamada (no realizada)",
    "sms": "SMS (no enviado)", "whatsapp_message": "WhatsApp (no enviado)",
    "written_notice": "Aviso escrito (no enviado)",
}
OUTCOME_LABEL = {
    "draft_created_not_sent": "Borrador creado; no enviado",
    "reply_simulated": "Respuesta simulada", "no_response_simulated": "Sin respuesta simulada",
}
FIELD_LABEL = {
    "address_token": "Marcador de dirección", "phone_token": "Marcador telefónico",
    "email_token": "Marcador de correo",
}
FINDING_LABEL = {
    "business_hours_updated": "Horario actualizado (ficticio)",
    "alternate_channel_declared": "Canal alternativo (ficticio)",
    "contact_data_confirmed": "Dato confirmado (ficticio)",
    "internal_note_added": "Nota interna (ficticia)",
}

cases, events = load_dataset(DATA)
validation = validate_dataset(DATA)
case_map = {c["case_id"]: c for c in cases}
cycle_meta = [json.loads(x) for x in (DATA / "cycles.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
last_cycle = max(cycle_meta, key=lambda x: x["simulation_time"])


def date_of(event):
    return date.fromisoformat(event["occurred_at"][:10])


def belongs(event, period):
    return period["start"] <= date_of(event) <= period["end"] and event["event_type"] != "case_seeded_simulated"


def money(value):
    value = float(value or 0)
    rendered = f"{abs(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if value < 0 else "") + "$ " + rendered


def num(value):
    return f"{int(value):,}".replace(",", ".")


def pct(value):
    return "N/D" if value is None else f"{float(value):.2f}".replace(".", ",") + "%"


def escape(value):
    return html.escape(str(value if value is not None else ""), quote=True)


PSTATS = []
for p in PERIODS:
    report = build_report(cases, events, p["start"], p["end"])
    rows = [e for e in events if belongs(e, p)]
    PSTATS.append({
        **report, **p, "days": (p["end"] - p["start"]).days + 1,
        "event_count": len(rows), "unique_cases": len({e["case_id"] for e in rows}),
        "period_events": rows, "type_counts": collections.Counter(e["event_type"] for e in rows),
    })
all_changes = [
    e for e in events
    if e["event_type"] != "case_seeded_simulated" and START.isoformat() <= e["occurred_at"][:10] <= END.isoformat()
]
whole = build_report(cases, events, START, END)
assert validation == {"cases": 1000, "events": 3231, "min_dpd": 1, "max_dpd": 560}
assert len(all_changes) == 2231
assert round(whole["payments_usd"], 2) == 2505955.85
assert len({e["case_id"] for e in all_changes}) == 905

daily = []
for i in range((END - START).days + 1):
    d = START + timedelta(days=i)
    rows = [e for e in all_changes if date_of(e) == d]
    counts = collections.Counter(e["event_type"] for e in rows)
    daily.append({
        "date": d, "events": len(rows), "unique_cases": len({e["case_id"] for e in rows}),
        "payments": round(sum(float(e.get("amount_usd", 0)) for e in rows if e["event_type"] == "payment_recorded_simulated"), 2),
        "payment_events": counts["payment_recorded_simulated"],
        "commitments": counts["commitment_created_simulated"],
        "status": counts["commitment_status_changed_simulated"],
        "channels": counts["channel_attempt_simulated"], "updates": counts["contact_data_update_simulated"],
        "findings": counts["research_finding_simulated"], "disputes": counts["dispute_opened_simulated"],
        "reviews": counts["internal_review_simulated"],
        "cycle": ", ".join(sorted({e["cycle_id"] for e in rows})) or "Sin actividad",
    })

type_rows = []
for event_type, (label, description) in TYPE_INFO.items():
    selected = [e for e in all_changes if e["event_type"] == event_type]
    by_period = [sum(1 for e in p["period_events"] if e["event_type"] == event_type) for p in PSTATS]
    payment_amount = round(sum(float(e.get("amount_usd", 0)) for e in selected), 2) if event_type == "payment_recorded_simulated" else None
    type_rows.append({"type": event_type, "label": label, "description": description,
                      "p1": by_period[0], "p2": by_period[1], "p3": by_period[2],
                      "total": sum(by_period), "payment_amount": payment_amount})

p1, p2, p3 = PSTATS
event_delta = (p2["event_count"] / p1["event_count"] - 1) * 100
case_delta = (p2["unique_cases"] / p1["unique_cases"] - 1) * 100
payment_delta = (p2["payments_usd"] / p1["payments_usd"] - 1) * 100
rate_delta_pp = p2["recovery_rate_pct"] - p1["recovery_rate_pct"]
status_p2 = collections.Counter(e.get("commitment_status", "") for e in p2["period_events"] if e["event_type"] == "commitment_status_changed_simulated")
nov10_status = sum(1 for e in all_changes if e["occurred_at"][:10] == "2026-11-10" and e["event_type"] == "commitment_status_changed_simulated")

detail = []
for e in sorted(all_changes, key=lambda x: (x["occurred_at"], x["event_id"])):
    d = date_of(e)
    period_id = next((p["id"] for p in PERIODS if p["start"] <= d <= p["end"]), "—")
    typ = e["event_type"]
    row = {
        "Fecha y hora (Bogotá)": datetime.fromisoformat(e["occurred_at"]).strftime("%Y-%m-%d %H:%M:%S"),
        "Periodo": period_id, "Ciclo": e.get("cycle_id", ""), "ID de evento": e.get("event_id", ""),
        "ID de cuenta ficticia": e.get("case_id", ""), "Tipo de cambio": TYPE_LABEL.get(typ, typ),
        "Pago USD": float(e.get("amount_usd", 0)) if typ == "payment_recorded_simulated" else None,
        "Capital USD": float(e.get("allocation_principal_usd", 0)) if typ == "payment_recorded_simulated" else None,
        "Interés USD": float(e.get("allocation_interest_usd", 0)) if typ == "payment_recorded_simulated" else None,
        "Otros USD": float(e.get("allocation_other_usd", 0)) if typ == "payment_recorded_simulated" else None,
        "Compromiso USD": float(e["amount_due_usd"]) if "amount_due_usd" in e else None,
        "Estado (simulado)": STATE_LABEL.get(e.get("commitment_status", ""), ""),
        "Vencimiento (simulado)": e.get("due_at", ""),
        "Campo actualizado": FIELD_LABEL.get(e.get("field_name", ""), ""),
        "Canal (no enviado)": CHANNEL_LABEL.get(e.get("channel", ""), ""),
        "Resultado simulado": OUTCOME_LABEL.get(e.get("outcome", ""), ""),
        "Detalle de categoría": FINDING_LABEL.get(e.get("finding_type", ""), e.get("review_outcome", "")),
        "Entrega": "No enviado" if e.get("delivery_status") == "not_sent" else "",
        "Verificación": e.get("verification_status", ""),
        "Referencia de origen": e.get("source_ref", ""),
    }
    detail.append(row)

OUT.mkdir(parents=True, exist_ok=True)
html_path = OUT / "Reporte_cambios_base_cobranza.html"
xlsx_path = OUT / "Reporte_cambios_base_cobranza.xlsx"
period_html = []
for ps in PSTATS:
    states = ps["commitments_due_by_status"]
    period_html.append(
        f"<tr><td><b>{escape(ps['id'])}</b><br>{ps['start']:%d/%m}–{ps['end']:%d/%m}<br><span class='muted'>{ps['days']} día(s)</span></td>"
        f"<td>{num(ps['event_count'])}<br><span class='muted'>{num(ps['unique_cases'])} cuentas con ≥1 evento</span></td>"
        f"<td>{money(ps['payments_usd'])}<br><span class='muted'>{num(ps['payment_event_count'])} registros · recuperación {pct(ps['recovery_rate_pct'])}</span></td>"
        f"<td>{money(ps['opening_balance_usd'])}<br><span class='muted'>Saldo final: {money(ps['closing_balance_usd'])}</span></td>"
        f"<td>{num(ps['commitments_created_count'])} creados<br><span class='muted'>{num(ps['commitments_due_count'])} vencidos · cumplimiento {pct(ps['commitment_kept_rate_pct'])}</span></td>"
        f"<td>{num(ps['channel_attempts_simulated'])}<br><span class='muted'>no enviados</span></td>"
        f"<td>{num(ps['contact_updates_count'])}</td><td>{escape(ps['note'])}</td></tr>"
    )
type_html = []
for row in type_rows:
    amount = money(row["payment_amount"]) if row["payment_amount"] is not None else "—"
    type_html.append(
        f"<tr><td>{escape(row['label'])}</td><td>{num(row['p1'])}</td><td>{num(row['p2'])}</td>"
        f"<td>{num(row['p3'])}</td><td><b>{num(row['total'])}</b></td><td>{amount}</td><td>{escape(row['description'])}</td></tr>"
    )
max_events = max(x["events"] for x in daily) or 1
daily_html = []
for d in daily:
    width = max(2, 100 * d["events"] / max_events)
    daily_html.append(
        f"<tr><td>{d['date']:%d %b}</td><td>{num(d['events'])}<div class='bar'><i style='width:{width:.1f}%'></i></div></td>"
        f"<td>{num(d['unique_cases'])}</td><td>{money(d['payments'])}</td><td>{num(d['payment_events'])}</td>"
        f"<td>{num(d['status'])}</td><td>{num(d['channels'])}</td><td>{num(d['updates'])}</td><td>{escape(d['cycle'])}</td></tr>"
    )

html_doc = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reporte de cambios de base — cobranzas | Simulación</title>
<style>
:root{{--navy:#10263f;--blue:#176b87;--teal:#21a38a;--ink:#203041;--muted:#5a6d7d;--paper:#f4f7fa;--line:#d9e2ea;--warn:#fff2da;--warnborder:#d49a25;--white:#fff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 Segoe UI,Arial,sans-serif}}
header{{background:linear-gradient(120deg,var(--navy),#174967);color:#fff;padding:34px max(24px,calc((100vw - 1220px)/2))}}
header h1{{margin:.2em 0;font-size:clamp(25px,3vw,38px);line-height:1.15}}header p{{margin:.45em 0;max-width:930px;color:#e3edf4}}
.badge{{display:inline-block;border:1px solid #e4bc61;color:#fff2cd;background:#604914;padding:5px 10px;border-radius:99px;font-size:12px;font-weight:800;letter-spacing:.04em}}
main{{max-width:1220px;margin:auto;padding:24px}}h2{{color:var(--navy);margin:0 0 14px;font-size:23px}}h3{{color:var(--navy);font-size:17px;margin:10px 0}}
.section{{background:var(--white);border:1px solid var(--line);border-radius:14px;padding:22px;margin:18px 0;box-shadow:0 4px 16px #19385209}}
.alert{{border-left:6px solid var(--warnborder);background:var(--warn);padding:15px 18px;border-radius:8px;margin:18px 0;font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:13px;margin:18px 0}}
.card{{background:white;border:1px solid var(--line);border-radius:12px;padding:16px 18px}}.card .label{{color:var(--muted);font-size:13px}}.card strong{{display:block;color:var(--navy);font-size:23px;margin-top:5px}}.card small{{color:var(--muted)}}
.tablewrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:760px;font-size:13px}}th{{background:#eaf1f6;color:var(--navy);text-align:left;font-weight:700}}td,th{{padding:10px 11px;border-bottom:1px solid var(--line);vertical-align:top}}tr:last-child td{{border-bottom:0}}.muted{{color:var(--muted);font-size:12px}}
.bar{{height:5px;background:#edf2f6;border-radius:8px;margin-top:5px;max-width:100px}}.bar i{{display:block;height:100%;background:var(--teal);border-radius:8px}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}ul,ol{{padding-left:22px}}li{{margin:6px 0}}.note{{border:1px dashed #a7bac9;padding:13px;border-radius:9px;background:#f7fafc}}
footer{{max-width:1220px;margin:auto;padding:4px 24px 32px;color:var(--muted);font-size:12px}}a.button{{display:inline-block;background:var(--blue);color:white;text-decoration:none;border-radius:8px;padding:10px 14px;font-weight:700}}
@media print{{body{{background:white}}header{{padding:22px}}main{{padding:12px}}.section{{break-inside:avoid;box-shadow:none}}a.button{{display:none}}}}
</style></head>
<body><header><span class="badge">{CAUTION}</span>
<h1>Reporte explicativo de cambios en la base de cobranza</h1>
<p>Lectura por períodos del libro de eventos sintético v3. No describe una cartera operativa ni cambios de una base real.</p>
<p><b>Corte:</b> 03–11 nov 2026 · America/Bogota · <b>Generado:</b> 10 nov 2026 · {escape(last_cycle['generated_at'])}</p>
<p><a class="button" href="{escape(xlsx_path.name)}">Descargar libro Excel</a></p></header>
<main>
<div class="alert"><b>Uso permitido: demostración y capacitación.</b> El origen contiene datos completamente sintéticos. Los registros de canales están marcados “no enviado”. No usar para asignar trabajo, contactar deudores, evaluar gestores ni tomar decisiones sobre cartera real.</div>
<div class="grid">
<div class="card"><span class="label">Universo de prueba</span><strong>{num(len(cases))}</strong><small>cuentas ficticias</small></div>
<div class="card"><span class="label">Cambios registrados</span><strong>{num(len(all_changes))}</strong><small>eventos no iniciales; 905 cuentas ficticias afectadas</small></div>
<div class="card"><span class="label">Pagos simulados</span><strong>{money(whole['payments_usd'])}</strong><small>425 registros · 03–11 nov</small></div>
<div class="card"><span class="label">Saldo modelo</span><strong>{money(whole['closing_balance_usd'])}</strong><small>apertura {money(whole['opening_balance_usd'])}</small></div>
</div>
<section class="section"><h2>Lectura ejecutiva</h2><ul>
<li>El log contiene <b>{num(validation['events'])} eventos</b>; los {num(validation['cases'])} eventos de carga inicial se excluyen. Se analizan {num(len(all_changes))} eventos de actividad simulada entre el 03 y el 11 nov.</li>
<li>En ventanas comparables de 4 días, los eventos suben de {num(p1['event_count'])} a {num(p2['event_count'])} ({event_delta:+.1f}%), mientras las cuentas con evento pasan de {num(p1['unique_cases'])} a {num(p2['unique_cases'])} ({case_delta:+.1f}%). El incremento se concentra en transiciones de compromisos.</li>
<li>Los pagos simulados pasan de {money(p1['payments_usd'])} a {money(p2['payments_usd'])} ({payment_delta:+.1f}%); la tasa del modelo cambia de {pct(p1['recovery_rate_pct'])} a {pct(p2['recovery_rate_pct'])} ({rate_delta_pp:+.2f} puntos porcentuales). No es recuperación real.</li>
<li>P2 contiene {num(p2['type_counts']['commitment_status_changed_simulated'])} eventos de cambio de estado, incluidos {num(status_p2.get('pending', 0))} que registran “pendiente”. El 10 nov concentra {num(nov10_status)} transiciones; alerta sobre la lógica/carga del fixture, no sobre desempeño.</li>
<li>Se registran 54 aperturas ficticias de disputa y 2 revisiones internas requeridas. El archivo no comunica ni determina resultados de casos.</li>
</ul></section>
<section class="section"><h2>Comparación por períodos</h2><p class="muted">P1 y P2 son ventanas consecutivas de 4 días. P3 es una extensión de reloj simulado de un día fechado 11 nov y generado el 10 nov; se informa aparte, no es actividad real.</p>
<div class="tablewrap"><table><thead><tr><th>Período</th><th>Cambios</th><th>Pagos simulados</th><th>Saldo modelo</th><th>Compromisos</th><th>Intentos de canal</th><th>Actualizaciones</th><th>Lectura</th></tr></thead><tbody>{''.join(period_html)}</tbody></table></div>
<div class="note"><b>Interpretación:</b> “Cambios” cuenta eventos, no filas únicas. “Vencidos” se clasifica por fecha de vencimiento y estado más reciente al cierre; puede diferir de las transiciones registradas durante el período.</div></section>
<section class="section"><h2>Cambios por tipo</h2><div class="tablewrap"><table><thead><tr><th>Tipo</th><th>P1</th><th>P2</th><th>P3*</th><th>Total</th><th>Pagos USD</th><th>Qué significa</th></tr></thead><tbody>{''.join(type_html)}</tbody></table></div><p class="muted">*P3 es un día futuro simulado. Solo “Pago registrado” suma a pagos; el monto de compromisos no es dinero recuperado.</p></section>
<section class="section"><h2>Actividad diaria</h2><p class="muted">Fecha de ocurrencia del reloj simulado. El 02 nov, que solo contiene carga inicial, se excluye.</p><div class="tablewrap"><table><thead><tr><th>Fecha</th><th>Eventos</th><th>Cuentas</th><th>Pagos</th><th>Registros pago</th><th>Estados</th><th>Canales</th><th>Datos</th><th>Ciclo</th></tr></thead><tbody>{''.join(daily_html)}</tbody></table></div></section>
<section class="section"><h2>Uso en el equipo de gestión</h2><div class="cols"><div><h3>Rutina sugerida para capacitación</h3><ol><li>Validar período, duración y ciclo cargado antes de comparar.</li><li>Conciliar saldo inicial − pagos del período = saldo final del modelo.</li><li>Separar compromisos creados, vencidos y transiciones de estado.</li><li>Distinguir actividad de canal de contacto efectivo: aquí no se envía nada.</li><li>Derivar disputas y marcas de revisión a validación humana en el ejercicio.</li></ol></div><div><h3>Controles antes de cualquier operación real</h3><ul><li>Fuente y snapshot/CDC aprobados, con trazabilidad y acceso mínimo.</li><li>Responsables y controles de privacidad, retención, permisos y correcciones.</li><li>Conciliar eventos con filas únicas; reportar estados finales aparte de transiciones.</li><li>Validar definiciones con negocio antes de usar métricas para metas o decisiones.</li></ul></div></div></section>
<section class="section"><h2>Fuente, definiciones y límites</h2><ul><li><b>Fuente:</b> data/reporting_synthetic_v3/cases.csv (1.000 cuentas), events.jsonl (3.231 eventos) y cycles.jsonl (2 ciclos). No es base productiva.</li><li><b>Evento de cambio:</b> todo evento distinto de case_seeded_simulated, agrupado por occurred_at, hora simulada y no fecha de generación.</li><li><b>Saldo:</b> saldo de apertura menos pagos; este cálculo no incorpora intereses nuevos ni otros cargos.</li><li><b>Tasa:</b> pagos/saldo inicial del período. Cumplimiento: cumplidos ÷ (cumplidos + incumplidos); pendientes y cancelados quedan fuera.</li><li><b>Privacidad:</b> contacto representado mediante tokens no enrutables; el Excel omite valores anterior/nuevo.</li><li><b>Base comparativa:</b> no se proporcionaron snapshots productivos ni CDC; no es posible afirmar diferencias de una base real.</li></ul></section>
</main><footer>Fixture v3 · Semilla 20261110 · {escape(LABEL)} · Reporte local generado el 10 nov 2026 (America/Bogota).</footer></body></html>"""
html_path.write_text(html_doc, encoding="utf-8")

# Workbook helpers
wb = Workbook()
navy, white, pale, teal = "10263F", "FFFFFF", "EAF1F6", "21A38A"
border = Side(style="thin", color="D9E2EA")
header_fill = PatternFill("solid", fgColor=navy)
caution_fill = PatternFill("solid", fgColor="FFF2DA")


def init_sheet(sheet, title, subtitle):
    sheet.sheet_view.showGridLines = False
    sheet.merge_cells("A1:E1")
    c = sheet["A1"]; c.value = title; c.fill = header_fill
    c.font = Font(name="Aptos Display", size=16, bold=True, color=white)
    c.alignment = Alignment(vertical="center")
    sheet.row_dimensions[1].height = 31
    sheet.merge_cells("A2:E2")
    c = sheet["A2"]; c.value = subtitle; c.fill = caution_fill
    c.font = Font(name="Aptos", size=10, bold=True, color="704D00")
    c.alignment = Alignment(wrap_text=True, vertical="center")
    sheet.row_dimensions[2].height = 31
    sheet.freeze_panes = "A5"
    sheet.sheet_view.zoomScale = 85


def add_header(sheet, row, headers):
    for col, label in enumerate(headers, 1):
        c = sheet.cell(row, col, label); c.fill = header_fill
        c.font = Font(name="Aptos", bold=True, color=white)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = Border(bottom=border)
    sheet.row_dimensions[row].height = 34


def style_rows(sheet, first, last, ncols):
    for row in sheet.iter_rows(min_row=first, max_row=last, min_col=1, max_col=ncols):
        for c in row:
            c.font = Font(name="Aptos", size=10, color="203041")
            c.alignment = Alignment(vertical="top", wrap_text=c.column in (1, 2, ncols))
            c.border = Border(bottom=border)


def make_table(sheet, name, first_row, last_row, last_col):
    table = Table(displayName=name, ref=f"A{first_row}:{get_column_letter(last_col)}{last_row}")
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False,
        showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    sheet.add_table(table)


# Summary
ws = wb.active; ws.title = "00_Resumen"
init_sheet(ws, "Reporte de cambios de base de cobranza", f"{CAUTION} | Libro de entrenamiento sintético v3 · Generado 10-Nov-2026 · America/Bogota")
summary = [
    ("Origen", "data/reporting_synthetic_v3/cases.csv + events.jsonl + cycles.jsonl"),
    ("Ventana analizada", "03-Nov-2026 a 11-Nov-2026 (reloj simulado)"),
    ("Generado / ciclo más reciente", last_cycle["generated_at"]),
    ("Ciclos registrados", len(cycle_meta)),
    ("Universo sintético", validation["cases"]),
    ("Eventos totales", validation["events"]),
    ("Eventos de carga inicial excluidos", 1000),
    ("Eventos de cambio analizados", len(all_changes)),
    ("Cuentas ficticias con ≥1 evento", 905),
    ("Saldo inicial del período", whole["opening_balance_usd"]),
    ("Pagos simulados registrados", whole["payments_usd"]),
    ("Saldo final del modelo", whole["closing_balance_usd"]),
    ("Tasa acumulada del período", whole["recovery_rate_pct"]),
    ("Cambios estado de compromisos", sum(e["event_type"] == "commitment_status_changed_simulated" for e in all_changes)),
    ("Intentos de canal", sum(e["event_type"] == "channel_attempt_simulated" for e in all_changes)),
    ("Actualizaciones de datos", sum(e["event_type"] == "contact_data_update_simulated" for e in all_changes)),
    ("Disputas abiertas (simuladas)", sum(e["event_type"] == "dispute_opened_simulated" for e in all_changes)),
]
for r, (label, value) in enumerate(summary, 4):
    ws.cell(r, 1, label); ws.cell(r, 2, value)
    ws.cell(r, 1).font = Font(name="Aptos", bold=True, color=navy)
    ws.cell(r, 1).fill = PatternFill("solid", fgColor=pale)
    for c in (ws.cell(r, 1), ws.cell(r, 2)):
        c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = Border(bottom=border)
for r in (13, 14, 15):
    ws.cell(r, 2).number_format = "$#,##0.00"
ws["B16"].number_format = '0.00"%"'
ws.merge_cells("A22:E22"); ws["A22"] = "Lectura para gestión (solo entrenamiento)"
ws["A22"].fill = header_fill; ws["A22"].font = Font(bold=True, color=white)
notes = [
    "Ledger sintético; no es snapshot productivo ni extracción de cartera real.",
    "“Cambios” cuenta eventos distintos de case_seeded_simulated. Una cuenta puede generar varios eventos.",
    "La carga inicial de 1.000 cuentas del 02-Nov se excluye de los cambios del período.",
    "P3 (11-Nov) es fecha futura del reloj simulado, generada el 10-Nov; no es hecho futuro ni predicción.",
    "Intentos de canal ficticios no enviados. Se omiten los tokens de contacto anterior/nuevo.",
    "No usar cifras o IDs para asignar tareas, contactar, medir desempeño ni decidir sobre cartera real.",
]
for r, note in enumerate(notes, 23):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
    ws.cell(r, 1, "• " + note).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 30
ws.column_dimensions["A"].width = 39; ws.column_dimensions["B"].width = 68

# Periods
sp = wb.create_sheet("01_Periodos")
init_sheet(sp, "Comparación por períodos", "P1/P2 son ventanas consecutivas de 4 días; P3 es extensión de 1 día del reloj simulado.")
period_headers = ["Periodo", "Inicio", "Fin", "Días", "Eventos de cambio", "Cuentas únicas afectadas",
    "Saldo inicial USD", "Pagos simulados USD", "Saldo final modelo USD", "Reducción modelo USD",
    "Recuperación %", "Registros pago", "Cuentas con pago", "Pagos totales (cuentas)",
    "Pagos parciales (cuentas)", "Compromisos creados", "Compromisos vencidos", "Cumplidos al cierre",
    "Incumplidos al cierre", "Pendientes al cierre", "Cancelados al cierre", "Cumplimiento %",
    "Intentos canal (no enviados)", "Actualizaciones contacto", "Hallazgos", "Disputas abiertas",
    "Revisiones internas", "Nota de lectura"]
add_header(sp, 4, period_headers)
for r, ps in enumerate(PSTATS, 5):
    states = ps["commitments_due_by_status"]
    vals = [ps["id"], ps["start"].isoformat(), ps["end"].isoformat(), ps["days"], ps["event_count"],
        ps["unique_cases"], ps["opening_balance_usd"], ps["payments_usd"], ps["closing_balance_usd"],
        ps["balance_reduction_usd"], ps["recovery_rate_pct"], ps["payment_event_count"],
        ps["payment_case_count"], ps["full_payment_case_count"], ps["partial_payment_case_count"],
        ps["commitments_created_count"], ps["commitments_due_count"], states.get("kept", 0),
        states.get("missed", 0), states.get("pending", 0), states.get("cancelled", 0),
        ps["commitment_kept_rate_pct"], ps["channel_attempts_simulated"], ps["contact_updates_count"],
        ps["research_findings_count"], ps["type_counts"].get("dispute_opened_simulated", 0),
        ps["type_counts"].get("internal_review_simulated", 0), ps["note"]]
    for c, value in enumerate(vals, 1): sp.cell(r, c, value)
style_rows(sp, 5, 7, len(period_headers)); make_table(sp, "TablaPeriodos", 4, 7, len(period_headers))
for r in range(5, 8):
    for c in (7, 8, 9, 10): sp.cell(r, c).number_format = "$#,##0.00"
    for c in (11, 22): sp.cell(r, c).number_format = '0.00"%"'
period_widths = [15,13,13,8,15,18,18,18,19,19,13,14,15,19,20,15,21,17,18,17,17,14,21,20,14,14,17,60]
for i, width in enumerate(period_widths, 1): sp.column_dimensions[get_column_letter(i)].width = width
chart = BarChart(); chart.type = "col"; chart.style = 10; chart.title = "Pagos simulados por período"
chart.y_axis.title = "USD"; chart.x_axis.title = "Período"; chart.height = 7; chart.width = 14
chart.add_data(Reference(sp, min_col=8, min_row=4, max_row=7), titles_from_data=True)
chart.set_categories(Reference(sp, min_col=1, min_row=5, max_row=7)); chart.legend = None
sp.add_chart(chart, "A10")
sp.conditional_formatting.add("K5:K7", ColorScaleRule(start_type="min", start_color="F4CCCC",
    mid_type="percentile", mid_value=50, mid_color="FFF2CC", end_type="max", end_color="D9EAD3"))

# Daily
sd = wb.create_sheet("02_Diario")
init_sheet(sd, "Actividad diaria del ledger", "Conteo por occurred_at local simulado; carga inicial del 02-Nov excluida.")
daily_headers = ["Fecha simulada", "Ciclo", "Eventos", "Cuentas únicas", "Pagos simulados USD", "Registros de pago",
    "Compromisos creados", "Cambios estado compromiso", "Intentos canal no enviados", "Actualizaciones contacto",
    "Hallazgos", "Disputas abiertas", "Revisiones internas"]
add_header(sd, 4, daily_headers)
for r, d in enumerate(daily, 5):
    vals = [d["date"].isoformat(), d["cycle"], d["events"], d["unique_cases"], d["payments"], d["payment_events"],
        d["commitments"], d["status"], d["channels"], d["updates"], d["findings"], d["disputes"], d["reviews"]]
    for c, value in enumerate(vals, 1): sd.cell(r, c, value)
style_rows(sd, 5, 4 + len(daily), len(daily_headers)); make_table(sd, "TablaDiaria", 4, 4 + len(daily), len(daily_headers))
for r in range(5, 5 + len(daily)): sd.cell(r, 5).number_format = "$#,##0.00"
for col, width in {"A":16,"B":34,"C":13,"D":15,"E":20,"F":17,"G":20,"H":25,"I":24,"J":23,"K":13,"L":16,"M":20}.items():
    sd.column_dimensions[col].width = width
chart = BarChart(); chart.type = "col"; chart.style = 11; chart.title = "Eventos de cambio por día (simulado)"
chart.y_axis.title = "N.º de eventos"; chart.x_axis.title = "Fecha"; chart.height = 7; chart.width = 18
chart.add_data(Reference(sd, min_col=3, min_row=4, max_row=4 + len(daily)), titles_from_data=True)
chart.set_categories(Reference(sd, min_col=1, min_row=5, max_row=4 + len(daily))); chart.legend = None
sd.add_chart(chart, "A16")

# Change types
sc = wb.create_sheet("03_TiposCambio")
init_sheet(sc, "Cambios clasificados por tipo", "Conteos de eventos, no filas únicas. Solo pagos suman a recuperación; compromisos no equivalen a dinero recibido.")
headers = ["Tipo de evento técnico","Tipo de cambio","P1 · 03–06 nov","P2 · 07–10 nov","P3 · 11 nov*","Total","Pagos USD","Descripción / cautela"]
add_header(sc, 4, headers)
for r, row in enumerate(type_rows, 5):
    vals = [row["type"], row["label"], row["p1"], row["p2"], row["p3"], row["total"], row["payment_amount"], row["description"]]
    for c, value in enumerate(vals, 1): sc.cell(r, c, value)
style_rows(sc, 5, 4 + len(type_rows), len(headers)); make_table(sc, "TablaTiposCambio", 4, 4 + len(type_rows), len(headers))
for r in range(5, 5 + len(type_rows)): sc.cell(r, 7).number_format = "$#,##0.00"
for col, width in {"A":39,"B":38,"C":17,"D":17,"E":17,"F":13,"G":18,"H":90}.items(): sc.column_dimensions[col].width = width
sc.merge_cells("A15:H15"); sc["A15"] = "* P3 es reloj futuro simulado del 11-Nov, generado el 10-Nov; no es operación real."
sc["A15"].fill = caution_fill; sc["A15"].alignment = Alignment(wrap_text=True, vertical="center"); sc.row_dimensions[15].height = 32

# Detailed append-only ledger without contact token values
se = wb.create_sheet("04_Detalle")
init_sheet(se, "Detalle de eventos de cambio", "2.231 eventos no iniciales · fixture sintético · omite tokens de contacto anterior/nuevo · canales no enviados.")
detail_headers = list(detail[0].keys())
add_header(se, 4, detail_headers)
for r, row in enumerate(detail, 5):
    for c, name in enumerate(detail_headers, 1):
        value = row[name]
        if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
            value = "'" + value
        se.cell(r, c, value)
style_rows(se, 5, 4 + len(detail), len(detail_headers)); make_table(se, "TablaDetalleEventos", 4, 4 + len(detail), len(detail_headers))
for r in range(5, 5 + len(detail)):
    for c in range(7, 12): se.cell(r, c).number_format = "$#,##0.00"
for col, width in {"A":22,"B":12,"C":32,"D":36,"E":28,"F":39,"G":16,"H":16,"I":16,"J":16,"K":18,"L":25,"M":27,"N":27,"O":27,"P":32,"Q":45,"R":18,"S":24,"T":45}.items():
    se.column_dimensions[col].width = width

# Glossary and usage
sg = wb.create_sheet("05_Glosario")
init_sheet(sg, "Glosario y guía de uso", "Solo aplica al fixture sintético. No sustituye política de cobranza ni habilita operación real.")
glossary = [
("Evento de cambio","Evento distinto de case_seeded_simulated; cada registro se cuenta por separado.","Monitorear variaciones del ledger.","No equivale a una fila única; una cuenta puede tener varios eventos."),
("Cuenta con evento","case_id sintético distinto que aparece en el período.","Diferenciar volumen del universo de cuentas afectadas.","No identifica persona real ni asigna trabajo."),
("Pago simulado","Evento de pago con monto y distribución a componentes.","Conciliar saldo inicial − pagos = saldo final del modelo.","No es recaudación bancaria ni tiene conexión a CRM/ERP."),
("Tasa del período","Pagos del período ÷ saldo inicial del período.","Practicar un denominador consistente.","No es resultado real ni referencia de desempeño."),
("Compromiso creado","Evento de creación de promesa/compromiso simulado.","Separar promesas nuevas de pagos recibidos.","No sumar al monto recuperado."),
("Compromiso vencido","Due date dentro de la ventana y estado más reciente al cierre.","Separar vencidos y resultado por estado.","Difiere del conteo de transiciones ocurridas en la ventana."),
("Cumplimiento simulado","Cumplidos ÷ (cumplidos + incumplidos) de compromisos vencidos.","Ejercicio de cálculo; pendientes/cancelados excluidos.","No inferir promesas o capacidad de pago reales."),
("Intento de canal","Evento channel_attempt_simulated con delivery_status=not_sent.","Practicar diferencia actividad/contacto efectivo.","No se envió llamada, SMS, correo ni WhatsApp."),
("Actualización de contacto","Cambio de marcador sintético address_token/phone_token/email_token.","Discutir controles de calidad/verificación.","Tokens no enrutables; valores omitidos del detalle."),
("P3 · 11 nov","Ciclo futuro del reloj simulado añadido el 10-Nov.","Demostrar actualización incremental.","No es hecho futuro ni pronóstico."),
("Uso operacional","No aplica a este fixture.","Para operación se requiere fuente aprobada, privacidad, permisos, retención, pruebas y responsables.","No usar para asignación, contacto, desempeño o decisiones reales."),
]
gloss_headers = ["Concepto", "Definición en este reporte", "Uso didáctico sugerido", "Límite / cautela"]
add_header(sg, 4, gloss_headers)
for r, row in enumerate(glossary, 5):
    for c, value in enumerate(row, 1): sg.cell(r, c, value)
style_rows(sg, 5, 4 + len(glossary), len(gloss_headers)); make_table(sg, "TablaGlosario", 4, 4 + len(glossary), len(gloss_headers))
for col, width in {"A":29,"B":68,"C":58,"D":76}.items(): sg.column_dimensions[col].width = width

for sheet in wb.worksheets:
    sheet.sheet_properties.pageSetUpPr.fitToPage = True
    sheet.page_setup.fitToWidth = 1; sheet.page_setup.fitToHeight = 0
    sheet.page_margins.left = 0.25; sheet.page_margins.right = 0.25
    sheet.page_margins.top = 0.5; sheet.page_margins.bottom = 0.5
    sheet.sheet_properties.tabColor = teal if sheet.title != "04_Detalle" else "176B87"
wb.properties.title = "Reporte de cambios de base de cobranza — simulación"
wb.properties.subject = "ReporterÍa sintética por períodos para capacitación"
wb.properties.creator = "OpenAI Codex"
wb.properties.description = f"{CAUTION}. Fuente local reporting_synthetic_v3; generado 2026-11-10 America/Bogota."
wb.save(xlsx_path)

# Reopen outputs and assert key figures/layout.
check = load_workbook(xlsx_path, read_only=False, data_only=False)
assert check.sheetnames == ["00_Resumen", "01_Periodos", "02_Diario", "03_TiposCambio", "04_Detalle", "05_Glosario"]
assert check["04_Detalle"].max_row == 4 + len(all_changes)
assert check["01_Periodos"]["H5"].value == PSTATS[0]["payments_usd"]
assert html_path.stat().st_size > 10000 and xlsx_path.stat().st_size > 20000
assert CAUTION in html_path.read_text(encoding="utf-8")
print(json.dumps({
    "html": str(html_path.resolve()), "xlsx": str(xlsx_path.resolve()),
    "html_bytes": html_path.stat().st_size, "xlsx_bytes": xlsx_path.stat().st_size,
    "changes": len(all_changes), "unique_cases": len({e["case_id"] for e in all_changes}),
    "periods": [{"id": p["id"], "events": p["event_count"], "payments_usd": p["payments_usd"],
                 "recovery_pct": p["recovery_rate_pct"]} for p in PSTATS],
    "sheets": check.sheetnames,
}, ensure_ascii=False, indent=2))

