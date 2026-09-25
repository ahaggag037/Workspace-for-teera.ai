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

# ---- v2 pilot pre-registration (written BEFORE the v2 eval run) ----
# Real work streams are phase-structured (boot -> study -> implement ->
# verify -> seal -> document -> persist). The v1 pilot ignored this.
# v2 adds interpolation-level predictive arms with FROZEN weights:
#   markov       : 0.0*pair + 0.7*type + 0.3*marginal
#   phase_markov : 0.5*pair + 0.3*type + 0.2*marginal
# Each level is Laplace-smoothed (alpha=1); empty levels are skipped and
# the remaining weights renormalized (documented deterministic backoff).
# v2 primary gates: R5/R6 (phase_markov beats the constant train prior on
# accuracy AND log-loss); R7/R8 reported (phase adds value over plain
# markov). R2/R3 from v1 stay computed and reported as legacy.
INTERP_WEIGHTS: dict[str, tuple[float, float, float]] = {
    "markov": (0.0, 0.7, 0.3),
    "phase_markov": (0.5, 0.3, 0.2),
}
OPS_ALPHA = 1.0
OPS_BRAIN_DIR = Path(__file__).resolve().parent.parent / "brain-ops"
OPS_BRAIN_PATH = OPS_BRAIN_DIR / "ops-brain.json"


def _smoothed(counter, labels: tuple[str, ...], alpha: float):
    total = sum(counter.values()) if counter else 0
    if total == 0:
        return None
    return {
        label: (counter.get(label, 0) + alpha) / (total + alpha * len(labels))
        for label in labels
    }


def _interp_dist(pair_counter, type_counter, marginal, labels, weights, alpha=OPS_ALPHA):
    """Frozen interpolation over (pair, type, marginal) levels."""
    levels = (
        _smoothed(pair_counter or {}, labels, alpha),
        _smoothed(type_counter or {}, labels, alpha),
        _smoothed(marginal or {}, labels, alpha),
    )
    out = {label: 0.0 for label in labels}
    used = 0.0
    for weight, dist in zip(weights, levels):
        if dist is None:
            continue
        used += weight
        for label in labels:
            out[label] += weight * dist[label]
    if used == 0.0:
        uniform = 1.0 / len(labels)
        return {label: uniform for label in labels}, "uniform"
    return {label: out[label] / used for label in labels}, "interp"


class OpsPhaseBrain:
    """Persistent phase-conditioned transition brain for REAL work events.

    Separate from the synthetic `brain/` banks by design: v1 showed the
    synthetic banks do not transfer zero-shot to real work streams. This
    brain accumulates across sessions and powers `ops-forecast`.
    """

    VERSION = "ops-brain-v1"

    def __init__(self, labels: tuple[str, ...] = LABELS, alpha: float = OPS_ALPHA) -> None:
        self.labels = tuple(labels)
        self.alpha = alpha
        self.pair_counts: dict[str, Counter] = {}
        self.type_counts: dict[str, Counter] = {}
        self.marginal: Counter = Counter()
        self.n_transitions = 0
        self.meta: dict[str, Any] = {"updates": 0, "last_rows_seen": 0}

    def observe_rows(self, rows: list[dict[str, Any]]) -> None:
        typed = [(str(row.get("phase", "na")), op_type(row)) for row in rows]
        for (phase0, type0), (_phase1, type1) in zip(typed, typed[1:]):
            self.pair_counts.setdefault(f"{phase0}|{type0}", Counter())[type1] += 1
            self.type_counts.setdefault(type0, Counter())[type1] += 1
            self.marginal[type1] += 1
            self.n_transitions += 1
        self.meta["updates"] += 1
        self.meta["last_rows_seen"] = len(rows)

    def predict(self, phase: str, current_type: str):
        pair = self.pair_counts.get(f"{phase}|{current_type}")
        typ = self.type_counts.get(current_type)
        return _interp_dist(pair, typ, self.marginal, self.labels, (0.5, 0.3, 0.2), self.alpha)

    def predict_markov(self, current_type: str):
        return _interp_dist(None, self.type_counts.get(current_type), self.marginal,
                            self.labels, INTERP_WEIGHTS["markov"], self.alpha)

    # ---- persistence ----
    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.VERSION,
            "labels": list(self.labels),
            "alpha": self.alpha,
            "pair_counts": {k: dict(v) for k, v in self.pair_counts.items()},
            "type_counts": {k: dict(v) for k, v in self.type_counts.items()},
            "marginal": dict(self.marginal),
            "n_transitions": self.n_transitions,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "OpsPhaseBrain":
        brain = cls(tuple(payload.get("labels", LABELS)), payload.get("alpha", OPS_ALPHA))
        brain.pair_counts = {k: Counter(v) for k, v in payload.get("pair_counts", {}).items()}
        brain.type_counts = {k: Counter(v) for k, v in payload.get("type_counts", {}).items()}
        brain.marginal = Counter(payload.get("marginal", {}))
        brain.n_transitions = int(payload.get("n_transitions", 0))
        brain.meta = payload.get("meta", {"updates": 0, "last_rows_seen": 0})
        return brain

    def save(self, path: str | Path = OPS_BRAIN_PATH) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path = OPS_BRAIN_PATH) -> "OpsPhaseBrain":
        source = Path(path)
        if not source.exists():
            return cls()
        return cls.from_dict(json.loads(source.read_text(encoding="utf-8")))

    def is_empty(self) -> bool:
        return self.n_transitions == 0


