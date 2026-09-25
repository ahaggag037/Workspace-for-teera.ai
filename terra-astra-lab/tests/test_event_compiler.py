import unittest

from taec_lab.contracts import Observation
from taec_lab.event_compiler import EventCompiler


class EventCompilerTests(unittest.TestCase):
    def test_compiles_two_events_and_relations(self):
        observations = [
            Observation(0, 0.0, "scan", "a", {"regime": "stable"}),
            Observation(1, 0.2, "pulse", "a", {"regime": "stable"}),
            Observation(2, 1.5, "ask", "b", {"regime": "stable"}),
            Observation(3, 1.7, "intent", "b", {"regime": "stable"}),
        ]
        graph = EventCompiler(gap_threshold=0.75).compile(observations, trace_id="x")
        self.assertEqual([event.event_type for event in graph.events], ["observe", "request"])
        self.assertEqual(len(graph.temporal_edges), 1)
        self.assertEqual(graph.events[1].causal_parents, ("x-e0",))
        self.assertGreaterEqual(graph.events[0].confidence, 0.9)

    def test_empty_trace_is_safe(self):
        graph = EventCompiler().compile([])
        self.assertEqual(graph.events, [])


if __name__ == "__main__":
    unittest.main()
