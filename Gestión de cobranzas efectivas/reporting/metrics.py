"""Indicadores y agregaciones reproducibles para reportería sintética."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Bogota")


def aging_bucket(days_past_due: int) -> str:
    """Bucket analítico versionado; no representa categoría legal o contable."""
    days = int(days_past_due)
    if days < 1 or days > 560:
        return "FUERA_RANGO"
    ranges = [
        (1, 30, "DPD_001_030"), (31, 60, "DPD_031_060"),
        (61, 90, "DPD_061_090"), (91, 120, "DPD_091_120"),
        (121, 180, "DPD_121_180"), (181, 360, "DPD_181_360"),
        (361, 560, "DPD_361_560"),
    ]
    return next(label for low, high, label in ranges if low <= days <= high)


def _as_datetime(value: date | datetime, end: bool = False) -> datetime:
    if isinstance(value, datetime):
        result = value
        if result.tzinfo is None:
            result = result.replace(tzinfo=TZ)
        return result
    return datetime.combine(value + (timedelta(days=1) if end else timedelta()),
                            time.min, tzinfo=TZ)


def _dt(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    return result if result.tzinfo else result.replace(tzinfo=TZ)


def _money(cents: int) -> float:
    return round(cents / 100, 2)


def _pct(numerator: int | float, denominator: int | float) -> float | None:
    return round((numerator / denominator) * 100, 2) if denominator else None


def build_report(cases: list[dict[str, Any]], events: list[dict[str, Any]],
                 period_start: date | datetime, period_end: date | datetime,
                 manager_id: str | None = None) -> dict[str, Any]:
    """Calcula KPIs a partir del libro de eventos, con ventana [inicio, fin]."""
    start_dt = _as_datetime(period_start)
    end_exclusive = _as_datetime(period_end, end=True)
    if start_dt >= end_exclusive:
        raise ValueError("El inicio del período debe preceder o coincidir con el fin.")

    filtered_cases = [case for case in cases if not manager_id or case["manager_id"] == manager_id]
    case_map = {case["case_id"]: case for case in filtered_cases}
    relevant_events = [event for event in events if event.get("case_id") in case_map]
    relevant_events.sort(key=lambda event: (_dt(event["occurred_at"]), event["event_id"]))
    window_events = [event for event in relevant_events if start_dt <= _dt(event["occurred_at"]) < end_exclusive]
    end_events = [event for event in relevant_events if _dt(event["occurred_at"]) < end_exclusive]
    pre_start_payments = [event for event in relevant_events
                          if event.get("event_type") == "payment_recorded_simulated"
                          and _dt(event["occurred_at"]) < start_dt]

    opening_by_case = {
        case_id: max(0, round(float(case["opening_balance_usd"]) * 100)
                     - sum(round(float(event.get("amount_usd", 0)) * 100)
                           for event in pre_start_payments if event["case_id"] == case_id))
        for case_id, case in case_map.items()
    }
    closing_by_case = dict(opening_by_case)
    for event in window_events:
        if event.get("event_type") == "payment_recorded_simulated":
            case_id = event["case_id"]
            closing_by_case[case_id] = max(
                0, closing_by_case[case_id] - round(float(event["amount_usd"]) * 100)
            )
    opening_cents = sum(opening_by_case.values())
    closing_cents = sum(closing_by_case.values())

    payment_events = [event for event in window_events
                      if event.get("event_type") == "payment_recorded_simulated"]
    payment_cents = sum(round(float(event["amount_usd"]) * 100) for event in payment_events)
    balance_before = dict(opening_by_case)
    for event in payment_events:
        case_id = event["case_id"]
        amount_cents = round(float(event["amount_usd"]) * 100)
        prior_balance = balance_before.get(case_id, 0)
        balance_before[case_id] = max(0, prior_balance - amount_cents)
    paid_cases = {event["case_id"] for event in payment_events}
    full_cases = {case_id for case_id in paid_cases if balance_before.get(case_id, 0) == 0}
    partial_cases = paid_cases - full_cases

    created = [event for event in window_events if event.get("event_type") == "commitment_created_simulated"]
    all_commitment_events = [event for event in end_events if event.get("event_type") in {
        "commitment_created_simulated", "commitment_status_changed_simulated"
    } and event.get("commitment_id")]
    latest_commitment: dict[str, dict[str, Any]] = {}
    for event in all_commitment_events:
        latest_commitment[event["commitment_id"]] = event
    due_commitments: dict[str, dict[str, Any]] = {}
    for commitment_id, latest in latest_commitment.items():
        try:
            due_dt = _dt(latest["due_at"])
        except (KeyError, TypeError, ValueError):
            continue
        if start_dt <= due_dt < end_exclusive:
            due_commitments[commitment_id] = latest
    commitment_states = Counter(event.get("commitment_status", "unknown")
                                for event in due_commitments.values())
    resolved_count = commitment_states["kept"] + commitment_states["missed"]
    kept_rate = _pct(commitment_states["kept"], resolved_count)

    channel_counts = Counter(event.get("channel", "not_specified") for event in window_events
                             if event.get("event_type") == "channel_attempt_simulated")
    channel_outcomes = Counter(event.get("outcome", "not_specified") for event in window_events
                               if event.get("event_type") == "channel_attempt_simulated")
    updates = [event for event in window_events
               if event.get("event_type") == "contact_data_update_simulated"]
    update_by_field = Counter(event.get("field_name", "not_specified") for event in updates)
    update_by_verification = Counter(event.get("verification_status", "unknown") for event in updates)
    findings = [event for event in window_events if event.get("event_type") == "research_finding_simulated"]

    day_delta_start = (start_dt.date() - date.fromisoformat(filtered_cases[0]["simulation_as_of"])).days if filtered_cases else 0
    day_delta_end = ((end_exclusive - timedelta(seconds=1)).date()
                     - date.fromisoformat(filtered_cases[0]["simulation_as_of"])).days if filtered_cases else 0
    roll_rates: Counter[str] = Counter()
    bucket_start_counts: Counter[str] = Counter()
    bucket_end_counts: Counter[str] = Counter()
    for case in filtered_cases:
        case_id = case["case_id"]
        start_dpd = min(560, max(1, int(case["days_past_due_at_start"]) + max(0, day_delta_start)))
        end_dpd = min(560, max(1, int(case["days_past_due_at_start"]) + max(0, day_delta_end)))
        if opening_by_case.get(case_id, 0) == 0:
            continue
        if closing_by_case.get(case_id, 0) == 0:
            end_bucket = "CURADO_SIMULADO"
        else:
            end_bucket = aging_bucket(end_dpd)
        start_bucket = aging_bucket(start_dpd)
        bucket_start_counts[start_bucket] += 1
        bucket_end_counts[end_bucket] += 1
        roll_rates[f"{start_bucket} → {end_bucket}"] += 1

    manager_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"cases": 0, "opening_cents": 0,
                                                                        "closing_cents": 0, "payments_cents": 0})
    payment_by_case = Counter()
    for event in payment_events:
        payment_by_case[event["case_id"]] += round(float(event["amount_usd"]) * 100)
    for case_id, case in case_map.items():
        row = manager_totals[case["manager_id"]]
        row["cases"] += 1
        row["opening_cents"] += opening_by_case.get(case_id, 0)
        row["closing_cents"] += closing_by_case.get(case_id, 0)
        row["payments_cents"] += payment_by_case.get(case_id, 0)
    managers = {
        manager: {
            "cases": values["cases"],
            "opening_balance_usd": _money(values["opening_cents"]),
            "closing_balance_usd": _money(values["closing_cents"]),
            "payments_usd": _money(values["payments_cents"]),
            "recovery_rate_pct": _pct(values["payments_cents"], values["opening_cents"]),
        }
        for manager, values in sorted(manager_totals.items())
    }

    return {
        "report_type": "synthetic_collection_period",
        "period_start": start_dt.isoformat(),
        "period_end_exclusive": end_exclusive.isoformat(),
        "timezone": "America/Bogota",
        "manager_filter": manager_id,
        "case_count": len(filtered_cases),
        "opening_balance_usd": _money(opening_cents),
        "closing_balance_usd": _money(closing_cents),
        "balance_reduction_usd": _money(opening_cents - closing_cents),
        "payments_usd": _money(payment_cents),
        "payment_event_count": len(payment_events),
        "payment_case_count": len({event["case_id"] for event in payment_events}),
        "full_payment_case_count": len(full_cases),
        "partial_payment_case_count": len(partial_cases),
        "recovery_rate_pct": _pct(payment_cents, opening_cents),
        "commitments_created_count": len(created),
        "commitments_due_count": len(due_commitments),
        "commitments_due_by_status": dict(sorted(commitment_states.items())),
        "commitments_resolved_count": resolved_count,
        "commitment_kept_rate_pct": kept_rate,
        "channel_attempts_simulated": sum(channel_counts.values()),
        "channel_counts_simulated": dict(sorted(channel_counts.items())),
        "channel_outcomes_simulated": dict(sorted(channel_outcomes.items())),
        "contact_updates_count": len(updates),
        "contact_updates_by_field": dict(sorted(update_by_field.items())),
        "contact_updates_by_verification": dict(sorted(update_by_verification.items())),
        "research_findings_count": len(findings),
        "aging_cases_at_start": dict(sorted(bucket_start_counts.items())),
        "aging_cases_at_end": dict(sorted(bucket_end_counts.items())),
        "aging_transition_counts": dict(sorted(roll_rates.items())),
        "manager_breakdown": managers,
        "synthetic": True,
        "simulation": True,
        "simulation_label": "SIMULACIÓN — NO USAR EN PRODUCCIÓN",
        "limitations": [
            "Todas las observaciones son generadas para entrenamiento y no representan resultados reales.",
            "Los canales son intentos ficticios no enviados; no equivalen a contacto ni entrega.",
            "La tasa de recuperación es pagos del período / saldo al inicio del período.",
            "El cumplimiento de compromisos usa compromisos vencidos con estado kept o missed; pendientes y cancelados se excluyen.",
            "El aging avanza según el reloj de simulación y se limita a 560 días.",
        ],
    }


def build_daily_series(cases: list[dict[str, Any]], events: list[dict[str, Any]],
                       period_start: date, period_end: date,
                       manager_id: str | None = None) -> list[dict[str, Any]]:
    """Serie diaria del período: pagos, saldo al cierre y actividad sintética."""
    selected_cases = [case for case in cases if not manager_id or case["manager_id"] == manager_id]
    selected_ids = {case["case_id"] for case in selected_cases}
    start_dt = _as_datetime(period_start)
    end_exclusive = _as_datetime(period_end, end=True)
    balance_cents = sum(round(float(case["opening_balance_usd"]) * 100) for case in selected_cases)
    daily: dict[date, dict[str, int]] = defaultdict(lambda: {
        "payments_cents": 0, "channel_attempts": 0, "contact_updates": 0,
        "commitments_created": 0, "research_findings": 0,
    })
    relevant = [event for event in events if event.get("case_id") in selected_ids]
    relevant.sort(key=lambda event: (_dt(event["occurred_at"]), event["event_id"]))
    for event in relevant:
        event_dt = _dt(event["occurred_at"])
        if event_dt < start_dt:
            if event.get("event_type") == "payment_recorded_simulated":
                balance_cents -= round(float(event["amount_usd"]) * 100)
        elif start_dt <= event_dt < end_exclusive:
            day = event_dt.date()
            kind = event.get("event_type")
            if kind == "payment_recorded_simulated":
                amount = round(float(event["amount_usd"]) * 100)
                daily[day]["payments_cents"] += amount
            elif kind == "channel_attempt_simulated":
                daily[day]["channel_attempts"] += 1
            elif kind == "contact_data_update_simulated":
                daily[day]["contact_updates"] += 1
            elif kind == "commitment_created_simulated":
                daily[day]["commitments_created"] += 1
            elif kind == "research_finding_simulated":
                daily[day]["research_findings"] += 1
    result = []
    end_balance = max(0, balance_cents)
    cursor = period_start
    while cursor <= period_end:
        row = daily[cursor]
        end_balance = max(0, end_balance - row["payments_cents"])
        result.append({
            "date": cursor.isoformat(),
            "payments_usd": _money(row["payments_cents"]),
            "closing_balance_usd": _money(end_balance),
            "channel_attempts_simulated": row["channel_attempts"],
            "contact_updates": row["contact_updates"],
            "commitments_created": row["commitments_created"],
            "research_findings": row["research_findings"],
        })
        cursor += timedelta(days=1)
    return result
