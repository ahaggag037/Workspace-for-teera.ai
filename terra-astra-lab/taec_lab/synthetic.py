"""Deterministic synthetic event world for protocol-only F1–F3.

Difficulties:
- easy: clean phase signatures + wide gaps (boundary F1 ~ 1.0, smoke test).
- hard: corrupted signatures, shrunken gaps, heavier distractors, so the
  default compiler misses some boundaries and must cope with merged events.
"""

from __future__ import annotations

import random
from typing import Iterable

from .contracts import Event, Observation, Trace

LABELS = ("observe", "request", "create", "fail", "recover", "escalate", "resolve")
TOKENS = {
    "observe": ("scan", "look", "sense", "pulse"),
    "request": ("ask", "intent", "need", "request"),
    "create": ("build", "draft", "compose", "make"),
    "fail": ("error", "block", "fault", "fail"),
    "recover": ("repair", "restore", "stabilize", "recover"),
    "escalate": ("alert", "raise", "urgent", "escalate"),
    "resolve": ("close", "done", "stable", "resolve"),
}

TRANSITIONS = {
    "stable": {
        "observe": {"request": 0.82, "observe": 0.18},
        "request": {"create": 0.70, "fail": 0.30},
        "create": {"resolve": 0.78, "fail": 0.22},
        "fail": {"recover": 0.70, "escalate": 0.30},
        "recover": {"resolve": 0.72, "request": 0.28},
        "escalate": {"recover": 0.58, "fail": 0.42},
        "resolve": {"observe": 0.55, "request": 0.45},
    },
    "stressed": {
        "observe": {"request": 0.65, "observe": 0.35},
        "request": {"create": 0.40, "fail": 0.60},
        "create": {"resolve": 0.35, "fail": 0.65},
        "fail": {"recover": 0.40, "escalate": 0.60},
        "recover": {"resolve": 0.45, "request": 0.55},
        "escalate": {"recover": 0.35, "fail": 0.65},
        "resolve": {"observe": 0.35, "request": 0.65},
    },
    "drift": {
        "observe": {"request": 0.45, "create": 0.35, "observe": 0.20},
        "request": {"fail": 0.50, "create": 0.30, "escalate": 0.20},
        "create": {"fail": 0.55, "resolve": 0.25, "escalate": 0.20},
        "fail": {"escalate": 0.60, "recover": 0.25, "fail": 0.15},
        "recover": {"request": 0.45, "resolve": 0.35, "escalate": 0.20},
        "escalate": {"fail": 0.50, "recover": 0.35, "resolve": 0.15},
        "resolve": {"request": 0.60, "observe": 0.25, "create": 0.15},
    },
}

DISTRACTORS = ("signal", "context", "state", "trace")


def _sample(rng: random.Random, distribution: dict[str, float]) -> str:
    threshold = rng.random()
    cumulative = 0.0
    for label, probability in distribution.items():
        cumulative += probability
        if threshold <= cumulative:
            return label
    return next(reversed(distribution))


def generate_trace(
    trace_id: str,
    seed: int,
    n_events: int = 14,
    regime: str | None = None,
    difficulty: str = "easy",
) -> Trace:
    hard = difficulty == "hard"
    rng = random.Random(seed)
    selected_regime = regime or ("stable", "stressed", "drift")[seed % 3]
    events: list[Event] = []
    observations: list[Observation] = []
    current_type = "observe"
    current_time = 0.0
    previous_phase = "phase-start"

    for event_index in range(n_events):
        event_type = current_type
        count = 2 + rng.randrange(3)
        phase = f"phase-{event_index}"
        if hard and event_index > 0 and rng.random() < 0.35:
            phase = previous_phase  # corrupted signature: no observable change
        previous_phase = f"phase-{event_index}"
        indices: list[int] = []
        start = current_time
        for offset in range(count):
            token_options = TOKENS[event_type]
            if hard:
                distractor_p = 0.15 if offset == count - 1 else 0.60
            else:
                distractor_p = 0.0 if offset == count - 1 else 0.35
            if rng.random() < distractor_p:
                token = rng.choice(DISTRACTORS)
            else:
                token = rng.choice(token_options)
            observation = Observation(
                index=len(observations),
                timestamp=current_time + offset * 0.20,
                token=token,
                state_signature=phase,
                features={
                    "regime": selected_regime,
                    "goal": "stabilize" if event_type in {"fail", "recover", "escalate"} else "complete",
                    "effect": event_type,
                },
            )
            observations.append(observation)
            indices.append(observation.index)
        end = observations[-1].timestamp
        next_type = _sample(rng, TRANSITIONS[selected_regime][event_type])
        events.append(
            Event(
                event_id=f"{trace_id}-e{event_index}",
                event_type=event_type,
                start=start,
                end=end,
                source_indices=tuple(indices),
                confidence=1.0,
                regime=selected_regime,
                goal="stabilize" if event_type in {"fail", "recover", "escalate"} else "complete",
                effects=(f"next={next_type}",),
                provenance={"source": "synthetic_event_world", "seed": seed, "difficulty": difficulty},
            )
        )
        current_type = next_type
        if hard and rng.random() < 0.35:
            gap = 0.20 + rng.random() * 0.20  # below the 0.75 detector threshold
        else:
            gap = 1.0 + rng.random() * 0.25
        current_time = end + gap

    return Trace(
        trace_id=trace_id,
        observations=tuple(observations),
        truth_events=tuple(events),
        regime=selected_regime,
    )


def build_dataset(
    count: int,
    seed_start: int,
    regimes: Iterable[str] | None = None,
    difficulty: str = "easy",
) -> list[Trace]:
    choices = tuple(regimes) if regimes is not None else ("stable", "stressed", "drift")
    traces = []
    for index in range(count):
        seed = seed_start + index
        traces.append(
            generate_trace(
                trace_id=f"trace-{seed}",
                seed=seed,
                regime=choices[index % len(choices)],
                difficulty=difficulty,
            )
        )
    return traces
