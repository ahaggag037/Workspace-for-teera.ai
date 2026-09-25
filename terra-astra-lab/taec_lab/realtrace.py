"""Real-trace bridge (phase 5 pilot): TAEC Mind over REAL work events.

This module is the lab's first NON-SYNTHETIC task family (roadmap gate #8,
first half). The data source is `telemetry/worklog.jsonl`: an append-only
ledger of real agent-work events (reads, edits, test runs, evals, commits)
with per-event corroboration (git refs, artifact paths, unittest output).
No synthetic generator is involved anywhere in the pilot.

Ontology transfer hypothesis: the same 7-type event grammar learned on the
synthetic world (observe/request/create/fail/recover/escalate/resolve)
is applied to real work events through a documented deterministic lexicon
(OPS_LEXICON). Each ledger row is one observation and one event boundary
(real events are already event-level, so boundaries are explicit).

Task: next-event TYPE prediction on the real ledger.
Arms (pre-registered, all on the same temporal split):
  - uniform: 1/7 on every step.
  - freq_prior: Laplace-smoothed train-segment type frequencies.
  - synth_zero_shot: the existing WARM synthetic banks (main brain),
    untouched, predicting on real events (P5 humility will flatten the
    unseen "ops" regime — that is by design, not a bug).
  - real_learned: a FRESH brain trained ONLY on the train segment of the
    real ledger (never saved to the synthetic brain).

Pre-registered gates (written before any eval run; do not retune after):
  R1 (sanity):   n_test >= 12, else verdict INCONCLUSIVE.
  R2 (primary):  real_learned accuracy > freq_prior accuracy.
  R3 (primary):  real_learned log-loss < freq_prior log-loss.
  R4 (reported): synth_zero_shot accuracy > uniform accuracy.
  verdict = PASS iff R1 and R2 and R3; FAIL iff R1 and not (R2 and R3).
  Kill condition: on FAIL, the Mind is NOT used for operational forecasting;
  ledger collection continues (data tap is independent of operator verdict).

Honesty notes baked into the report:
- Pilot scale: one work session, tens of events. Small-n, wide uncertainty.
- Inter-event wall time was not recorded this session, so observations use
  sequence time (1.0 spacing); hazard/time-window signals are therefore
  NOT meaningful here and are reported as such.
- The ledger is a replay of this session corroborated by artifacts; from
  now on new rows are appended live by `worklog-record` as work happens.
"""

from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from .contracts import Event, Observation, Trace
from .event_compiler import EventCompiler
from .mind import TAECMind
from .scoring import summarize_classification
from .synthetic import LABELS

DEFAULT_LEDGER = Path(__file__).resolve().parent.parent / "telemetry" / "worklog.jsonl"

# Deterministic lexicon: real work verb -> TAEC 7-type event ontology.
OPS_LEXICON: dict[str, tuple[str, ...]] = {
    "observe": ("read", "status", "recall", "boot", "inspect", "search", "look", "sense"),
    "request": ("plan", "goal", "task", "ask"),
    "create": ("edit", "write", "implement", "lesson", "build", "draft", "compose", "make"),
    "fail": ("test_fail", "eval_fail", "gate_fail", "error", "block"),
    "recover": ("fix", "revert", "debug", "repair", "restore", "patch"),
    "escalate": ("eval", "seal", "gate", "alert", "raise", "urgent"),
    "resolve": ("test_pass", "eval_pass", "commit", "push", "document", "done", "close", "stable"),
}

VERB_TO_OP: dict[str, str] = {
    verb: op for op, verbs in OPS_LEXICON.items() for verb in verbs
}
OPS_COMPILER = EventCompiler(lexicon=OPS_LEXICON)
OPS_TRAIN_FRACTION = 0.60
MIN_TEST_EVENTS = 12  # gate R1


def load_ledger(path: str | Path = DEFAULT_LEDGER) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    rows.sort(key=lambda row: int(row["seq"]))
    return rows


