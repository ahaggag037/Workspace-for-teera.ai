"""Protocol runner for the first executable F1–F3 slice."""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

from .contracts import Trace, to_dict
from .event_compiler import EventCompiler
from .hazard import HazardModel
from .predictors import EventTransitionPredictor, RawTokenPredictor, SuccessorRepresentationPredictor
from .scoring import (
    boundary_f1,
    interval_coverage,
    mean_absolute_error,
    summarize_classification,
)
from .synthetic import LABELS, build_dataset


def _metric_mean(rows: list[dict[str, float]], key: str) -> float:
    values = [row[key] for row in rows if isinstance(row.get(key), (int, float)) and not math.isnan(row[key])]
    return mean(values) if values else float("nan")


def _compile_traces(traces: list[Trace], compiler: EventCompiler):
    return [compiler.compile(trace.observations, trace_id=trace.trace_id) for trace in traces]


def _evaluate_predictions(
    traces: list[Trace], compiled, raw: RawTokenPredictor, event: EventTransitionPredictor, sr: SuccessorRepresentationPredictor
) -> dict[str, Any]:
    targets: list[str] = []
    raw_predictions: list[dict[str, float]] = []
    event_predictions: list[dict[str, float]] = []
    sr_predictions: list[dict[str, float]] = []
    for trace, graph in zip(traces, compiled):
        events = graph.events
        for index, truth_event in enumerate(trace.truth_events[:-1]):
            next_type = trace.truth_events[index + 1].event_type
            current_indices = set(truth_event.source_indices)
            observations = [item for item in trace.observations if item.index in current_indices]
            targets.append(next_type)
            raw_predictions.append(raw.predict(observations))
            event_predictions.append(event.predict(events[: index + 1]))
            sr_predictions.append(sr.predict(events[: index + 1]))

    return {
        "raw_token": summarize_classification(targets, raw_predictions, LABELS),
        "event_transition": summarize_classification(targets, event_predictions, LABELS),
        "successor_representation": summarize_classification(targets, sr_predictions, LABELS),
    }


def _evaluate_boundaries(traces: list[Trace], compiled) -> dict[str, float]:
    truth: list[int] = []
    predicted: list[int] = []
    offset = 0
    for trace, graph in zip(traces, compiled):
        truth.extend(offset + event.source_indices[0] for event in trace.truth_events[1:])
        predicted.extend(offset + event.source_indices[0] for event in graph.events[1:])
        offset += len(trace.observations)
    return boundary_f1(truth, predicted)


def _evaluate_hazard(traces: list[Trace], hazard: HazardModel) -> dict[str, float]:
    type_targets: list[str] = []
    type_predictions: list[dict[str, float]] = []
    timing_errors: list[float] = []
    intervals: list[tuple[float, float]] = []
    actual_delays: list[float] = []
    for trace in traces:
        for index, current in enumerate(trace.truth_events[:-1]):
            following = trace.truth_events[index + 1]
            forecast = hazard.forecast(current, trace.regime, f"{trace.trace_id}-f{index}")
            probabilities = {candidate.event_type: candidate.probability for candidate in forecast.candidates}
            best = max(forecast.candidates, key=lambda candidate: candidate.probability)
            actual_delay = following.start - current.end
            type_targets.append(following.event_type)
            type_predictions.append(probabilities)
            timing_errors.append(abs(actual_delay - ((best.time_window[0] + best.time_window[1]) / 2)))
            intervals.append(best.time_window)
            actual_delays.append(actual_delay)
    return {
        "n": len(type_targets),
        "type_accuracy": sum(
            max(prediction, key=prediction.get) == truth
            for truth, prediction in zip(type_targets, type_predictions)
        ) / len(type_targets) if type_targets else 0.0,
        "mean_absolute_time_error": mean_absolute_error(timing_errors),
        "time_window_coverage": interval_coverage(actual_delays, intervals),
    }


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# TAEC Lab — F1–F3 Protocol Report",
        "",
        "> STATUS: PROTOCOL_TEST_ONLY. This is synthetic evidence for implementation debugging, not capability evidence.",
        "",
        f"- Seed: `{report['config']['seed']}`",
        f"- Train traces: `{report['config']['train_traces']}`",
        f"- Test traces: `{report['config']['test_traces']}`",
        f"- Held-out status: `{report['heldout_status']}`",
        "",
        "## Boundary detection (F1)",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for key, value in report["f1_boundaries"].items():
        lines.append(f"| {key} | {value:.6f} |")
    lines += ["", "## Next-event forecasting", "", "| condition | accuracy | log loss | Brier | ECE |", "|---|---:|---:|---:|---:|"]
    for condition, metrics in report["f1_f3_forecasting"].items():
        lines.append(
            f"| {condition} | {metrics['accuracy']:.6f} | {metrics['log_loss']:.6f} | {metrics['brier']:.6f} | {metrics['ece']:.6f} |"
        )
    lines += ["", "## Hazard/time-to-event", "", "| metric | value |", "|---|---:|"]
    for key, value in report["hazard"].items():
        lines.append(f"| {key} | {value:.6f} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- This run validates that the protocol, contracts, traces, and scoring path execute end-to-end.",
        "- It does not prove generalization, consciousness, self-improvement, or superiority of COK/RCC.",
        "- A real held-out evaluator and multi-seed confirmation are still required.",
    ]
    return "\n".join(lines) + "\n"


def run_protocol(
    seed: int = 20260924,
    train_count: int = 40,
    test_count: int = 20,
    difficulty: str = "easy",
    report_dir: str | Path | None = None,
) -> dict[str, Any]:
    train = build_dataset(train_count, seed_start=seed, regimes=("stable", "stressed"),
                          difficulty=difficulty)
    test = build_dataset(test_count, seed_start=seed + 10000,
                         regimes=("drift", "stressed", "stable"), difficulty=difficulty)
    compiler = EventCompiler(gap_threshold=0.75)
    compiled_train = _compile_traces(train, compiler)
    compiled_test = _compile_traces(test, compiler)

    raw = RawTokenPredictor(LABELS)
    raw.fit(train)
    event = EventTransitionPredictor(LABELS)
    event.fit(graph.events for graph in compiled_train)
    sr = SuccessorRepresentationPredictor(LABELS, gamma=0.8)
    sr.fit(graph.events for graph in compiled_train)
    hazard = HazardModel(LABELS)
    hazard.fit(train)

    report: dict[str, Any] = {
        "status": "PROTOCOL_TEST_ONLY",
        "heldout_status": "NOT_RUN",
        "claim_scope": "synthetic implementation protocol; no capability claim",
        "config": {"seed": seed, "train_traces": train_count, "test_traces": test_count,
                   "difficulty": difficulty},
        "f1_boundaries": _evaluate_boundaries(test, compiled_test),
        "f1_f3_forecasting": _evaluate_predictions(test, compiled_test, raw, event, sr),
        "hazard": _evaluate_hazard(test, hazard),
        "artifacts": {
            "compiler": "EventCompiler.v0",
            "raw_baseline": "RawTokenPredictor.v0",
            "event_baseline": "EventTransitionPredictor.v0",
            "successor": "SuccessorRepresentation.v0",
            "hazard": "HazardModel.v0",
        },
    }
    if report_dir is not None:
        directory = Path(report_dir)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "protocol-f1-f3.json").write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
        )
        (directory / "protocol-f1-f3.md").write_text(_markdown_report(report), encoding="utf-8")
    return report
