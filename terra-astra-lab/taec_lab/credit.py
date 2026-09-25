"""Lesson credit assignment: the knowledge bank grades itself.

For each dev prediction, the retrieved lessons share credit/blame for the
outcome. `apply=True` writes use/success counts back into the bank, so
future retrieval prefers lessons with a proven record (P3 + P6).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .mind import TAECMind
from .synthetic import build_dataset


def run_credit(
    seed: int = 20280924,
    n_traces: int = 12,
    brain_dir: str | Path | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    mind = TAECMind(brain_dir=brain_dir) if brain_dir else TAECMind()
    traces = build_dataset(n_traces, seed_start=seed,
                           regimes=("stable", "stressed", "drift"), difficulty="easy")
    tally: dict[str, list[int]] = {}
    n_predictions = 0
    n_correct = 0
    for trace in traces:
        graph = mind.compile(trace.observations, trace_id=trace.trace_id)
        events = graph.events
        for k in range(len(trace.truth_events) - 1):
            truth = trace.truth_events[k + 1].event_type
            result = mind.predict_next(events[: k + 1], regime=trace.regime)
            top = max(result.probabilities, key=result.probabilities.get)
            correct = top == truth
            n_predictions += 1
            n_correct += int(correct)
            for kid in result.knowledge_ids:
                cell = tally.setdefault(kid, [0, 0])
                cell[0] += 1
                cell[1] += int(correct)
    table = []
    for kid, (uses, hits) in sorted(tally.items()):
        table.append({"item_id": kid, "uses": uses, "hits": hits,
                      "reliability": hits / uses if uses else 0.0})
    table.sort(key=lambda row: (row["reliability"], row["uses"]), reverse=True)
    if apply:
        for row in table:
            item = mind.bank.items.get(row["item_id"])
            if item is not None:
                item.use_count += row["uses"]
                item.success_count += row["hits"]
        mind.bank.save(mind.knowledge_path)
    return {
        "status": "CREDIT_ASSIGNMENT",
        "applied": apply,
        "mind_status": mind.status,
        "n_predictions": n_predictions,
        "accuracy": n_correct / n_predictions if n_predictions else 0.0,
        "lessons_touched": len(table),
        "table": table,
    }