def append_event(row: dict[str, Any], path: str | Path = DEFAULT_LEDGER) -> int:
    ledger = load_ledger(path)
    seq = (int(ledger[-1]["seq"]) + 1) if ledger else 1
    row = dict(row)
    row["seq"] = seq
    row.setdefault("outcome", "ok")
    row.setdefault("source", "live-turn")
    row.setdefault("corroborated_by", "")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return seq


def op_type(row: dict[str, Any]) -> str:
    verb = str(row.get("verb", "")).lower()
    mapped = VERB_TO_OP.get(verb)
    if mapped is not None:
        return mapped
    return "unknown" if verb not in {v for vs in OPS_LEXICON.values() for v in vs} else "unknown"


def to_observations(rows: list[dict[str, Any]]) -> list[Observation]:
    """One observation per real event; explicit one-to-one boundaries."""
    observations: list[Observation] = []
    for index, row in enumerate(rows):
        observations.append(
            Observation(
                index=index,
                timestamp=float(index),  # sequence time; wall time not recorded
                token=str(row.get("verb", "")).lower(),
                state_signature=f"phase-{row.get('phase', 'na')}",
                features={
                    "regime": "ops",
                    "area": str(row.get("area", "na")),
                    "outcome": str(row.get("outcome", "na")),
                },
            )
        )
    return observations


def compile_ops(rows: list[dict[str, Any]], trace_id: str = "real") -> list[Event]:
    observations = to_observations(rows)
    starts = list(range(len(observations)))  # each real event is one event
    graph = OPS_COMPILER.compile(observations, trace_id=trace_id, starts=starts)
    return list(graph.events)


