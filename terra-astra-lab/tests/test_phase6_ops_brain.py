import json
import tempfile
import unittest
from pathlib import Path

from taec_lab.realtrace import (
    INTERP_WEIGHTS,
    OpsPhaseBrain,
    forecast_next_ops,
    learn_ops_brain,
    load_ledger,
    run_realtrace_eval,
)

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


def _fixture_ledger(tmp: Path) -> Path:
    ledger = tmp / "worklog.jsonl"
    with open(ledger, "w", encoding="utf-8") as handle:
        for index, row in enumerate(FIXTURE_ROWS):
            handle.write(json.dumps(dict(row, seq=index + 1)) + "\n")
    return ledger


class OpsPhaseBrainTests(unittest.TestCase):
    def test_distributions_sum_to_one_at_all_levels(self):
        brain = OpsPhaseBrain()
        brain.observe_rows(FIXTURE_ROWS)
        for phase in ("implement", "verify", "persist", "unseen-phase"):
            for current in ("create", "observe", "resolve", "unknown-type"):
                for dist in (
                    brain.predict(phase, current)[0],
                    brain.predict_markov(current)[0],
                ):
                    self.assertAlmostEqual(sum(dist.values()), 1.0, places=9)

    def test_pair_level_dominates_with_support(self):
        brain = OpsPhaseBrain()
        rows = [
            {"verb": "edit", "phase": "implement"},
            {"verb": "test_pass", "phase": "verify"},
        ] * 8
        brain.observe_rows(rows)
        dist, _ = brain.predict("implement", "create")
        self.assertGreater(dist["resolve"], 0.5)  # create -> test_pass(resolve)

    def test_persistence_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops-brain.json"
            brain = OpsPhaseBrain()
            brain.observe_rows(FIXTURE_ROWS)
            brain.save(path)
            reloaded = OpsPhaseBrain.load(path)
            self.assertEqual(reloaded.n_transitions, brain.n_transitions)
            self.assertEqual(reloaded.to_dict(), brain.to_dict())

    def test_empty_brain_is_cold_start(self):
        self.assertTrue(OpsPhaseBrain().is_empty())
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _fixture_ledger(Path(tmp))
            result = forecast_next_ops(
                ledger_path=ledger, brain_path=Path(tmp) / "missing.json"
            )
            self.assertEqual(result["status"], "COLD_START")


class ForecastAndEvalTests(unittest.TestCase):
    def test_learn_then_forecast_uses_persistent_brain(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ledger = _fixture_ledger(tmp)
            brain_path = tmp / "ops-brain.json"
            summary = learn_ops_brain(ledger_path=ledger, brain_path=brain_path)
            self.assertEqual(summary["status"], "OPS_LEARN")
            self.assertEqual(summary["n_transitions"], len(FIXTURE_ROWS) - 1)
            result = forecast_next_ops(ledger_path=ledger, brain_path=brain_path)
            self.assertEqual(result["status"], "OPS_FORECAST")
            self.assertEqual(result["base"]["phase"], "persist")
            self.assertEqual(result["base"]["current_type"], "resolve")
            total = sum(item["probability"] for item in result["candidates"])
            self.assertAlmostEqual(total, 1.0, places=6)
            # The CLI forecast must agree with a direct brain computation.
            expected, _ = OpsPhaseBrain.load(brain_path).predict("persist", "resolve")
            got = {item["op"]: item["probability"] for item in result["candidates"]}
            for name, probability in expected.items():
                self.assertAlmostEqual(got[name], round(probability, 6), places=6)

    def test_eval_v2_wellformed_and_smalln_inconclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _fixture_ledger(Path(tmp))
            report = run_realtrace_eval(ledger_path=ledger, report_dir=None)
            self.assertEqual(report["version"], 2)
            self.assertEqual(report["verdict"], "INCONCLUSIVE")  # 8 test < 12
            for arm in ("markov", "phase_markov"):
                self.assertIn(arm, report["arms"])
            for gate in ("R5_phase_acc_gt_const", "R6_phase_ll_lt_const",
                         "R7_phase_acc_ge_markov", "R8_phase_ll_le_markov"):
                self.assertIn(gate, report["gates"])
            self.assertEqual(report["primary_gates"], ["R1", "R5", "R6"])

    def test_interp_weights_are_frozen(self):
        self.assertEqual(INTERP_WEIGHTS["markov"], (0.0, 0.7, 0.3))
        self.assertEqual(INTERP_WEIGHTS["phase_markov"], (0.5, 0.3, 0.2))


if __name__ == "__main__":
    unittest.main()
