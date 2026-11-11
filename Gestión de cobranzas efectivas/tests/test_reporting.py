from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reporting.metrics import aging_bucket, build_daily_series, build_report  # noqa: E402
from reporting.simulation import (  # noqa: E402
    LABEL, append_cycle, initialize_dataset, load_dataset, validate_dataset,
)

try:
    from jsonschema import Draft202012Validator
except ImportError:  # El validador JSON Schema es opcional para el runtime de la app.
    Draft202012Validator = None


class ReportingSimulationTests(unittest.TestCase):
    def test_aging_bucket_boundaries(self):
        expected = {
            1: "DPD_001_030", 30: "DPD_001_030", 31: "DPD_031_060",
            60: "DPD_031_060", 61: "DPD_061_090", 90: "DPD_061_090",
            91: "DPD_091_120", 120: "DPD_091_120", 121: "DPD_121_180",
            180: "DPD_121_180", 181: "DPD_181_360", 360: "DPD_181_360",
            361: "DPD_361_560", 560: "DPD_361_560", 561: "FUERA_RANGO",
        }
        for days, bucket in expected.items():
            with self.subTest(days=days):
                self.assertEqual(aging_bucket(days), bucket)

    def test_dataset_schema_financial_reconciliation_and_tokenization(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "reporting_synthetic_v2"
            result = initialize_dataset(count=560, seed=11, as_of=date(2026, 11, 10), data_dir=data_dir)
            self.assertEqual(result["cases"], 560)
            check = validate_dataset(data_dir)
            self.assertEqual((check["min_dpd"], check["max_dpd"]), (1, 560))
            cases, events = load_dataset(data_dir)
            self.assertTrue(all(case["synthetic"] and case["simulation"] for case in cases))
            self.assertTrue(all(case["simulation_label"] == LABEL for case in cases))
            self.assertTrue(all(case["email_token"].endswith("@example.invalid") for case in cases))
            self.assertTrue(all(event["synthetic"] and event["simulation"] for event in events))
            self.assertTrue(all(event.get("delivery_status", "not_sent") == "not_sent" for event in events))
            for case in cases:
                self.assertEqual(
                    round(case["opening_principal_usd"] + case["opening_interest_usd"] + case["opening_other_usd"], 2),
                    round(case["opening_balance_usd"], 2),
                )

    def test_cycle_is_idempotent_and_advances_simulated_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "reporting_synthetic_v2"
            initialize_dataset(count=560, seed=41, as_of=date(2026, 11, 10), data_dir=data_dir)
            before_cases, before_events = load_dataset(data_dir)
            now = datetime(2026, 11, 10, 12, 5, tzinfo=ZoneInfo("America/Bogota"))
            first = append_cycle(data_dir, "TEST-CYCLE-001", 20, 41, now)
            after_cases, after_events = load_dataset(data_dir)
            second = append_cycle(data_dir, "TEST-CYCLE-001", 20, 41, now)
            _, after_duplicate_events = load_dataset(data_dir)
            self.assertGreater(first["appended_events"], 0)
            self.assertFalse(first["duplicate"])
            self.assertTrue(second["duplicate"])
            self.assertEqual(len(after_duplicate_events), len(after_events))
            self.assertEqual(len(before_cases), len(after_cases))
            self.assertEqual(validate_dataset(data_dir)["events"], len(after_events))

    def test_report_uses_explicit_denominators_and_synthetic_channels(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "reporting_synthetic_v2"
            initialize_dataset(count=560, seed=53, as_of=date(2026, 11, 10), data_dir=data_dir)
            cases, events = load_dataset(data_dir)
            report = build_report(cases, events, date(2026, 11, 3), date(2026, 11, 10))
            daily = build_daily_series(cases, events, date(2026, 11, 3), date(2026, 11, 10))
            self.assertTrue(report["synthetic"] and report["simulation"])
            self.assertEqual(report["case_count"], 560)
            self.assertAlmostEqual(report["balance_reduction_usd"], report["payments_usd"], places=2)
            self.assertEqual(daily[-1]["closing_balance_usd"], report["closing_balance_usd"])
            self.assertAlmostEqual(sum(row["payments_usd"] for row in daily), report["payments_usd"], places=2)
            if report["commitments_resolved_count"]:
                expected = round(
                    report["commitments_due_by_status"].get("kept", 0)
                    / report["commitments_resolved_count"] * 100, 2
                )
                self.assertEqual(report["commitment_kept_rate_pct"], expected)
            channel_events = [event for event in events if event["event_type"] == "channel_attempt_simulated"]
            self.assertTrue(all(event["delivery_status"] == "not_sent" for event in channel_events))
            self.assertIn("America/Bogota", report["timezone"])

    @unittest.skipIf(Draft202012Validator is None, "jsonschema no está instalado en este entorno de pruebas")
    def test_json_schemas_match_generated_fixtures(self):
        import csv
        import json

        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "reporting_synthetic_v3"
            initialize_dataset(count=560, seed=79, as_of=date(2026, 11, 10), data_dir=data_dir)
            case_schema = json.loads((ROOT / "rag" / "schemas" / "reporting_case.schema.json").read_text(encoding="utf-8"))
            event_schema = json.loads((ROOT / "rag" / "schemas" / "reporting_event.schema.json").read_text(encoding="utf-8"))
            case_validator = Draft202012Validator(case_schema)
            event_validator = Draft202012Validator(event_schema)
            with (data_dir / "cases.csv").open(encoding="utf-8-sig", newline="") as source:
                cases = list(csv.DictReader(source))
            for row in cases:
                item = {
                    key: (int(value) if key == "days_past_due_at_start"
                          else float(value) if key.endswith("_usd")
                          else value.lower() == "true" if key in ("synthetic", "simulation")
                          else value)
                    for key, value in row.items()
                }
                case_validator.validate(item)
            with (data_dir / "events.jsonl").open(encoding="utf-8") as source:
                events = [json.loads(line) for line in source if line.strip()]
            for event in events:
                event_validator.validate(event)


if __name__ == "__main__":
    unittest.main()
