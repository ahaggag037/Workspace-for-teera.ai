"""Cold-start vs warm-memory evaluation.

Cold = fresh Mind with empty external weights (uniform fallback).
Warm = same Mind after training on synthetic traces and saving banks.

This measures whether workspace-side learning transfers to new traces.
It is still synthetic protocol evidence, not a model-capability claim.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .learning import train_mind
from .mind import TAECMind
from .scoring import summarize_classification
from .synthetic import LABELS, build_dataset


def _predict_all(mind: TAECMind, traces) -> tuple[list[str], list[dict[str, float]]]:
    targets: list[str] = []
    predictions: list[dict[str, float]] = []
    for trace in traces:
        graph = mind.compile(trace.observations, trace_id=trace.trace_id)
        events = graph.events
        for index in range(len(trace.truth_events) - 1):
            targets.append(trace.truth_events[index + 1].event_type)
            result = mind.predict_next(events[: index + 1], regime=trace.regime)
            predictions.append(result.probabilities)
    return targets, predictions


def run_memory_eval(
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

    tmp = Path(tempfile.mkdtemp(prefix="taec-cold-"))
    try:
        cold_mind = TAECMind(brain_dir=tmp / "cold")
        cold_targets, cold_preds = _predict_all(cold_mind, test)
        cold = summarize_classification(cold_targets, cold_preds, LABELS)

        warm_dir = tmp / "warm"
        warm_mind = TAECMind(brain_dir=warm_dir)
        training = train_mind(warm_mind, train, seed)
        reloaded = TAECMind(brain_dir=warm_dir)
        warm_targets, warm_preds = _predict_all(reloaded, test)
        warm = summarize_classification(warm_targets, warm_preds, LABELS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    report: dict[str, Any] = {
        "status": "PROTOCOL_TEST_ONLY",
        "heldout_status": "NOT_RUN",
        "claim_scope": "synthetic external-memory transfer; no model-weight claim",
        "config": {"seed": seed, "train_traces": train_count, "test_traces": test_count,
                   "difficulty": difficulty},
        "cold_start": cold,
        "warm_memory": warm,
        "delta": {
            "accuracy": warm["accuracy"] - cold["accuracy"],
            "log_loss": cold["log_loss"] - warm["log_loss"],
            "brier": cold["brier"] - warm["brier"],
            "ece": cold["ece"] - warm["ece"],
        },
        "training": training,
    }
    if report_dir is not None:
        directory = Path(report_dir)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "memory-cold-vs-warm.json").write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
        )
        (directory / "memory-cold-vs-warm.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _markdown(report: dict[str, Any]) -> str:
    cold = report["cold_start"]
    warm = report["warm_memory"]
    delta = report["delta"]
    lines = [
        "# TAEC Lab — Cold Start vs Warm Memory",
        "",
        "> STATUS: PROTOCOL_TEST_ONLY. Synthetic transfer of workspace-side memory only.",
        "",
        f"- Seed: `{report['config']['seed']}`",
        f"- Train: `{report['config']['train_traces']}` traces",
        f"- Test: `{report['config']['test_traces']}` traces",
        f"- Lessons stored: `{report['training']['lessons']}`",
        "",
        "| condition | accuracy | log loss | Brier | ECE |",
        "|---|---:|---:|---:|---:|",
        f"| cold (no memory) | {cold['accuracy']:.6f} | {cold['log_loss']:.6f} | {cold['brier']:.6f} | {cold['ece']:.6f} |",
        f"| warm (external memory) | {warm['accuracy']:.6f} | {warm['log_loss']:.6f} | {warm['brier']:.6f} | {warm['ece']:.6f} |",
        f"| delta (warm-cold, +good except logloss/brier/ece shown as cold-warm) | {delta['accuracy']:+.6f} | {delta['log_loss']:+.6f} | {delta['brier']:+.6f} | {delta['ece']:+.6f} |",
        "",
        "## Reading",
        "",
        "- Positive delta means the saved workspace banks helped on unseen synthetic traces.",
        "- This is external-memory learning, not a change to model weights.",
        "- Held-out confirmation with an independent evaluator is still required.",
    ]
    return "\n".join(lines) + "\n"
