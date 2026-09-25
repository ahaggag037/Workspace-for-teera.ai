"""Boundary detection, event parsing, and lightweight event graph construction."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from .contracts import Event, Observation


DEFAULT_LEXICON: dict[str, tuple[str, ...]] = {
    "observe": ("scan", "look", "sense", "pulse"),
    "request": ("ask", "intent", "need", "request"),
    "create": ("build", "draft", "compose", "make"),
    "fail": ("error", "block", "fault", "fail"),
    "recover": ("repair", "restore", "stabilize", "recover"),
    "escalate": ("alert", "raise", "urgent", "escalate"),
    "resolve": ("close", "done", "stable", "resolve"),
}


@dataclass
class EventGraph:
    events: list[Event] = field(default_factory=list)
    temporal_edges: list[tuple[str, str, str]] = field(default_factory=list)
    causal_edges: list[tuple[str, str, str]] = field(default_factory=list)
    semantic_edges: list[tuple[str, str, str]] = field(default_factory=list)
    goal_edges: list[tuple[str, str, str]] = field(default_factory=list)
    conflict_edges: list[tuple[str, str, str]] = field(default_factory=list)

    def add_events(self, events: Iterable[Event]) -> None:
        event_list = list(events)
        self.events.extend(event_list)
        for left, right in zip(event_list, event_list[1:]):
            self.temporal_edges.append((left.event_id, "precedes", right.event_id))
            if left.event_type in {"observe", "request", "create", "recover"}:
                self.causal_edges.append((left.event_id, "enables", right.event_id))
            if left.goal and left.goal == right.goal:
                self.goal_edges.append((left.event_id, "serves", right.event_id))
            if {left.event_type, right.event_type} == {"fail", "resolve"}:
                self.semantic_edges.append((left.event_id, "opposes", right.event_id))


class BoundaryDetector:
    def __init__(self, gap_threshold: float = 0.75) -> None:
        self.gap_threshold = gap_threshold

    def boundary_positions(self, observations: list[Observation]) -> list[int]:
        if not observations:
            return []
        positions = [0]
        for position in range(1, len(observations)):
            previous = observations[position - 1]
            current = observations[position]
            gap = current.timestamp - previous.timestamp
            if gap > self.gap_threshold or current.state_signature != previous.state_signature:
                positions.append(position)
        return positions


class EventParser:
    def __init__(self, lexicon: dict[str, tuple[str, ...]] | None = None) -> None:
        self.lexicon = lexicon or DEFAULT_LEXICON
        self._reverse = {
            token: event_type
            for event_type, tokens in self.lexicon.items()
            for token in tokens
        }

    def parse_type(self, observations: list[Observation]) -> tuple[str, float, tuple[str, ...]]:
        scores: Counter[str] = Counter()
        evidence: list[str] = []
        for observation in observations:
            token = observation.token.lower()
            event_type = self._reverse.get(token)
            if event_type:
                scores[event_type] += 1
                evidence.append(token)
        if not scores:
            return "unknown", 0.0, tuple()
        event_type, score = scores.most_common(1)[0]
        total = sum(scores.values())
        return event_type, score / total, tuple(evidence)


class EventCompiler:
    """Small executable Event Compiler for the first protocol slice."""

    def __init__(
        self,
        gap_threshold: float = 0.75,
        lexicon: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self.detector = BoundaryDetector(gap_threshold=gap_threshold)
        self.parser = EventParser(lexicon=lexicon)

    def compile(self, observations: Iterable[Observation], trace_id: str = "trace") -> EventGraph:
        ordered = list(observations)
        if not ordered:
            return EventGraph()
        starts = self.detector.boundary_positions(ordered)
        groups: list[list[Observation]] = []
        for position, start in enumerate(starts):
            end = starts[position + 1] if position + 1 < len(starts) else len(ordered)
            groups.append(ordered[start:end])

        events: list[Event] = []
        previous: Event | None = None
        for index, group in enumerate(groups):
            event_type, confidence, evidence = self.parser.parse_type(group)
            first = group[0]
            last = group[-1]
            regime = str(first.features.get("regime")) if first.features.get("regime") else None
            goal = str(first.features.get("goal")) if first.features.get("goal") else None
            event = Event(
                event_id=f"{trace_id}-e{index}",
                event_type=event_type,
                start=first.timestamp,
                end=last.timestamp,
                source_indices=tuple(item.index for item in group),
                confidence=confidence,
                regime=regime,
                goal=goal,
                effects=tuple(str(item.features["effect"]) for item in group if "effect" in item.features),
                causal_parents=(previous.event_id,) if previous else tuple(),
                temporal_relations={"previous": previous.event_id} if previous else {},
                semantic_tags=tuple(sorted(set(evidence))),
                provenance={"operator": "EventCompiler.v0", "observation_count": len(group)},
            )
            events.append(event)
            previous = event

        graph = EventGraph()
        graph.add_events(events)
        return graph
