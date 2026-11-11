"""Generación local, reproducible y aislada de datos sintéticos de reportería."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "reporting_synthetic_v3"
TIMEZONE = ZoneInfo("America/Bogota")
LABEL = "SIMULACIÓN — NO USAR EN PRODUCCIÓN"
SCHEMA_VERSION = "reporting-synthetic-v3"
DEFAULT_SEED = 20261110
CASE_FIELDS = [
    "case_id", "obligation_id", "manager_id", "currency", "opening_principal_usd",
    "opening_interest_usd", "opening_other_usd", "opening_balance_usd",
    "days_past_due_at_start", "aging_bucket_version", "simulation_as_of",
    "dispute_status", "address_token", "phone_token", "email_token", "synthetic",
    "simulation", "simulation_label",
]


def _now_local() -> datetime:
    return datetime.now(TIMEZONE).replace(second=0, microsecond=0)


def _safe_cycle_slug(cycle_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", cycle_id)[:40]


def _jsonl_read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as source:
        for line_no, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON inválido en {path.name}:{line_no}: {exc}") from exc
            rows.append(item)
    return rows


def _append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as target:
        for row in rows:
            target.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _event(event_id: str, case: dict[str, Any], cycle_id: str, occurred_at: datetime,
           event_type: str, source_ref: str, **fields: Any) -> dict[str, Any]:
    event = {
        "event_id": event_id,
        "case_id": case["case_id"],
        "obligation_id": case["obligation_id"],
        "cycle_id": cycle_id,
        "occurred_at": occurred_at.isoformat(),
        "event_type": event_type,
        "source_ref": source_ref,
        "verification_status": "synthetic_fixture",
        "actor_simulated": fields.pop("actor_simulated", "SIMULADOR"),
        "schema_version": SCHEMA_VERSION,
        "synthetic": True,
        "simulation": True,
        "simulation_label": LABEL,
    }
    event.update(fields)
    return event


def _payment_event(event_id: str, case: dict[str, Any], cycle_id: str,
                   occurred_at: datetime, amount_cents: int, source_ref: str,
                   commitment_id: str | None = None,
                   remaining_components: dict[str, int] | None = None) -> dict[str, Any]:
    components = remaining_components or {
        "principal": round(float(case["opening_principal_usd"]) * 100),
        "interest": round(float(case["opening_interest_usd"]) * 100),
        "other": round(float(case["opening_other_usd"]) * 100),
    }
    amount_cents = max(0, min(amount_cents, sum(components.values())))
    principal = min(amount_cents, components["principal"])
    interest = min(amount_cents - principal, components["interest"])
    other = amount_cents - principal - interest
    return _event(
        event_id, case, cycle_id, occurred_at, "payment_recorded_simulated", source_ref,
        amount_usd=round(amount_cents / 100, 2),
        allocation_principal_usd=round(principal / 100, 2),
        allocation_interest_usd=round(interest / 100, 2),
        allocation_other_usd=round(other / 100, 2),
        commitment_id=commitment_id,
    )


def _remaining_components(cases: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    result = {
        case["case_id"]: {
            "principal": round(float(case["opening_principal_usd"]) * 100),
            "interest": round(float(case["opening_interest_usd"]) * 100),
            "other": round(float(case["opening_other_usd"]) * 100),
        }
        for case in cases
    }
    for event in sorted(events, key=lambda row: (row["occurred_at"], row["event_id"])):
        if event.get("event_type") != "payment_recorded_simulated" or event.get("case_id") not in result:
            continue
        row = result[event["case_id"]]
        if all(event.get(key) is not None for key in (
            "allocation_principal_usd", "allocation_interest_usd", "allocation_other_usd"
        )):
            allocations = {
                "principal": round(float(event["allocation_principal_usd"]) * 100),
                "interest": round(float(event["allocation_interest_usd"]) * 100),
                "other": round(float(event["allocation_other_usd"]) * 100),
            }
        else:
            amount = round(float(event.get("amount_usd", 0)) * 100)
            principal = min(amount, row["principal"])
            interest = min(amount - principal, row["interest"])
            allocations = {"principal": principal, "interest": interest,
                           "other": amount - principal - interest}
        for key, amount in allocations.items():
            row[key] = max(0, row[key] - amount)
    return result


def _apply_payment_to_components(event: dict[str, Any], remaining: dict[str, int]) -> None:
    for key, field in (("principal", "allocation_principal_usd"),
                       ("interest", "allocation_interest_usd"),
                       ("other", "allocation_other_usd")):
        remaining[key] = max(0, remaining[key] - round(float(event[field]) * 100))


def _make_cases(count: int, seed: int, as_of: date) -> list[dict[str, Any]]:
    if count < 560:
        raise ValueError("Se requieren al menos 560 casos para cubrir cada día del rango 1–560.")
    rng = random.Random(seed)
    rows = []
    for index in range(1, count + 1):
        principal_cents = rng.randint(50_000, 2_500_000)
        interest_cents = rng.randint(0, min(300_000, principal_cents // 2))
        other_cents = rng.randint(0, 25_000)
        days_past_due = ((index - 1) % 560) + 1
        rows.append({
            "case_id": f"CASE-SYN-RPT-{index:05d}",
            "obligation_id": f"OBL-SYN-RPT-{index:05d}",
            "manager_id": f"GESTOR-SIM-{((index - 1) % 20) + 1:02d}",
            "currency": "USD",
            "opening_principal_usd": round(principal_cents / 100, 2),
            "opening_interest_usd": round(interest_cents / 100, 2),
            "opening_other_usd": round(other_cents / 100, 2),
            "opening_balance_usd": round((principal_cents + interest_cents + other_cents) / 100, 2),
            "days_past_due_at_start": days_past_due,
            "aging_bucket_version": "dpd-v1",
            "simulation_as_of": (as_of - timedelta(days=7)).isoformat(),
            "dispute_status": "open_simulated" if rng.random() < 0.05 else "none_reported_simulated",
            "address_token": f"ADDR-SYN-{index:05d}-v1",
            "phone_token": f"TEL-SYN-{index:05d}-v1",
            "email_token": f"EMAIL-SYN-{index:05d}-v1@example.invalid",
            "synthetic": True,
            "simulation": True,
            "simulation_label": LABEL,
        })
    return rows


def _baseline_events(cases: list[dict[str, Any]], seed: int,
                     as_of: date) -> list[dict[str, Any]]:
    rng = random.Random(seed ^ 0x51A7)
    start = datetime.combine(as_of - timedelta(days=7), time(0, 0), tzinfo=TIMEZONE)
    cutoff = datetime.combine(as_of, time(12, 0), tzinfo=TIMEZONE)
    events: list[dict[str, Any]] = []
    sequence = 0

    def add(case: dict[str, Any], event_type: str, when: datetime,
            source: str, **fields: Any) -> dict[str, Any]:
        nonlocal sequence
        sequence += 1
        item = _event(f"EVT-SYN-RPT-BASE-{sequence:07d}", case, "BASELINE-WEEK-01",
                      when, event_type, source, **fields)
        events.append(item)
        return item

    for case in cases:
        component_state = {
            "principal": round(float(case["opening_principal_usd"]) * 100),
            "interest": round(float(case["opening_interest_usd"]) * 100),
            "other": round(float(case["opening_other_usd"]) * 100),
        }
        open_at = start - timedelta(minutes=rng.randint(1, 1440))
        add(case, "case_seeded_simulated", open_at, f"FIXTURE:{case['case_id']}")
        disputed = case["dispute_status"] == "open_simulated"
        dispute_at = start + timedelta(minutes=rng.randint(0, 180)) if disputed else None
        if dispute_at:
            add(case, "dispute_opened_simulated", dispute_at,
                f"FIXTURE:{case['case_id']}:DISPUTE", dispute_status="open")

        if not disputed and rng.random() < 0.67:
            when = start + timedelta(seconds=rng.randint(1, int((cutoff - start).total_seconds())))
            channel = rng.choice(["phone_call", "sms", "whatsapp_message", "email", "written_notice"])
            outcome = rng.choice(["draft_created_not_sent", "reply_simulated", "no_response_simulated"])
            add(case, "channel_attempt_simulated", when,
                f"FIXTURE:{case['case_id']}:CHANNEL", channel=channel,
                outcome=outcome, delivery_status="not_sent")

        if rng.random() < 0.13:
            when = start + timedelta(seconds=rng.randint(1, int((cutoff - start).total_seconds())))
            field = rng.choice(["address_token", "phone_token", "email_token"])
            versions = {"address_token": "ADDR", "phone_token": "TEL", "email_token": "EMAIL"}
            prefix = versions[field]
            suffix = "@example.invalid" if field == "email_token" else ""
            add(case, "contact_data_update_simulated", when,
                f"FIXTURE:{case['case_id']}:DATA-UPDATE", field_name=field,
                old_value_token=case[field], new_value_token=f"{prefix}-SYN-{case['case_id'][-5:]}-v2{suffix}",
                update_source="synthetic_investigation", verification_status="synthetic_fixture")

        if rng.random() < 0.12:
            when = start + timedelta(seconds=rng.randint(1, int((cutoff - start).total_seconds())))
            add(case, "research_finding_simulated", when,
                f"FIXTURE:{case['case_id']}:RESEARCH", finding_type=rng.choice([
                    "business_hours_updated", "alternate_channel_declared", "contact_data_confirmed",
                    "internal_note_added",
                ]), finding_summary="Hallazgo didáctico ficticio; requiere verificación humana.",
                verification_status="synthetic_fixture")

        balance_cents = round(float(case["opening_balance_usd"]) * 100)
        commitment_id = None
        commitment_amount_cents = 0
        if rng.random() < 0.36:
            commitment_id = f"COM-SYN-RPT-{case['case_id'][-5:]}"
            created_at = start + timedelta(seconds=rng.randint(1, int((cutoff - start).total_seconds())))
            due_at = created_at + timedelta(days=rng.randint(1, 9))
            commitment_amount_cents = min(balance_cents, rng.randint(5_000, max(5_000, balance_cents // 3)))
            add(case, "commitment_created_simulated", created_at,
                f"FIXTURE:{case['case_id']}:COMMITMENT", commitment_id=commitment_id,
                amount_due_usd=round(commitment_amount_cents / 100, 2),
                due_at=due_at.isoformat(), commitment_status="accepted")
            status_at = min(due_at, cutoff)
            if due_at > cutoff:
                status = "pending"
            else:
                status = rng.choices(["kept", "missed", "cancelled"], [0.58, 0.34, 0.08])[0]
            add(case, "commitment_status_changed_simulated", status_at,
                f"FIXTURE:{case['case_id']}:COMMITMENT-STATUS", commitment_id=commitment_id,
                amount_due_usd=round(commitment_amount_cents / 100, 2),
                due_at=due_at.isoformat(), commitment_status=status)
            if status == "kept":
                paid_at = min(due_at, cutoff)
                sequence += 1
                payment = _payment_event(
                    f"EVT-SYN-RPT-BASE-{sequence:07d}", case, "BASELINE-WEEK-01",
                    paid_at, commitment_amount_cents,
                    f"FIXTURE:{case['case_id']}:PAYMENT", commitment_id, component_state,
                )
                events.append(payment)
                _apply_payment_to_components(payment, component_state)
                balance_cents = sum(component_state.values())

        if balance_cents > 0 and rng.random() < 0.31:
            payment_cents = balance_cents if rng.random() < 0.08 else rng.randint(1, balance_cents)
            when = start + timedelta(seconds=rng.randint(1, int((cutoff - start).total_seconds())))
            if disputed and when >= dispute_at:
                when = max(start, dispute_at - timedelta(minutes=1))
            sequence += 1
            payment = _payment_event(
                f"EVT-SYN-RPT-BASE-{sequence:07d}", case, "BASELINE-WEEK-01", when,
                payment_cents, f"FIXTURE:{case['case_id']}:PAYMENT-INDEPENDENT",
                remaining_components=component_state,
            )
            events.append(payment)
            _apply_payment_to_components(payment, component_state)

    events.sort(key=lambda item: (item["occurred_at"], item["event_id"]))
    return events


def _write_cases(path: Path, cases: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=CASE_FIELDS)
        writer.writeheader()
        writer.writerows(cases)


def load_dataset(data_dir: Path | str = DEFAULT_DATA_DIR) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    data_dir = Path(data_dir)
    cases_path, events_path = data_dir / "cases.csv", data_dir / "events.jsonl"
    if not cases_path.exists() or not events_path.exists():
        raise FileNotFoundError(
            f"No existe la población sintética en {data_dir}. Inicialízala con scripts/generate_reporting_data.py --initialize."
        )
    with cases_path.open("r", encoding="utf-8-sig", newline="") as source:
        cases = list(csv.DictReader(source))
    for case in cases:
        for key in ("opening_principal_usd", "opening_interest_usd", "opening_other_usd", "opening_balance_usd"):
            case[key] = float(case[key])
        case["days_past_due_at_start"] = int(case["days_past_due_at_start"])
        case["synthetic"] = case["synthetic"].lower() == "true"
        case["simulation"] = case["simulation"].lower() == "true"
    return cases, _jsonl_read(events_path)


def initialize_dataset(count: int = 1000, seed: int = DEFAULT_SEED,
                        as_of: date | None = None,
                        data_dir: Path | str = DEFAULT_DATA_DIR) -> dict[str, Any]:
    data_dir = Path(data_dir)
    if any((data_dir / name).exists() for name in ("cases.csv", "events.jsonl", "cycles.jsonl")):
        raise FileExistsError(f"No se sobrescriben datos existentes: {data_dir}")
    as_of = as_of or _now_local().date()
    cases = _make_cases(count, seed, as_of)
    events = _baseline_events(cases, seed, as_of)
    data_dir.mkdir(parents=True, exist_ok=True)
    _write_cases(data_dir / "cases.csv", cases)
    _append_jsonl(data_dir / "events.jsonl", events)
    _append_jsonl(data_dir / "cycles.jsonl", [{
        "cycle_id": "BASELINE-WEEK-01",
        "generated_at": _now_local().isoformat(),
        "simulation_time": datetime.combine(as_of, time(12, 0), tzinfo=TIMEZONE).isoformat(),
        "event_count": len(events), "seed": seed, "synthetic": True,
        "simulation": True, "simulation_label": LABEL,
    }])
    validate_dataset(data_dir)
    return {"cases": len(cases), "events": len(events), "data_dir": str(data_dir), "seed": seed}


def _payment_total_by_case(events: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for event in events:
        if event.get("event_type") == "payment_recorded_simulated":
            try:
                cents = round(float(event["amount_usd"]) * 100)
            except (KeyError, TypeError, ValueError):
                continue
            totals[event["case_id"]] = totals.get(event["case_id"], 0) + cents
    return totals


def _next_simulation_time(data_dir: Path) -> datetime:
    cycles = _jsonl_read(data_dir / "cycles.jsonl")
    if not cycles:
        return _now_local()
    last = max(datetime.fromisoformat(row["simulation_time"]) for row in cycles)
    return last + timedelta(days=1)


def _current_commitments(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for event in sorted(events, key=lambda row: (row["occurred_at"], row["event_id"])):
        if event.get("event_type") in {"commitment_created_simulated", "commitment_status_changed_simulated"}:
            key = event.get("commitment_id")
            if key:
                result[key] = event
    return result


def append_cycle(data_dir: Path | str = DEFAULT_DATA_DIR, cycle_id: str | None = None,
                 event_count: int = 30, seed: int = DEFAULT_SEED,
                 now: datetime | None = None) -> dict[str, Any]:
    data_dir = Path(data_dir)
    cases, events = load_dataset(data_dir)
    cycle_id = cycle_id or _now_local().strftime("CYCLE-%Y%m%dT%H%M%z")
    cycles = _jsonl_read(data_dir / "cycles.jsonl")
    prior = next((row for row in cycles if row.get("cycle_id") == cycle_id), None)
    if prior:
        return {"cycle_id": cycle_id, "appended_events": 0, "duplicate": True,
                "simulation_time": prior["simulation_time"]}

    now = now or _now_local()
    sim_at = _next_simulation_time(data_dir)
    # Hacer la marca simulada monótona; la hora real solo se guarda como metadato.
    if now.tzinfo is None:
        now = now.replace(tzinfo=TIMEZONE)
    rng_seed = int(hashlib.sha256(f"{seed}:{cycle_id}".encode()).hexdigest()[:12], 16)
    rng = random.Random(rng_seed)
    by_id = {case["case_id"]: case for case in cases}
    payments = _payment_total_by_case(events)
    component_state = _remaining_components(cases, events)
    open_disputes = set()
    for event in sorted(events, key=lambda row: (row["occurred_at"], row["event_id"])):
        if event.get("event_type") == "dispute_opened_simulated":
            open_disputes.add(event["case_id"])
        elif event.get("event_type") == "dispute_resolved_simulated":
            open_disputes.discard(event["case_id"])

    new_events: list[dict[str, Any]] = []
    seq = 0
    slug = _safe_cycle_slug(cycle_id)

    def add(case: dict[str, Any], kind: str, **fields: Any) -> None:
        nonlocal seq
        seq += 1
        event_id = f"EVT-SYN-RPT-{slug}-{seq:03d}"
        new_events.append(_event(event_id, case, cycle_id, sim_at, kind,
                                 f"FIXTURE:{case['case_id']}:{cycle_id}", **fields))

    # Resolve compromises cujo vencimento chegou en el reloj de simulación.
    for commitment_id, commitment in _current_commitments(events).items():
        if commitment.get("commitment_status") != "pending":
            continue
        due_at = datetime.fromisoformat(commitment["due_at"])
        if due_at <= sim_at:
            case = by_id[commitment["case_id"]]
            status = rng.choices(["kept", "missed"], [0.68, 0.32])[0]
            add(case, "commitment_status_changed_simulated", commitment_id=commitment_id,
                amount_due_usd=float(commitment["amount_due_usd"]), due_at=commitment["due_at"],
                commitment_status=status)
            if status == "kept":
                remaining = component_state[case["case_id"]]
                balance_cents = sum(remaining.values())
                amount = min(round(float(commitment["amount_due_usd"]) * 100), max(0, balance_cents))
                if amount:
                    seq += 1
                    payment = _payment_event(
                        f"EVT-SYN-RPT-{slug}-{seq:03d}", case, cycle_id, sim_at,
                        amount, f"FIXTURE:{case['case_id']}:{cycle_id}:PAYMENT", commitment_id,
                        remaining,
                    )
                    new_events.append(payment)
                    _apply_payment_to_components(payment, remaining)
                    payments[case["case_id"]] = payments.get(case["case_id"], 0) + amount

    selected_count = min(max(0, event_count), len(cases))
    selected = rng.sample(cases, selected_count)
    for case in selected:
        roll = rng.random()
        if roll < 0.27:
            if case["case_id"] in open_disputes:
                add(case, "internal_review_simulated", review_outcome="human_review_required")
                continue
            channel = rng.choice(["phone_call", "sms", "whatsapp_message", "email", "written_notice"])
            outcome = rng.choice(["draft_created_not_sent", "reply_simulated", "no_response_simulated"])
            add(case, "channel_attempt_simulated", channel=channel, outcome=outcome,
                delivery_status="not_sent")
        elif roll < 0.48:
            remaining = round(float(case["opening_balance_usd"]) * 100) - payments.get(case["case_id"], 0)
            if remaining > 0:
                amount = rng.randint(1, remaining)
                seq += 1
                payment = _payment_event(
                    f"EVT-SYN-RPT-{slug}-{seq:03d}", case, cycle_id, sim_at,
                    amount, f"FIXTURE:{case['case_id']}:{cycle_id}:PAYMENT",
                    remaining_components=component_state[case["case_id"]],
                )
                new_events.append(payment)
                _apply_payment_to_components(payment, component_state[case["case_id"]])
                payments[case["case_id"]] = payments.get(case["case_id"], 0) + amount
        elif roll < 0.67:
            field = rng.choice(["address_token", "phone_token", "email_token"])
            prefix = {"address_token": "ADDR", "phone_token": "TEL", "email_token": "EMAIL"}[field]
            suffix = "@example.invalid" if field == "email_token" else ""
            add(case, "contact_data_update_simulated", field_name=field,
                old_value_token=case[field],
                new_value_token=f"{prefix}-SYN-{case['case_id'][-5:]}-{slug[-8:]}{suffix}",
                update_source="synthetic_investigation", verification_status="synthetic_fixture")
        elif roll < 0.82:
            commitment_id = f"COM-SYN-RPT-{slug}-{case['case_id'][-5:]}"
            due_at = sim_at + timedelta(days=rng.randint(1, 3))
            amount_cents = min(round(float(case["opening_balance_usd"]) * 100) - payments.get(case["case_id"], 0),
                               rng.randint(1, max(1, round(float(case["opening_balance_usd"]) * 35))))
            if amount_cents > 0:
                fields = {"commitment_id": commitment_id,
                          "amount_due_usd": round(amount_cents / 100, 2),
                          "due_at": due_at.isoformat(), "commitment_status": "accepted"}
                add(case, "commitment_created_simulated", **fields)
                fields["commitment_status"] = "pending"
                add(case, "commitment_status_changed_simulated", **fields)
        else:
            add(case, "research_finding_simulated", finding_type=rng.choice([
                    "business_hours_updated", "alternate_channel_declared", "contact_data_confirmed"
                ]), finding_summary="Hallazgo didáctico ficticio; requiere verificación humana.",
                verification_status="synthetic_fixture")

    existing_ids = {event.get("event_id") for event in events}
    new_events = [event for event in new_events if event["event_id"] not in existing_ids]
    _append_jsonl(data_dir / "events.jsonl", new_events)
    cycle_record = {
        "cycle_id": cycle_id, "generated_at": now.isoformat(),
        "simulation_time": sim_at.isoformat(), "event_count": len(new_events),
        "seed": seed, "synthetic": True, "simulation": True,
        "simulation_label": LABEL,
    }
    _append_jsonl(data_dir / "cycles.jsonl", [cycle_record])
    validate_dataset(data_dir)
    return {"cycle_id": cycle_id, "appended_events": len(new_events),
            "duplicate": False, "simulation_time": sim_at.isoformat()}


def validate_dataset(data_dir: Path | str = DEFAULT_DATA_DIR) -> dict[str, Any]:
    cases, events = load_dataset(data_dir)
    if not cases:
        raise ValueError("La población sintética está vacía.")
    case_ids = {case["case_id"] for case in cases}
    if len(case_ids) != len(cases):
        raise ValueError("case_id duplicado.")
    if any(case.get("synthetic") is not True or case.get("simulation") is not True for case in cases):
        raise ValueError("Cada caso debe estar marcado como sintético y de simulación.")
    days = [case["days_past_due_at_start"] for case in cases]
    if min(days) != 1 or max(days) != 560:
        raise ValueError(f"La cobertura debe ser exactamente 1–560 días; encontrada {min(days)}–{max(days)}.")
    event_ids = [event.get("event_id") for event in events]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError("event_id duplicado; falla de idempotencia.")
    for event in events:
        if event.get("case_id") not in case_ids:
            raise ValueError(f"Evento {event.get('event_id')} sin caso asociado.")
        if event.get("synthetic") is not True or event.get("simulation") is not True:
            raise ValueError(f"Evento {event.get('event_id')} no está marcado como sintético/simulado.")
        if event.get("event_type") == "channel_attempt_simulated" and event.get("delivery_status") != "not_sent":
            raise ValueError("Un intento de canal sintético no puede indicar entrega efectiva.")
        if event.get("event_type") == "payment_recorded_simulated":
            amount = round(float(event.get("amount_usd", 0)) * 100)
            if amount <= 0:
                raise ValueError(f"Pago no positivo en {event.get('event_id')}.")
    totals = _payment_total_by_case(events)
    by_case = {case["case_id"]: round(float(case["opening_balance_usd"]) * 100) for case in cases}
    if any(totals.get(case_id, 0) > balance for case_id, balance in by_case.items()):
        raise ValueError("Los pagos acumulados exceden el saldo de apertura.")
    component_totals: dict[str, dict[str, int]] = {}
    for case in cases:
        component_totals[case["case_id"]] = {"principal": 0, "interest": 0, "other": 0}
    for event in events:
        if event.get("event_type") != "payment_recorded_simulated":
            continue
        allocation = {
            "principal": round(float(event.get("allocation_principal_usd", 0)) * 100),
            "interest": round(float(event.get("allocation_interest_usd", 0)) * 100),
            "other": round(float(event.get("allocation_other_usd", 0)) * 100),
        }
        amount = round(float(event["amount_usd"]) * 100)
        if sum(allocation.values()) != amount or any(value < 0 for value in allocation.values()):
            raise ValueError(f"Asignación de pago no conciliada en {event.get('event_id')}.")
        for key, value in allocation.items():
            component_totals[event["case_id"]][key] += value
    opening_components = {
        case["case_id"]: {
            "principal": round(float(case["opening_principal_usd"]) * 100),
            "interest": round(float(case["opening_interest_usd"]) * 100),
            "other": round(float(case["opening_other_usd"]) * 100),
        }
        for case in cases
    }
    if any(component_totals[case_id][key] > opening_components[case_id][key]
           for case_id in case_ids for key in ("principal", "interest", "other")):
        raise ValueError("La asignación acumulada a componentes excede el saldo de apertura.")
    return {"cases": len(cases), "events": len(events), "min_dpd": min(days), "max_dpd": max(days)}