def learn_ops_brain(
    ledger_path: str | Path = DEFAULT_LEDGER,
    brain_path: str | Path = OPS_BRAIN_PATH,
) -> dict[str, Any]:
    """Operational learning: absorb the live ledger into the persistent ops
    brain. IDEMPOTENT per ledger prefix: only rows beyond
    meta["last_seq_learned"] are absorbed, so repeated `ops-learn` runs never
    double-count history (found by the phase-7 self-audit: a second learn
    pushed 49 -> 108 transitions from 60 rows; fixed before any forecast
    relied on it). Eval still trains on the train split only."""
    rows = load_ledger(ledger_path)
    brain = OpsPhaseBrain.load(brain_path)
    last_seen = int(brain.meta.get("last_seq_learned", 0) or 0)
    new_rows = [row for row in rows if int(row.get("seq", 0)) > last_seen]
    brain.observe_rows(new_rows)
    if rows:
        brain.meta["last_seq_learned"] = int(rows[-1]["seq"])
    brain.save(brain_path)
    return {
        "status": "OPS_LEARN",
        "brain_path": str(brain_path),
        "n_transitions": brain.n_transitions,
        "rows_seen": len(rows),
        "rows_absorbed": len(new_rows),
        "last_seq_learned": brain.meta["last_seq_learned"],
        "updates": brain.meta["updates"],
        "pair_keys": len(brain.pair_counts),
    }


