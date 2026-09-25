import json
import tempfile
import unittest
from pathlib import Path

from taec_lab.realtrace import (
    compile_ops,
    load_ledger,
    op_type,
    run_realtrace_eval,
    to_observations,
)

# Fixed real-schema fixture (deterministic rows; NOT the live ledger).
FIXTURE_ROWS = [
    {"verb": "read", "area": "brain", "phase": "boot", "outcome": "ok"},
    {"verb": "edit", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "write", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "edit", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "write", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "edit", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "test_pass", "area": "tests", "phase": "verify", "outcome": "ok"},
    {"verb": "edit", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "write", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "test_fail", "area": "tests", "phase": "verify", "outcome": "fail"},
    {"verb": "fix", "area": "tests", "phase": "implement", "outcome": "ok"},
    {"verb": "test_pass", "area": "tests", "phase": "verify", "outcome": "ok"},
    {"verb": "edit", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "write", "area": "code", "phase": "implement", "outcome": "ok"},
    {"verb": "test_pass", "area": "tests", "phase": "verify", "outcome": "ok"},
    {"verb": "eval", "area": "reports", "phase": "seal", "outcome": "ok"},
    {"verb": "document", "area": "docs", "phase": "document", "outcome": "ok"},
    {"verb": "lesson", "area": "brain", "phase": "persist", "outcome": "ok"},
    {"verb": "commit", "area": "git", "phase": "persist", "outcome": "ok"},
    {"verb": "push", "area": "git", "phase": "persist", "outcome": "ok"},
]


class OntologyMappingTests(unittest.TestCase):
    def test_verbs_map_to_seven_types(self):
        self.assertEqual(op_type({"verb": "edit"}), "create")
        self.assertEqual(op_type({"verb": "test_fail"}), "fail")
        self.assertEqual(op_type({"verb": "fix"}), "recover")
        self.assertEqual(op_type({"verb": "eval"}), "escalate")
        self.assertEqual(op_type({"verb": "commit"}), "resolve")
        self.assertEqual(op_type({"verb": "read"}), "observe")
        self.assertEqual(op_type({"verb": "mystery"}), "unknown")

    def test_one_observation_per_real_event(self):
        rows = [dict(row, seq=i + 1) for i, row in enumerate(FIXTURE_ROWS)]
        observations = to_observations(rows)
        self.assertEqual(len(observations), len(rows))
        events = compile_ops(rows, trace_id="fx")
        self.assertEqual(len(events), len(rows))
        self.assertEqual(
            [event.event_type for event in events],
            [op_type(row) for row in rows],
        )
        self.assertEqual(observations[0].features["regime"], "ops")


class PilotEvalTests(unittest.TestCase):
    def test_eval_on_fixture_is_wellformed_and_smalln_inconclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "worklog.jsonl"
            with open(ledger, "w", encoding="utf-8") as handle:
                for index, row in enumerate(FIXTURE_ROWS):
                    handle.write(json.dumps(dict(row, seq=index + 1)) + "\n")
            rows = load_ledger(ledger)
            self.assertEqual(len(rows), len(FIXTURE_ROWS))
            report = run_realtrace_eval(ledger_path=ledger, report_dir=None)
            self.assertEqual(report["status"], "PILOT_REAL_TRACE")
            # 20 rows -> 12 train / 8 test < 12 -> gate R1 must fail open.
            self.assertFalse(report["gates"]["R1_min_test"])
            self.assertEqual(report["verdict"], "INCONCLUSIVE")
            for arm in ("uniform", "freq_prior", "synth_zero_shot", "real_learned"):
                self.assertIn(arm, report["arms"])
                self.assertIn("accuracy", report["arms"][arm])

    def test_train_writes_only_to_temp_brain(self):
        from taec_lab.realtrace import _train_real_brain
        from taec_lab.mind import TAECMind

        with tempfile.TemporaryDirectory() as tmp:
            brain = Path(tmp) / "brain-real"
            rows = [dict(row, seq=i + 1) for i, row in enumerate(FIXTURE_ROWS)]
            mind = _train_real_brain(rows, brain)
            self.assertEqual(mind.status, "WARM")
            self.assertFalse(mind.weights.is_empty())
            # The main synthetic brain must remain untouched by this call.
            main = TAECMind()
            self.assertEqual(main.weights.meta.get("train_traces", 0), 80)


if __name__ == "__main__":
    unittest.main()
