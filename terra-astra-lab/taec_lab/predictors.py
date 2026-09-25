"""Baseline predictors and a lightweight successor representation."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable, Mapping, Sequence

from .contracts import Event, Observation, Trace
from .scoring import normalize


class RawTokenPredictor:
    """A deliberately weak baseline: last low-level token -> next event type."""

    def __init__(self, labels: Sequence[str]) -> None:
        self.labels = tuple(labels)
        self._counts: dict[str, Counter[str]] = defaultdict(Counter)
        self._prior: Counter[str] = Counter()

    def fit(self, traces: Iterable[Trace]) -> None:
        for trace in traces:
            for current, following in zip(trace.truth_events, trace.truth_events[1:]):
                current_tokens = [
                    observation.token
                    for observation in trace.observations
                    if observation.index in current.source_indices
                ]
                if not current_tokens:
                    continue
                self._counts[current_tokens[-1]][following.event_type] += 1
                self._prior[following.event_type] += 1

    def predict(self, observations: Sequence[Observation]) -> dict[str, float]:
        token = observations[-1].token if observations else ""
        counts = self._counts.get(token)
        if not counts:
            counts = self._prior
        return normalize(counts, self.labels)


class EventTransitionPredictor:
    """First-order event graph transition baseline."""

    def __init__(self, labels: Sequence[str]) -> None:
        self.labels = tuple(labels)
        self._counts: dict[str, Counter[str]] = defaultdict(Counter)
        self._prior: Counter[str] = Counter()

    def fit(self, event_sequences: Iterable[Sequence[Event]]) -> None:
        for events in event_sequences:
            for current, following in zip(events, events[1:]):
                self._counts[current.event_type][following.event_type] += 1
                self._prior[following.event_type] += 1

    def transition_matrix(self) -> dict[str, dict[str, float]]:
        matrix: dict[str, dict[str, float]] = {}
        for label in self.labels:
            matrix[label] = normalize(self._counts.get(label, {}), self.labels)
        return matrix

    def predict(self, events: Sequence[Event]) -> dict[str, float]:
        if not events:
            return normalize(self._prior, self.labels)
        return normalize(self._counts.get(events[-1].event_type, self._prior), self.labels)


class SuccessorRepresentation:
    """Discounted expected future occupancy over event states.

    This is intentionally small and dependency-free. It is a representation
    primitive, not evidence that a model has hippocampal function.
    """

    def __init__(self, labels: Sequence[str], gamma: float = 0.8, steps: int = 12) -> None:
        self.labels = tuple(labels)
        self.gamma = gamma
        self.steps = steps
        self.index = {label: index for index, label in enumerate(self.labels)}
        self.transition: list[list[float]] = []
        self.matrix: list[list[float]] = []

    def fit(self, event_sequences: Iterable[Sequence[Event]]) -> None:
        n = len(self.labels)
        counts = [[1.0 for _ in range(n)] for _ in range(n)]
        for events in event_sequences:
            for current, following in zip(events, events[1:]):
                if current.event_type in self.index and following.event_type in self.index:
                    counts[self.index[current.event_type]][self.index[following.event_type]] += 1.0
        self.transition = []
        for row in counts:
            total = sum(row)
            self.transition.append([value / total for value in row])

        identity = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        occupancy = [[identity[i][j] for j in range(n)] for i in range(n)]
        power = identity
        discount = self.gamma
        for _ in range(self.steps):
            power = _matmul(power, self.transition)
            for i in range(n):
                for j in range(n):
                    occupancy[i][j] += discount * power[i][j]
            discount *= self.gamma
        self.matrix = occupancy

    def predict(self, current_event_type: str) -> dict[str, float]:
        if not self.matrix or current_event_type not in self.index:
            uniform = 1.0 / len(self.labels) if self.labels else 0.0
            return {label: uniform for label in self.labels}
        row = self.matrix[self.index[current_event_type]].copy()
        row[self.index[current_event_type]] = 0.0
        return normalize(dict(zip(self.labels, row)), self.labels)


class SuccessorRepresentationPredictor:
    def __init__(self, labels: Sequence[str], gamma: float = 0.8) -> None:
        self.sr = SuccessorRepresentation(labels, gamma=gamma)

    def fit(self, event_sequences: Iterable[Sequence[Event]]) -> None:
        self.sr.fit(event_sequences)

    def predict(self, events: Sequence[Event]) -> dict[str, float]:
        if not events:
            uniform = 1.0 / len(self.sr.labels) if self.sr.labels else 0.0
            return {label: uniform for label in self.sr.labels}
        return self.sr.predict(events[-1].event_type)


def _matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    n = len(left)
    result = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if left[i][k] == 0.0:
                continue
            for j in range(n):
                result[i][j] += left[i][k] * right[k][j]
    return result
