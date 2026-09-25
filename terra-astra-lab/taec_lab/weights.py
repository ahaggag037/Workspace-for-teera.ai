"""External weights: persistent learned parameters stored in workspace.

These are NOT model weights. They are workspace-side parameters that change
the behavior of the TAEC Lab Mind from run to run without touching any
model checkpoint. They function as an external memory / policy bank.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence

from .contracts import Trace
from .scoring import normalize


class ExternalWeights:
    """Learned transition / successor / hazard tables persisted as JSON."""

    VERSION = "weights-v1"

    def __init__(self, labels: Sequence[str]) -> None:
        self.labels = tuple(labels)
        self.transition_counts: dict[str, Counter[str]] = {label: Counter() for label in labels}
        self.prior: Counter[str] = Counter()
        self.successor_matrix: list[list[float]] = []
        self.hazard_counts: dict[str, int] = defaultdict(int)
        self.hazard_durations: dict[str, list[float]] = defaultdict(list)
        self.meta: dict = {"updates": 0, "train_traces": 0, "seeds": []}

    # ---- training ----
    def update_transitions(self, event_sequences: Iterable[Sequence]) -> None:
        for events in event_sequences:
            for current, following in zip(events, events[1:]):
                c = current.event_type if hasattr(current, "event_type") else current
                n = following.event_type if hasattr(following, "event_type") else following
                if c in self.labels and n in self.labels:
                    self.transition_counts[c][n] += 1
                    self.prior[n] += 1

    def update_hazard(self, traces: Iterable[Trace]) -> None:
        for trace in traces:
            for current, following in zip(trace.truth_events, trace.truth_events[1:]):
                key = f"{trace.regime}|{current.event_type}|{following.event_type}"
                self.hazard_counts[key] += 1
                self.hazard_durations[key].append(max(0.0, following.start - current.end))

    def rebuild_successor(self, gamma: float = 0.8, steps: int = 12) -> None:
        n = len(self.labels)
        index = {label: i for i, label in enumerate(self.labels)}
        counts = [[1.0 for _ in range(n)] for _ in range(n)]
        for current, counter in self.transition_counts.items():
            for nxt, c in counter.items():
                counts[index[current]][index[nxt]] += float(c)
        transition = []
        for row in counts:
            total = sum(row)
            transition.append([v / total for v in row])
        identity = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        occupancy = [[identity[i][j] for j in range(n)] for i in range(n)]
        power = identity
        discount = gamma
        for _ in range(steps):
            power = _matmul(power, transition)
            for i in range(n):
                for j in range(n):
                    occupancy[i][j] += discount * power[i][j]
            discount *= gamma
        self.successor_matrix = occupancy

    def note_training(self, n_traces: int, seed: int) -> None:
        self.meta["updates"] += 1
        self.meta["train_traces"] += n_traces
        self.meta["seeds"].append(seed)

    # ---- inference ----
    def transition_probs(self, current: str, alpha: float = 1.0) -> dict[str, float]:
        # Laplace smoothing: never assign zero probability. Unsmoothed zeros
        # caused catastrophic log-loss on hard/misaligned traces (found 2026-09-24).
        from collections import Counter as _Counter

        counter = self.transition_counts.get(current, _Counter())
        if sum(counter.values()) == 0:
            counter = self.prior
        smoothed = {label: counter.get(label, 0) + alpha for label in self.labels}
        return normalize(smoothed, self.labels)

    def successor_probs(self, current: str) -> dict[str, float]:
        if not self.successor_matrix or current not in self.labels:
            u = 1.0 / len(self.labels) if self.labels else 0.0
            return {label: u for label in self.labels}
        i = self.labels.index(current)
        row = self.successor_matrix[i][:]
        row[i] = 0.0
        return normalize(dict(zip(self.labels, row)), self.labels)

    def hazard_stats(self, regime: str, current: str, nxt: str) -> tuple[float, float, float]:
        key = f"{regime}|{current}|{nxt}"
        durations = self.hazard_durations.get(key, [])
        total_for_state = sum(
            self.hazard_counts.get(f"{regime}|{current}|{label}", 0) for label in self.labels
        )
        if total_for_state == 0:
            prob = 1.0 / len(self.labels)
            return prob, 1.0, 0.5
        prob = self.hazard_counts.get(key, 0) / total_for_state
        if not durations:
            return prob, 1.0, 0.5
        mean = sum(durations) / len(durations)
        var = sum((d - mean) ** 2 for d in durations) / len(durations)
        return prob, mean, math.sqrt(var)

    # ---- persistence ----
    def to_dict(self) -> dict:
        return {
            "version": self.VERSION,
            "labels": list(self.labels),
            "transition_counts": {k: dict(v) for k, v in self.transition_counts.items()},
            "prior": dict(self.prior),
            "successor_matrix": self.successor_matrix,
            "hazard_counts": dict(self.hazard_counts),
            "hazard_durations": {k: v for k, v in self.hazard_durations.items()},
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "ExternalWeights":
        w = cls(payload.get("labels", []))
        for k, v in payload.get("transition_counts", {}).items():
            w.transition_counts[k] = Counter(v)
        w.prior = Counter(payload.get("prior", {}))
        w.successor_matrix = payload.get("successor_matrix", [])
        w.hazard_counts = defaultdict(int, payload.get("hazard_counts", {}))
        w.hazard_durations = defaultdict(list, payload.get("hazard_durations", {}))
        w.meta = payload.get("meta", {"updates": 0, "train_traces": 0, "seeds": []})
        return w

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path, labels: Sequence[str]) -> "ExternalWeights":
        p = Path(path)
        if not p.exists():
            return cls(labels)
        return cls.from_dict(json.loads(p.read_text(encoding="utf-8")))

    def is_empty(self) -> bool:
        return sum(sum(c.values()) for c in self.transition_counts.values()) == 0


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