def _split(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cut = int(len(rows) * OPS_TRAIN_FRACTION)
    return rows[:cut], rows[cut:]


def _freq_prior(train_rows: list[dict[str, Any]]) -> dict[str, float]:
    counts = Counter(op_type(row) for row in train_rows)
    smoothed = {label: counts.get(label, 0) + 1.0 for label in LABELS}
    total = sum(smoothed.values())
    return {label: smoothed[label] / total for label in LABELS}


def _train_real_brain(train_rows: list[dict[str, Any]], brain_dir: Path) -> TAECMind:
    """Fresh brain trained ONLY on the real train segment (never the synthetic one)."""
    mind = TAECMind(brain_dir=brain_dir)
    events = compile_ops(train_rows, trace_id="real-train")
    trace = Trace(
        trace_id="real-train",
        observations=tuple(to_observations(train_rows)),
        truth_events=tuple(events),
        regime="ops",
    )
    mind.weights.update_transitions([events])
    mind.weights.update_hazard([trace])
    mind.weights.rebuild_successor()
    mind.weights.note_training(len(train_rows), seed=0)
    mind.save()
    return TAECMind(brain_dir=brain_dir)  # reload from disk like a fresh run


def run_realtrace_eval(
    ledger_path: str | Path = DEFAULT_LEDGER,
    report_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Pilot: does the TAEC Mind say anything about REAL work-event streams?"""
    rows = load_ledger(ledger_path)
    train_rows, test_rows = _split(rows)
    all_events = compile_ops(rows, trace_id="real")
    train_events = compile_ops(train_rows, trace_id="real-train")

    truth = [op_type(row) for row in test_rows]
    uniform = {label: 1.0 / len(LABELS) for label in LABELS}
    freq = _freq_prior(train_rows)

    synth_mind = TAECMind()  # main synthetic WARM brain, read-only
    with tempfile.TemporaryDirectory(prefix="taec-real-") as tmp:
        real_mind = _train_real_brain(train_rows, Path(tmp) / "brain-real")
        arms: dict[str, list[dict[str, float]]] = {
            "uniform": [],
            "freq_prior": [],
            "synth_zero_shot": [],
            "real_learned": [],
        }
        for k in range(len(train_rows) - 1, len(rows) - 1):
            context = all_events[: k + 1]
            arms["uniform"].append(dict(uniform))
            arms["freq_prior"].append(dict(freq))
            arms["synth_zero_shot"].append(
                synth_mind.predict_next(context, regime="ops").probabilities
            )
            arms["real_learned"].append(
                real_mind.predict_next(context, regime="ops").probabilities
            )

    metrics = {
        arm: summarize_classification(truth, predictions, LABELS)
        for arm, predictions in arms.items()
    }
    r1 = len(truth) >= MIN_TEST_EVENTS
    r2 = metrics["real_learned"]["accuracy"] > metrics["freq_prior"]["accuracy"]
    r3 = metrics["real_learned"]["log_loss"] < metrics["freq_prior"]["log_loss"]
    r4 = metrics["synth_zero_shot"]["accuracy"] > metrics["uniform"]["accuracy"]
    verdict = "PASS" if (r1 and r2 and r3) else ("FAIL" if r1 else "INCONCLUSIVE")
    report: dict[str, Any] = {
        "status": "PILOT_REAL_TRACE",
        "claim_scope": (
            "first real (non-synthetic) trace family at pilot scale; "
            "no capability claim; operator usage gated on verdict"
        ),
        "ledger": {
            "path": str(ledger_path),
            "n_events": len(rows),
            "n_train": len(train_rows),
            "n_test": len(truth),
            "op_histogram_all": dict(Counter(op_type(row) for row in rows)),
        },
        "split": {"rule": f"temporal {int(OPS_TRAIN_FRACTION * 100)}/{100 - int(OPS_TRAIN_FRACTION * 100)}", "train_ops": dict(Counter(op_type(r) for r in train_rows)), "test_ops": dict(Counter(op_type(r) for r in test_rows))},
        "arms": metrics,
        "gates": {"R1_min_test": r1, "R2_real_acc_gt_freq": r2, "R3_real_ll_lt_freq": r3, "R4_synth_acc_gt_uniform_reported": r4},
        "verdict": verdict,
        "kill_condition": (
            "on FAIL: Mind not used for operational forecasting; ledger tap continues"
        ),
        "honesty_notes": [
            "one session, tens of events; small-n pilot",
            "sequence time (1.0 spacing): hazard/time-window signals not meaningful here",
            "ledger rows are artifact-corroborated replays; live rows append going forward",
        ],
    }
    if report_dir is not None:
        directory = Path(report_dir)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "realtrace-pilot.json").write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        (directory / "realtrace-pilot.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TAEC Lab — Real-Trace Pilot (phase 5)",
        "",
        "> STATUS: PILOT_REAL_TRACE. First non-synthetic task family; small-n by design.",
        "",
        f"- Verdict: **{report['verdict']}**",
        f"- Ledger: `{report['ledger']['path']}` — {report['ledger']['n_events']} real events "
        f"(train {report['ledger']['n_train']} / test {report['ledger']['n_test']})",
        "",
        "| arm | accuracy | log loss | Brier | ECE |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in ("uniform", "freq_prior", "synth_zero_shot", "real_learned"):
        m = report["arms"][arm]
        lines.append(
            f"| {arm} | {m['accuracy']:.6f} | {m['log_loss']:.6f} | {m['brier']:.6f} | {m['ece']:.6f} |"
        )
    lines += ["", "| gate | result |", "|---|:---:|"]
    for gate, passed in report["gates"].items():
        lines.append(f"| {gate} | {'✅' if passed else '❌'} |")
    lines += [
        "",
        "## Reading",
        "",
        "- Same frozen protocol as the synthetic phases, applied to REAL work events.",
        "- `synth_zero_shot` tests zero-shot ontology transfer from the synthetic banks.",
        "- `real_learned` is trained only on the real train segment (fresh brain, separate dir).",
        "- Sequence time only: time-window metrics are not meaningful in this pilot.",
        "- Pilot scale: verdicts are directional, not confirmatory.",
    ]
    return "\n".join(lines) + "\n"
