"""Learning loop: traces -> external weights + knowledge lessons."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .contracts import Trace
from .event_compiler import EventCompiler
from .knowledge import KnowledgeItem
from .mind import TAECMind
from .synthetic import LABELS


def extract_lessons(traces: Iterable[Trace]) -> list[KnowledgeItem]:
    """Derive small interpretable lessons from ground-truth transitions."""
    traces = list(traces)
    counts: dict[tuple[str, str], Counter[str]] = {}
    for trace in traces:
        for current, following in zip(trace.truth_events, trace.truth_events[1:]):
            key = (trace.regime, current.event_type)
            counts.setdefault(key, Counter())[following.event_type] += 1
    lessons = []
    for (regime, current), counter in sorted(counts.items()):
        total = sum(counter.values())
        top, top_count = counter.most_common(1)[0]
        item_id = f"lesson-{regime}-{current}"
        lessons.append(
            KnowledgeItem(
                item_id=item_id,
                title=f"After {current} in {regime}, expect {top}",
                content=(
                    f"In regime {regime}, event {current} transitions to {top} "
                    f"in {top_count}/{total} observed cases. "
                    f"Full distribution: {dict(counter)}."
                ),
                tags=("transition", regime, current, top, "forecast"),
                source="synthetic-training",
                confidence=min(0.95, 0.5 + top_count / max(1, total) / 2),
            )
        )
    return lessons


def train_mind(mind: TAECMind, traces: list[Trace], seed: int) -> dict:
    compiler = EventCompiler()
    compiled = [compiler.compile(t.observations, trace_id=t.trace_id) for t in traces]
    mind.weights.update_transitions(graph.events for graph in compiled)
    mind.weights.update_hazard(traces)
    mind.weights.rebuild_successor()
    mind.weights.note_training(len(traces), seed)
    lessons = extract_lessons(traces)
    for lesson in lessons:
        mind.bank.add(lesson)
    mind.save()
    return {
        "traces": len(traces),
        "lessons": len(lessons),
        "weights_updates": mind.weights.meta["updates"],
        "status": mind.status,
    }
