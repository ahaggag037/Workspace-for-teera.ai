"""TAEC Mind: auto-loading external mind over workspace banks.

Boot behavior:
1. Look for brain_dir (default: <lab>/brain).
2. Load WEIGHTS.json and KNOWLEDGE.jsonl if present.
3. Report COLD_START (no banks) or WARM (banks loaded).

The Mind never claims to change model weights. It changes its own
workspace-side state, which changes its predictions on the next run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from .contracts import Event, Forecast, ForecastCandidate, Observation
from .event_compiler import EventCompiler
from .knowledge import KnowledgeBank
from .scoring import normalize
from .synthetic import LABELS
from .weights import ExternalWeights


def default_brain_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "brain"


@dataclass
class MindPrediction:
    probabilities: dict[str, float]
    forecast: Forecast
    knowledge_ids: tuple[str, ...] = ()
    mind_status: str = "COLD_START"


class TAECMind:
    def __init__(
        self,
        brain_dir: str | Path | None = None,
        labels: Sequence[str] = LABELS,
        gamma: float = 0.8,
    ) -> None:
        self.labels = tuple(labels)
        self.brain_dir = Path(brain_dir) if brain_dir else default_brain_dir()
        self.weights_path = self.brain_dir / "WEIGHTS.json"
        self.knowledge_path = self.brain_dir / "KNOWLEDGE.jsonl"
        self.weights = ExternalWeights.load(self.weights_path, self.labels)
        self.bank = KnowledgeBank.load(self.knowledge_path)
        self.compiler = EventCompiler()
        self.gamma = gamma
        self.status = "WARM" if not self.weights.is_empty() else "COLD_START"

    def compile(self, observations: Sequence[Observation], trace_id: str = "live"):
        return self.compiler.compile(observations, trace_id=trace_id)

    def predict_next(
        self,
        events: Sequence[Event],
        regime: str = "stable",
        origin_id: str | None = None,
    ) -> MindPrediction:
        current = events[-1].event_type if events else "observe"
        humility = 0.0
        if self.weights.is_empty():
            uniform = 1.0 / len(self.labels)
            probs = {label: uniform for label in self.labels}
        else:
            trans = self.weights.transition_probs(current)
            succ = self.weights.successor_probs(current)
            # Fixed interpretable ensemble: transition carries the sharp
            # next-step signal, successor carries multi-step occupancy.
            probs = normalize(
                {label: 0.7 * trans[label] + 0.3 * succ[label] for label in self.labels},
                self.labels,
            )
            # P5 regime humility (mechanism, not prose): flatten toward
            # uniform when training support is thin (e.g. unseen regime)
            # or the compiled event is low-confidence (e.g. merged group).
            support = sum(
                self.weights.hazard_counts.get(f"{regime}|{current}|{label}", 0)
                for label in self.labels
            )
            last_conf = events[-1].confidence if events else 0.0
            humility = min(0.6, 5.0 / (5.0 + support) + 0.3 * (1.0 - last_conf))
            uniform_p = 1.0 / len(self.labels)
            probs = {
                label: (1.0 - humility) * p + humility * uniform_p
                for label, p in probs.items()
            }
        query = f"{regime} {current} next event forecast"
        hits = self.bank.search(query, top_k=2)
        candidates = []
        for label in self.labels:
            _, mean, sd = self.weights.hazard_stats(regime, current, label)
            low = max(0.0, mean - sd)
            high = mean + sd
            candidates.append(
                ForecastCandidate(
                    event_type=label,
                    probability=probs[label],
                    time_window=(low, high),
                    conditions=(f"regime={regime}", f"after={current}"),
                    leading_indicators=(f"{current}:transition",),
                    disconfirming_signals=(f"regime_change:{regime}",),
                    causal_path=(current, label),
                    consequence=f"next_event={label}",
                    expiry=high,
                )
            )
        candidates.sort(key=lambda c: c.probability, reverse=True)
        forecast = Forecast(
            forecast_id=f"{origin_id or 'live'}-forecast",
            origin_event_id=origin_id,
            horizon="meso",
            candidates=tuple(candidates),
            mode="observational",
            provenance={
                "operator": "TAECMind.v1",
                "mind_status": self.status,
                "knowledge": [h.item_id for h in hits],
                "weights_updates": self.weights.meta.get("updates", 0),
                "humility_lambda": round(humility, 4),
            },
        )
        return MindPrediction(
            probabilities=probs,
            forecast=forecast,
            knowledge_ids=tuple(h.item_id for h in hits),
            mind_status=self.status,
        )

    def save(self) -> None:
        self.weights.save(self.weights_path)
        self.bank.save(self.knowledge_path)
        if not self.weights.is_empty():
            self.status = "WARM"
