"""Typed contracts for event-centric traces and forecast attribution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Observation:
    index: int
    timestamp: float
    token: str
    state_signature: str
    features: dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    event_id: str
    event_type: str
    start: float
    end: float
    source_indices: tuple[int, ...]
    confidence: float
    regime: str | None = None
    goal: str | None = None
    effects: tuple[str, ...] = ()
    causal_parents: tuple[str, ...] = ()
    temporal_relations: dict[str, str] = field(default_factory=dict)
    semantic_tags: tuple[str, ...] = ()
    conflict_relations: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass
class ForecastCandidate:
    event_type: str
    probability: float
    time_window: tuple[float, float]
    conditions: tuple[str, ...] = ()
    leading_indicators: tuple[str, ...] = ()
    disconfirming_signals: tuple[str, ...] = ()
    causal_path: tuple[str, ...] = ()
    consequence: str | None = None
    intervention: str | None = None
    expiry: float | None = None


@dataclass
class Forecast:
    forecast_id: str
    origin_event_id: str | None
    horizon: str
    candidates: tuple[ForecastCandidate, ...]
    mode: str = "observational"
    created_at: float | None = None
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass
class ForecastResidual:
    forecast_id: str
    type_error: float
    timing_error: float
    omitted_event: bool
    false_event: bool
    causal_error: bool = False
    regime_error: bool = False
    consequence_error: bool = False
    calibration_error: float = 0.0
    notes: str = ""


@dataclass
class PathwayCertificate:
    claim_id: str
    saved_evidence: tuple[str, ...]
    retrieved_evidence: tuple[str, ...]
    applied_operator: str
    verified_outcome: str
    later_transfer: str
    status: str = "UNKNOWN"


@dataclass
class Trace:
    trace_id: str
    observations: tuple[Observation, ...]
    truth_events: tuple[Event, ...]
    regime: str


def to_dict(value: Any) -> Any:
    """Convert contract objects into JSON-compatible primitive values."""
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_dict(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): to_dict(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [to_dict(item) for item in value]
    return value