def forecast_next_ops(
    ledger_path: str | Path = DEFAULT_LEDGER,
    brain_path: str | Path = OPS_BRAIN_PATH,
) -> dict[str, Any]:
    """The Mind forecasting the NEXT real work event from the live ledger tail."""
    rows = load_ledger(ledger_path)
    brain = OpsPhaseBrain.load(brain_path)
    if brain.is_empty():
        uniform = 1.0 / len(LABELS)
        return {
            "status": "COLD_START",
            "note": "run ops-learn first; no operational banks exist yet",
            "honesty": "uniform fallback used explicitly (BOOT rule)",
            "candidates": [{"op": label, "probability": uniform} for label in LABELS],
        }
    last = rows[-1] if rows else None
    phase = str(last.get("phase", "na")) if last else "na"
    current = op_type(last) if last else "observe"
    distribution, _level = brain.predict(phase, current)
    ranked = sorted(distribution.items(), key=lambda item: (-item[1], item[0]))
    return {
        "status": "OPS_FORECAST",
        "brain": str(brain_path),
        "n_transitions": brain.n_transitions,
        "base": {
            "phase": phase,
            "current_type": current,
            "last_verb": str(last.get("verb")) if last else None,
        },
        "candidates": [
            {"op": name, "probability": round(prob, 6)} for name, prob in ranked
        ],
        "honesty": [
            "next-event probabilities only; no wall-clock window (ledger has sequence time)",
            "interp levels frozen (0.5 pair / 0.3 type / 0.2 marginal)",
        ],
    }


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
    phase_brain = OpsPhaseBrain()  # in-memory; trained on the TRAIN split only
    phase_brain.observe_rows(train_rows)
    with tempfile.TemporaryDirectory(prefix="taec-real-") as tmp:
        real_mind = _train_real_brain(train_rows, Path(tmp) / "brain-real")
        arms: dict[str, list[dict[str, float]]] = {
            "uniform": [],
            "freq_prior": [],
            "synth_zero_shot": [],
            "real_learned": [],
            "markov": [],
            "phase_markov": [],
        }
        for k in range(len(train_rows) - 1, len(rows) - 1):
            context = all_events[: k + 1]
            context_phase = str(rows[k].get("phase", "na"))
            context_type = op_type(rows[k])
            arms["uniform"].append(dict(uniform))
            arms["freq_prior"].append(dict(freq))
            arms["synth_zero_shot"].append(
                synth_mind.predict_next(context, regime="ops").probabilities
            )
            arms["real_learned"].append(
                real_mind.predict_next(context, regime="ops").probabilities
            )
            arms["markov"].append(phase_brain.predict_markov(context_type)[0])
            arms["phase_markov"].append(phase_brain.predict(context_phase, context_type)[0])

    metrics = {
        arm: summarize_classification(truth, predictions, LABELS)
        for arm, predictions in arms.items()
    }
    # ---- v1 gates (legacy, still computed and reported) ----
    r1 = len(truth) >= MIN_TEST_EVENTS
    r2 = metrics["real_learned"]["accuracy"] > metrics["freq_prior"]["accuracy"]
    r3 = metrics["real_learned"]["log_loss"] < metrics["freq_prior"]["log_loss"]
    r4 = metrics["synth_zero_shot"]["accuracy"] > metrics["uniform"]["accuracy"]
    # ---- v2 primary gates (pre-registered before the v2 run) ----
    r5 = metrics["phase_markov"]["accuracy"] > metrics["freq_prior"]["accuracy"]
    r6 = metrics["phase_markov"]["log_loss"] < metrics["freq_prior"]["log_loss"]
    r7 = metrics["phase_markov"]["accuracy"] >= metrics["markov"]["accuracy"]
    r8 = metrics["phase_markov"]["log_loss"] <= metrics["markov"]["log_loss"]
    verdict = "PASS" if (r1 and r5 and r6) else ("FAIL" if r1 else "INCONCLUSIVE")
    report: dict[str, Any] = {
        "status": "PILOT_REAL_TRACE",
        "version": 2,
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
        "gates": {
            "R1_min_test": r1,
            "R2_real_acc_gt_freq_legacy": r2,
            "R3_real_ll_lt_freq_legacy": r3,
            "R4_synth_acc_gt_uniform_reported": r4,
            "R5_phase_acc_gt_const": r5,
            "R6_phase_ll_lt_const": r6,
            "R7_phase_acc_ge_markov": r7,
            "R8_phase_ll_le_markov": r8,
        },
        "primary_gates": ["R1", "R5", "R6"],
        "verdict": verdict,
        "kill_condition": (
            "on FAIL: Mind not used for operational forecasting; ledger tap continues"
        ),
        "honesty_notes": [
            "one session, tens of events; small-n pilot",
            "sequence time (1.0 spacing): hazard/time-window signals not meaningful here",
            "freq_prior IS the constant train-majority baseline (Laplace); the uniform arm",
            "  degenerates to always-create via alphabetical tie-break (known v1 caveat)",
            "v2 arms/weights frozen before the v2 run; the v1 report stays archived",
        ],
    }
    if report_dir is not None:
        directory = Path(report_dir)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "realtrace-pilot-v2.json").write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        (directory / "realtrace-pilot-v2.md").write_text(_markdown(report), encoding="utf-8")
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
    for arm in ("uniform", "freq_prior", "synth_zero_shot", "real_learned", "markov", "phase_markov"):
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
