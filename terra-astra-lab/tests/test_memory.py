import tempfile
import unittest
from pathlib import Path

from taec_lab.eval_memory import run_memory_eval
from taec_lab.knowledge import KnowledgeBank, KnowledgeItem
from taec_lab.learning import train_mind
from taec_lab.mind import TAECMind
from taec_lab.synthetic import build_dataset
from taec_lab.weights import ExternalWeights


class MemoryTests(unittest.TestCase):
    def test_weights_persist_and_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            brain = Path(tmp) / "brain"
            mind = TAECMind(brain_dir=brain)
            self.assertEqual(mind.status, "COLD_START")
            traces = build_dataset(6, seed_start=999, regimes=("stable",))
            result = train_mind(mind, traces, 999)
            self.assertEqual(result["status"], "WARM")
            self.assertTrue((brain / "WEIGHTS.json").exists())
            self.assertTrue((brain / "KNOWLEDGE.jsonl").exists())
            reloaded = TAECMind(brain_dir=brain)
            self.assertEqual(reloaded.status, "WARM")
            self.assertFalse(reloaded.weights.is_empty())
            self.assertGreater(len(reloaded.bank), 0)

    def test_knowledge_retrieval_prefers_relevant(self):
        bank = KnowledgeBank()
        bank.add(KnowledgeItem("a", "fail escalate stressed", "after fail expect escalate",
                               ("stressed", "fail"), "test", 0.9))
        bank.add(KnowledgeItem("b", "create resolve stable", "after create expect resolve",
                               ("stable", "create"), "test", 0.9))
        hits = bank.search("stressed fail next event forecast", top_k=1)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].item_id, "a")

    def test_cold_vs_warm_runs(self):
        report = run_memory_eval(seed=777, train_count=6, test_count=4)
        self.assertEqual(report["status"], "PROTOCOL_TEST_ONLY")
        self.assertIn("cold_start", report)
        self.assertIn("warm_memory", report)
        self.assertIn("delta", report)


if __name__ == "__main__":
    unittest.main()
