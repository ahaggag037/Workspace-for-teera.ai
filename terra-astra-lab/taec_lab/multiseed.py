"""Multi-seed confirmation for cold-vs-warm external-memory transfer.

Runs the memory evaluation over several disjoint seeds and aggregates
mean / sd / min / max plus an approximate 95% CI. A win on one seed is
a hint; a win on all seeds is a protocol-level result.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Sequence

from .eval_memory import run_memory_eval

METRICS = ("accuracy", "log_loss", "brier", "ece")


def _aggregate(values: list[float]) -> dict[str, float]:
    k = len(values)
    sd = pstdev(values) if k > 1 else 0.0
    ci = 1.96 * sd / math.sqrt(k) if k > 1 else 0.0
    return {
        "mean": mean(values),
        "sd": sd,
        "min": min(values),
        "max": max(values),
        "ci95": ci,
    }


def run_multiseed(
    seeds: Sequence[int] = (20260924, 424242, 777777),
    train_count: int = 40,
    test_count: int = 20,
    difficulty: str = "easy",
    report_dir: str | Path | None = None,
) -> dict[str, Any]:
    per_seed: list[dict[str, Any]] = []
    for seed in seeds:
        per_seed.append(
            run_memory_eval(
                seed=seed, train_count=train_count, test_count=test_count,
                difficulty=difficulty,
            )
        )
    aggregate: dict[str, Any] = {}
    for section in ("cold_start", "warm_memory"):
        aggregate[section] = {
            metric: _aggregate([rep[section][metric] for rep in per_seed])
            for metric in METRICS
        }
    aggregate["delta"] = {
        metric: _aggregate([rep["delta"][metric] for rep in per_seed])
        for metric in METRICS
    }
    wins = sum(1 for rep in per_seed if rep["delta"]["accuracy"] > 0)
    report: dict[str, Any] = {
        "status": "PROTOCOL_TEST_ONLY",
        "heldout_status": "NOT_RUN",
        "claim_scope": "multi-seed synthetic external-memory transfer; no model-weight claim",
        "config": {
            "seeds": list(seeds),
            "k": len(seeds),
            "train_traces": train_count,
            "test_traces": test_count,
            "difficulty": difficulty,
        },
        "aggregate": aggregate,
        "consistency": {
            "seeds_won_accuracy": wins,
            "seeds_total": len(seeds),
            "verdict": "PASS" if wins == len(seeds) and aggregate["delta"]["accuracy"]["mean"] > 0 else "FAIL",
        },
        "per_seed": [
            {"seed": seed, "cold_start": rep["cold_start"],
             "warm_memory": rep["warm_memory"], "delta": rep["delta"]}
            for seed, rep in zip(seeds, per_seed)
        ],
    }
    if report_dir is not None:
        directory = Path(report_dir)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "multiseed.json").write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
        )
        (directory / "multiseed.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _markdown(report: dict[str, Any]) -> str:
    agg = report["aggregate"]
    lines = [
        "# TAEC Lab — Multi-Seed Memory Transfer",
        "",
        "> STATUS: PROTOCOL_TEST_ONLY. Synthetic transfer across disjoint seeds.",
        "",
        f"- Seeds: `{report['config']['seeds']}` (k={report['config']['k']})",
        f"- Train/test: `{report['config']['train_traces']}/{report['config']['test_traces']}`",
        f"- Difficulty: `{report['config']['difficulty']}`",
        f"- Consistency: `{report['consistency']['seeds_won_accuracy']}/{report['consistency']['seeds_total']}` → **{report['consistency']['verdict']}**",
        "",
        "## Aggregate delta (warm − cold; + means memory helped)",
        "",
        "| metric | mean | sd | min | max | ±95% CI |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        d = agg["delta"][metric]
        lines.append(
            f"| {metric} | {d['mean']:+.6f} | {d['sd']:.6f} | {d['min']:+.6f} | {d['max']:+.6f} | {d['ci95']:.6f} |"
        )
    lines += ["", "## Per-seed accuracy (cold → warm)", "", "| seed | cold | warm | delta |", "|---|---:|---:|---:|"]
    for row in report["per_seed"]:
        lines.append(
            f"| {row['seed']} | {row['cold_start']['accuracy']:.4f} | "
            f"{row['warm_memory']['accuracy']:.4f} | {row['delta']['accuracy']:+.4f} |"
        )
    lines += [
        "",
        "## Reading",
        "",
        "- PASS requires warm to beat cold on accuracy in every seed.",
        "- This rules out single-seed luck, not synthetic-world bias.",
        "- The sealed held-out pack is the next independent gate.",
    ]
    return "\n".join(lines) + "\n"
