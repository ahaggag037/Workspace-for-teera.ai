import json
import unittest

from taec_lab.contracts import Event, ForecastCandidate, Observation, to_dict


class ContractTests(unittest.TestCase):
    def test_contracts_are_json_serializable(self):
        observation = Observation(0, 0.0, "scan", "phase-0", {"regime": "stable"})
        event = Event("t-e0", "observe", 0.0, 0.2, (0,), 1.0)
        candidate = ForecastCandidate("request", 0.5, (0.5, 1.5))
        payload = to_dict({"observation": observation, "event": event, "candidate": candidate})
        encoded = json.dumps(payload)
        self.assertIn("observe", encoded)
        self.assertIn("request", encoded)


if __name__ == "__main__":
    unittest.main()
