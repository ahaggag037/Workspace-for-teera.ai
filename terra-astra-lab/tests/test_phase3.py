import tempfile
import unittest
from pathlib import Path

from taec_lab.credit import run_credit
from taec_lab.event_compiler import EventCompiler
from taec_lab.heldout import build_pack, evaluate_predictions, solve_pack
from taec_lab.learning import train_mind
from taec_lab.mind import TAECMind
from taec_lab.multiseed import run_multiseed
from taec_lab.scoring import boundary_f1
from taec_lab.synthetic import build_dataset


def _f1(traces) -> float:
    compiler = EventCompiler()
    truth, pred, offset = [], [], 0
    for trace in traces:
        graph = compiler.compile(trace.observations, trace_id=trace.trace_id)
        truth.extend(offset + e.source_indices[0] for e in trace.truth_events[1:])
        pred.extend(offset + e.source_indices[0] for e in graph.events[1:])
        offset += len(trace.observations)
    return boundary_f1(truth, pred)["f1"]


class Phase3Tests(unittest.TestCase):
    def test_hard_mode_is_strictly_harder(self):
        easy = build_dataset(6, seed_start=5001, difficulty="easy")
        hard = build_dataset(6, seed_start=5001, difficulty="hard")
        self.assertEqual(_f1(easy), 1.0)
        hard_f1 = _f1(hard)
        self.assertLess(hard_f1, 1.0)
        self.assertGreater(hard_f1, 0.3)

    def test_multiseed_aggregates(self):
        report = run_multiseed(seeds=[7, 8], train_count=4, test_count=3)
        self.assertEqual(report["config"]["k"], 2)
        self.assertIn("mean", report["aggregate"]["delta"]["accuracy"])
        self.assertIn(report["consistency"]["verdict"], ("PASS", "FAIL"))

    def test_heldout_seal_and_transfer(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            build_pack(tmp / "pack", n_traces=4, difficulty="easy")
            # Cold baseline solver.
            solve_pack(tmp / "pack", tmp / "cold.json", brain_dir=None)
            cold_verdict = evaluate_predictions(tmp / "pack", tmp / "cold.json")
            self.assertTrue(cold_verdict["seal_ok"])
            # Warm solver trained on disjoint dev seeds.
            brain = tmp / "brain"
            mind = TAECMind(brain_dir=brain)
            train_mind(mind, build_dataset(8, seed_start=31337), 31337)
            solve_pack(tmp / "pack", tmp / "warm.json", brain_dir=brain)
            warm_verdict = evaluate_predictions(tmp / "pack", tmp / "warm.json")
            self.assertTrue(warm_verdict["seal_ok"])
            self.assertGreater(
                warm_verdict["solver_scores"]["accuracy"],
                cold_verdict["solver_scores"]["accuracy"],
            )
            # Tamper with truths -> seal breaks.
            truths = tmp / "pack" / "truths.json"
            truths.write_text(truths.read_text(encoding="utf-8") + " ", encoding="utf-8")
            broken = evaluate_predictions(tmp / "pack", tmp / "warm.json")
            self.assertFalse(broken["seal_ok"])
            self.assertEqual(broken["verdict"], "FAIL")

    def test_credit_applies_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            brain = Path(tmp) / "brain"
            mind = TAECMind(brain_dir=brain)
            train_mind(mind, build_dataset(8, seed_start=4242), 4242)
            dry = run_credit(seed=99999, n_traces=4, brain_dir=brain, apply=False)
            self.assertGreater(dry["n_predictions"], 0)
            run_credit(seed=99999, n_traces=4, brain_dir=brain, apply=True)
            reloaded = TAECMind(brain_dir=brain)
            total_uses = sum(i.use_count for i in reloaded.bank.items.values())
            self.assertGreater(total_uses, 0)


if __name__ == "__main__":
    unittest.main()
