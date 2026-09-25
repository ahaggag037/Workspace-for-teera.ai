"""Simple time-to-event hazard model for the protocol slice."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable

from .contracts import Event, Forecast, ForecastCandidate, Trace


class HazardModel:
    def __init__(self, labels: Iterable[str]) -> None:
        self.labels = tuple(labels)
        self._counts: dict[tuple[str, str, str], int] = defaultdict(int)
        self._durations: dict[tuple[str, str, str], list[float]] = defaultdict(list)

    def fit(self, traces: Iterable[Trace]) -> None:
        for trace in traces:
            for current, following in zip(trace.truth_events, trace.truth_events[1:]):
                key = (trace.regime, current.event_type, following.event_type)
                self._counts[key] += 1
                self._durations[key].append(max(0.0, following.start - current.end))

    def _mean_sd(self, values: list[float]) -> tuple[float, float]:
        if not values:
            return 1.0, 0.5
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        return mean, math.sqrt(variance)

    def forecast(self, event: Event, regime: str, forecast_id: str) -> Forecast:
        counts = {
            label: self._counts.get((regime, event.event_type, label), 0)
            for label in self.labels
        }
        total = sum(counts.values())
        if total == 0:
            counts = {label: 1 for label in self.labels}
            total = len(self.labels)
        candidates: list[ForecastCandidate] = []
        for label in self.labels:
            probability = counts[label] / total
            mean, sd = self._mean_sd(self._durations.get((regime, event.event_type, label), []))
            low = max(0.0, mean - sd)
            high = mean + sd
            candidates.append(
                ForecastCandidate(
                    event_type=label,
                    probability=probability,
                    time_window=(low, high),
                    conditions=(f"regime={regime}", f"after={event.event_type}"),
                    leading_indicators=(f"{event.event_type}:transition",),
                    disconfirming_signals=(f"regime_change:{regime}",),
                    causal_path=(event.event_type, label),
                    consequence=f"next_event={label}",
                    expiry=high,
                )
            )
        candidates.sort(key=lambda candidate: candidate.probability, reverse=True)
        return Forecast(
            forecast_id=forecast_id,
            origin_event_id=event.event_id,
            horizon="meso",
            candidates=tuple(candidates),
            mode="observational",
            provenance={"operator": "HazardModel.v0", "regime": regime},
        )
