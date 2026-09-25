import math
import unittest

from taec_lab.experiment import run_protocol


class ProtocolTests(unittest.TestCase):
    def test_protocol_produces_bounded_report(self):
        report = run_protocol(seed=1234, train_count=8, test_count=5)
        self.assertEqual(report["status"], "PROTOCOL_TEST_ONLY")
        self.assertEqual(report["heldout_status"], "NOT_RUN")
        self.assertEqual(report["f1_boundaries"]["f1"], 1.0)
        for condition in report["f1_f3_forecasting"].values():
            self.assertGreater(condition["n"], 0)
            self.assertTrue(math.isfinite(condition["brier"]))
        self.assertGreater(report["hazard"]["n"], 0)


if __name__ == "__main__":
    unittest.main()
