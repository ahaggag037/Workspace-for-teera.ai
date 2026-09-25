import math
import unittest

from taec_lab.scoring import accuracy, boundary_f1, interval_coverage, summarize_classification, top_label


class ScoringTests(unittest.TestCase):
    def test_classification_metrics_are_finite(self):
        truth = ["a", "b"]
        predictions = [{"a": 0.8, "b": 0.2}, {"a": 0.1, "b": 0.9}]
        result = summarize_classification(truth, predictions, ("a", "b"))
        self.assertEqual(result["accuracy"], 1.0)
        self.assertTrue(math.isfinite(result["log_loss"]))
        self.assertTrue(math.isfinite(result["brier"]))

    def test_argmax_tie_break_is_order_independent(self):
        forward = {"b": 0.5, "a": 0.5}
        backward = {"a": 0.5, "b": 0.5}
        self.assertEqual(top_label(forward), "a")
        self.assertEqual(top_label(backward), "a")
        self.assertEqual(accuracy(["a"], [forward]), 1.0)
        self.assertEqual(accuracy(["a"], [backward]), 1.0)

    def test_boundary_and_interval_metrics(self):
        result = boundary_f1([2, 4], [2, 4])
        self.assertEqual(result["f1"], 1.0)
        self.assertEqual(interval_coverage([1.0, 3.0], [(0.5, 1.5), (2.0, 2.5)]), 0.5)


if __name__ == "__main__":
    unittest.main()
