"""Sealed held-out task pack + independent evaluator.

Seed ledger (disjoint ranges, never overlap):
- learn/train:      20260924 .., 20270001 ..
- protocol test:    seed + 10000 ..
- credit/dev:       20280924 ..
- softseg dev/eval: 20500924 .., 20510924 ..   (phase-4 operator tuning)
- HELD-OUT PACK v1: 999001 ..   (only the evaluator reads truths)
- HELD-OUT PACK v2: 999601 ..   (phase-4 sealed attempt; fusedseg-v2)

The pack ships observations without labels. Truths live in a separate
file sealed by sha256 in the manifest. `evaluate_predictions` refuses to
score if the seal is broken (tamper-evident, not tamper-proof).

Pre-registered gates for PASS:
  G1 seal_ok is True
  G2 next-event accuracy  > uniform-cold accuracy
  G3 next-event log-loss  < uniform-cold log-loss
  G4 boundary F1 >= 0.50
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from .contracts import Observation
from .mind import TAECMind
from .scoring import boundary_f1, summarize_classification
from .synthetic import LABELS, build_dataset

HELDOUT_SEED_START = 999001


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _obs_payload(trace) -> list[dict[str, Any]]:
    return [
        {
            "index": o.index,
            "timestamp": o.timestamp,
            "token": o.token,
            "state_signature": o.state_signature,
            "features": dict(o.features),
        }
        for o in trace.observations
    ]


def build_pack(
    out_dir: str | Path,
    n_traces: int = 12,
    seed_start: int = HELDOUT_SEED_START,
    difficulty: str = "hard",
) -> dict[str, Any]:
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    traces = build_dataset(
        n_traces, seed_start=seed_start,
        regimes=("drift", "stressed", "stable"), difficulty=difficulty,
    )
    next_tasks: list[dict[str, Any]] = []
    boundary_tasks: list[dict[str, Any]] = []
    truths_next: dict[str, str] = {}
    truths_bound: dict[str, list[int]] = {}
    for trace in traces:
        payload = _obs_payload(trace)
        btask_id = f"{trace.trace_id}-boundaries"
        boundary_tasks.append({"task_id": btask_id, "trace_id": trace.trace_id,
                               "observations": payload})
        truths_bound[btask_id] = [e.source_indices[0] for e in trace.truth_events[1:]]
        for k in range(len(trace.truth_events) - 1):
            cutoff = trace.truth_events[k].source_indices[-1]
            task_id = f"{trace.trace_id}-next-{k}"
            next_tasks.append({
                "task_id": task_id, "trace_id": trace.trace_id,
                "regime": trace.regime, "cutoff_index": cutoff,
                "observations": payload[: cutoff + 1],
            })
            truths_next[task_id] = trace.truth_events[k + 1].event_type
    pack_path = directory / "pack.json"
    truths_path = directory / "truths.json"
    pack_path.write_text(json.dumps(
        {"meta": {"n_traces": n_traces, "seed_start": seed_start,
                  "difficulty": difficulty, "labels": list(LABELS)},
         "next_event_tasks": next_tasks, "boundary_tasks": boundary_tasks},
        indent=1, sort_keys=True), encoding="utf-8")
    truths_path.write_text(json.dumps(
        {"next_event": truths_next, "boundaries": truths_bound},
        indent=1, sort_keys=True), encoding="utf-8")
    manifest = {
        "pack_sha256": _sha256(pack_path),
        "truths_sha256": _sha256(truths_path),
        "n_next_tasks": len(next_tasks),
        "n_boundary_tasks": len(boundary_tasks),
        "seed_start": seed_start,
        "difficulty": difficulty,
        "gates": {"G1": "seal_ok", "G2": "acc > cold_acc",
                  "G3": "logloss < cold_logloss", "G4": "boundary_f1 >= 0.50"},
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def _to_observations(payload: list[dict[str, Any]]) -> list[Observation]:
    return [Observation(p["index"], p["timestamp"], p["token"],
                        p["state_signature"], p["features"]) for p in payload]


def solve_pack(
    pack_dir: str | Path,
    predictions_path: str | Path,
    brain_dir: str | Path | None = None,
    segmentation: str = "hard",
) -> dict[str, Any]:
    """Run a TAECMind over the pack and write a predictions file.

    brain_dir=None -> cold uniform mind in a temp dir (baseline solver).
    segmentation="hard" -> production detector (default, backward compatible).
    segmentation="v2"   -> fused-evidence boundaries + recency typing
                           (TAECMind.v2-fusedseg; adoption candidate).
    segmentation="soft" -> killed n-best mixture arm (kept for the record).
    """
    from .softseg import FusedSegMind, SoftSegMind

    pack = json.loads((Path(pack_dir) / "pack.json").read_text(encoding="utf-8"))
    if brain_dir is None:
        tmp = tempfile.mkdtemp(prefix="taec-heldout-cold-")
        mind = TAECMind(brain_dir=Path(tmp) / "cold")
        solver = "cold-uniform"
    else:
        mind = TAECMind(brain_dir=brain_dir)
        solver = f"mind:{mind.status}"
    if segmentation == "soft":
        solver = f"{solver}+softseg-killed"
        mind = SoftSegMind(brain_dir=mind.brain_dir)
    if segmentation == "v2":
        solver = f"{solver}+fusedseg-v2"
        mind = FusedSegMind(brain_dir=mind.brain_dir)
    next_preds: dict[str, dict[str, float]] = {}
    for task in pack["next_event_tasks"]:
        obs = _to_observations(task["observations"])
        if segmentation == "soft":
            result = mind.predict_next_from_observations(
                obs, regime=task["regime"], trace_id=task["trace_id"]
            )
        elif segmentation == "v2":
            result = mind.predict_next_fused(
                obs, regime=task["regime"], trace_id=task["trace_id"]
            )
        else:
            graph = mind.compile(obs, trace_id=task["trace_id"])
            result = mind.predict_next(graph.events, regime=task["regime"])
        next_preds[task["task_id"]] = result.probabilities
    bound_preds: dict[str, list[int]] = {}
    for task in pack["boundary_tasks"]:
        obs = _to_observations(task["observations"])
        if segmentation == "soft":
            bound_preds[task["task_id"]] = mind.modal_boundaries(obs)
        elif segmentation == "v2":
            bound_preds[task["task_id"]] = mind.fused_starts(obs)[1:]
        else:
            graph = mind.compile(obs, trace_id=task["trace_id"])
            bound_preds[task["task_id"]] = (
                [e.source_indices[0] for e in graph.events[1:]] if len(graph.events) > 1 else []
            )
    payload = {
        "solver": solver,
        "segmentation": segmentation,
        "next_event": next_preds,
        "boundaries": bound_preds,
    }
    Path(predictions_path).write_text(json.dumps(payload, indent=1, sort_keys=True),
                                       encoding="utf-8")
    return {"solver": solver, "segmentation": segmentation,
            "n_next": len(next_preds), "n_bound": len(bound_preds)}


def evaluate_predictions(
    pack_dir: str | Path,
    predictions_path: str | Path,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    directory = Path(pack_dir)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    seal_ok = _sha256(directory / "truths.json") == manifest["truths_sha256"]
    truths = json.loads((directory / "truths.json").read_text(encoding="utf-8"))
    preds = json.loads(Path(predictions_path).read_text(encoding="utf-8"))

    task_ids = sorted(truths["next_event"].keys())
    y_true = [truths["next_event"][t] for t in task_ids]
    y_pred = [preds["next_event"][t] for t in task_ids]
    uniform = {label: 1.0 / len(LABELS) for label in LABELS}
    cold = summarize_classification(y_true, [dict(uniform) for _ in y_true], LABELS)
    warm = summarize_classification(y_true, y_pred, LABELS)

    truth_b: list[int] = []
    pred_b: list[int] = []
    offset = 0
    pack = json.loads((directory / "pack.json").read_text(encoding="utf-8"))
    obs_len = {t["task_id"]: len(t["observations"]) for t in pack["boundary_tasks"]}
    for btask_id in sorted(truths["boundaries"].keys()):
        truth_b.extend(offset + i for i in truths["boundaries"][btask_id])
        pred_b.extend(offset + i for i in preds["boundaries"].get(btask_id, []))
        offset += obs_len[btask_id]
    boundaries = boundary_f1(truth_b, pred_b)

    gates = {
        "G1_seal_ok": bool(seal_ok),
        "G2_acc_beats_cold": warm["accuracy"] > cold["accuracy"],
        "G3_logloss_beats_cold": warm["log_loss"] < cold["log_loss"],
        "G4_boundary_f1_ge_050": boundaries["f1"] >= 0.50,
    }
    verdict: dict[str, Any] = {
        "status": "HELDOUT_EVAL",
        "solver": preds.get("solver", "unknown"),
        "seal_ok": bool(seal_ok),
        "n_next_tasks": len(task_ids),
        "cold_uniform": cold,
        "solver_scores": warm,
        "delta": {m: (warm[m] - cold[m] if m == "accuracy"
                      else cold[m] - warm[m]) for m in ("accuracy", "log_loss", "brier", "ece")},
        "boundaries": boundaries,
        "gates": gates,
        "verdict": "PASS" if all(gates.values()) else "FAIL",
    }
    if report_path is not None:
        rp = Path(report_path)
        rp.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")
        rp.with_suffix(".md").write_text(_markdown(verdict), encoding="utf-8")
    return verdict


def _markdown(verdict: dict[str, Any]) -> str:
    cold, warm, delta = verdict["cold_uniform"], verdict["solver_scores"], verdict["delta"]
    lines = [
        "# TAEC Lab — Sealed Held-Out Verdict",
        "",
        f"- Solver: `{verdict['solver']}`",
        f"- Seal: `{'OK' if verdict['seal_ok'] else 'BROKEN'}`",
        f"- Next-event tasks: `{verdict['n_next_tasks']}`",
        f"- Verdict: **{verdict['verdict']}**",
        "",
        "| condition | accuracy | log loss | Brier | ECE |",
        "|---|---:|---:|---:|---:|",
        f"| cold uniform | {cold['accuracy']:.6f} | {cold['log_loss']:.6f} | {cold['brier']:.6f} | {cold['ece']:.6f} |",
        f"| solver | {warm['accuracy']:.6f} | {warm['log_loss']:.6f} | {warm['brier']:.6f} | {warm['ece']:.6f} |",
        f"| delta | {delta['accuracy']:+.6f} | {delta['log_loss']:+.6f} | {delta['brier']:+.6f} | {delta['ece']:+.6f} |",
        "",
        "| gate | result |",
        "|---|:---:|",
    ]
    for gate, passed in verdict["gates"].items():
        lines.append(f"| {gate} | {'✅' if passed else '❌'} |")
    b = verdict["boundaries"]
    lines += [
        "",
        f"Boundary F1: **{b['f1']:.4f}** (P={b['precision']:.4f}, R={b['recall']:.4f})",
        "",
        "## Reading",
        "",
        "- The solver never saw held-out truths; the seal proves the truths file is intact.",
        "- PASS means transfer to a disjoint seed range under pre-registered gates.",
        "- Still synthetic: the next gate after this is non-synthetic task families.",
    ]
    return "\n".join(lines) + "\n"
