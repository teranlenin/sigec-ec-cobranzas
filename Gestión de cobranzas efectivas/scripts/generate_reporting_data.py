#!/usr/bin/env python3
"""CLI offline para inicializar y avanzar ciclos de reportería sintética."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from reporting.metrics import build_report  # noqa: E402
from reporting.simulation import (  # noqa: E402
    DEFAULT_DATA_DIR, DEFAULT_SEED, LABEL, _jsonl_read, append_cycle,
    initialize_dataset, load_dataset, validate_dataset,
)

TZ = ZoneInfo("America/Bogota")


def _write_report(data_dir: Path, report: dict, start: date, end: date) -> tuple[Path, Path]:
    report_dir = data_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(TZ)
    stem = f"weekly-{start.isoformat()}-to-{end.isoformat()}-{generated.strftime('%H%M%S%f')}"
    json_path = report_dir / f"{stem}.json"
    md_path = report_dir / f"{stem}.md"
    if json_path.exists() or md_path.exists():
        raise FileExistsError("No se sobrescriben reportes existentes; vuelve a ejecutar para un nombre nuevo.")
    report = {
        **report,
        "generated_at": generated.isoformat(),
        "dataset_version": "reporting-synthetic-v3",
        "cycle_count": len(_jsonl_read(data_dir / "cycles.jsonl")),
        "simulation_label": LABEL,
    }
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Reporte semanal de cobranza — SIMULACIÓN",
        "",
        f"**Rótulo:** {LABEL}",
        f"**Período:** {start.isoformat()} a {end.isoformat()} (America/Bogota)",
        f"**Generado:** {generated.isoformat()}",
        "",
        "## Resumen financiero ficticio",
        f"- Saldo inicial del período: USD {report['opening_balance_usd']:,.2f}",
        f"- Saldo final del período: USD {report['closing_balance_usd']:,.2f}",
        f"- Pagos simulados del período: USD {report['payments_usd']:,.2f}",
        f"- Tasa de recuperación (pagos / saldo inicial): {report['recovery_rate_pct'] if report['recovery_rate_pct'] is not None else 'N/D'}%",
        "",
        "## Gestión simulada",
        f"- Casos: {report['case_count']}",
        f"- Pagos parciales: {report['partial_payment_case_count']} casos; pagos totales: {report['full_payment_case_count']} casos",
        f"- Compromisos vencidos: {report['commitments_due_count']}; cumplidos: {report['commitments_due_by_status'].get('kept', 0)}; incumplidos: {report['commitments_due_by_status'].get('missed', 0)}; pendientes: {report['commitments_due_by_status'].get('pending', 0)}",
        f"- Actualizaciones de contacto ficticias: {report['contact_updates_count']}",
        f"- Intentos de canal ficticios (no enviados): {report['channel_attempts_simulated']}",
        f"- Hallazgos sintéticos: {report['research_findings_count']}",
        "",
        "## Límites",
        *[f"- {item}" for item in report["limitations"]],
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def _weekly(data_dir: Path, start: date, end: date, manager_id: str | None) -> tuple[Path, Path]:
    cases, events = load_dataset(data_dir)
    report = build_report(cases, events, start, end, manager_id=manager_id)
    return _write_report(data_dir, report, start, end)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generación de reportería local y sintética; sin conectores.")
    parser.add_argument("--mode", required=True,
                        choices=["initialize", "cycle", "loop", "weekly", "validate"],
                        help="initialize: crea baseline nuevo; cycle: agrega un lote; loop: avanza cada 5 min; weekly: exporta reporte; validate: comprueba invariantes")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--cases", type=int, default=1000)
    parser.add_argument("--event-count", type=int, default=30)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(TZ).date())
    parser.add_argument("--cycle-id", help="ID estable opcional; repetirlo hace que el ciclo sea idempotente.")
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--from-date", type=date.fromisoformat)
    parser.add_argument("--to-date", type=date.fromisoformat)
    parser.add_argument("--manager-id", help="Filtro sintético opcional, p. ej. GESTOR-SIM-01.")
    args = parser.parse_args()
    if args.interval_seconds < 1:
        parser.error("--interval-seconds debe ser positivo")

    if args.mode == "initialize":
        print(json.dumps(initialize_dataset(args.cases, args.seed, args.as_of, args.output_dir), ensure_ascii=False, indent=2))
    elif args.mode == "cycle":
        print(json.dumps(append_cycle(args.output_dir, args.cycle_id, args.event_count, args.seed), ensure_ascii=False, indent=2))
    elif args.mode == "loop":
        print(f"Modo cíclico local de simulación cada {args.interval_seconds}s. Ctrl+C para detener; no se envían comunicaciones.")
        try:
            while True:
                print(json.dumps(append_cycle(args.output_dir, None, args.event_count, args.seed), ensure_ascii=False))
                time.sleep(args.interval_seconds)
        except KeyboardInterrupt:
            print("Bucle de simulación detenido por el usuario.")
    elif args.mode == "weekly":
        end = args.to_date or datetime.now(TZ).date()
        start = args.from_date or (end - timedelta(days=6))
        if start > end:
            parser.error("--from-date no puede ser posterior a --to-date")
        paths = _weekly(args.output_dir, start, end, args.manager_id)
        print("Reporte sintético generado:")
        for path in paths:
            print(path)
    else:
        print(json.dumps(validate_dataset(args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
