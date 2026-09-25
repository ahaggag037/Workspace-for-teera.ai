"""Soft segmentation: boundary-uncertainty-aware prediction (phase 4).

Why this exists (see brain/STATE.md): incremental hard-mode learning went
FLAT and the diagnosed bottleneck was segmentation under corruption, not
transition statistics. When two adjacent events get merged (hidden gap +
corrupted signature in hard mode), the Mind predicts from the WRONG
`current` event type, so transition/successor banks cannot help.

Research arc (all tuned on dev seeds 20500924.. ONLY, frozen before any
sealed attempt; documented honestly per AGENTS.md):

1. H-mixture (SoftSegMind): n-best boundary hypotheses weighted by
   hazard-duration plausibility, mixed next-event distributions.
   RESULT: boundary F1 improved slightly but typing NEVER rescued a wrong
   anchor (6 correct->wrong flips vs 0 wrong->correct on dev) and the
   softmax flattening taxed log-loss. Root cause found: the bank's hazard
   duration tables conflate easy/hard gap regimes (1.0-1.25 vs 0.2-0.4),
   so merged hypotheses fit the learned durations BETTER than the true
   fine segmentation. KILLED per P8; kept here only as the recorded
   ablation arm.
2. H-transition scoring: plausibility from learned transition matrix.
   RESULT: dominated as well (merged typing still yields plausible
   transitions). KILLED.
3. v2 fused-segmentation (FusedSegMind, ADOPTED CANDIDATE):
   - Boundary detector v2: per-position fused evidence (time gap +
     state-signature change + lexicon-switch) with the frozen rule
     "phase change OR true lexical-type switch".
   - Recency typing: the FINAL group's type for prediction is the type of
     its last lexical token (compiled majority type as fallback), so a
     merged group still predicts from the state that actually ended.
   DEV RESULT: strictly dominates hard on every pre-registered metric
   (accuracy +0.016, log-loss -0.075, Brier -0.023, boundary F1 +0.036).

Protocol honesty (AGENTS.md):
- Pre-registered gates A1-A3 on the untouched eval split, then one sealed
  held-out attempt. Kill condition: on FAIL the operator is DISABLED
  (research-only) and the hard detector remains the default.
- Ablation is inference-only: all arms run on the SAME frozen banks.
- Still synthetic protocol evidence; no capability claims.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from .contracts import Event, Observation, Trace, to_dict
from .mind import MindPrediction, TAECMind
from .scoring import boundary_f1, normalize, summarize_classification
from .synthetic import LABELS, build_dataset

# ---- frozen operator constants (tuned on dev seeds ONLY, then frozen
# before any sealed eval; do not retune after seeing sealed results) ----
GAP_FLOOR = 0.200001          # within-event spacing in the synthetic world
GAP_SPAN = 0.199              # gap -> full evidence at ~0.4 time units
W_GAP, W_PHASE, W_LEX = 0.40, 0.35, 0.25
LEX_SWITCH = 1.0              # lexical token -> different-type lexical token
LEX_TO_DISTRACTOR = 0.7       # lexical token -> distractor (hard-mode tell)
BOUNDARY_RULE_PHASE = W_PHASE - 1e-9          # pure phase change
BOUNDARY_RULE_LEX = W_LEX * LEX_SWITCH - 1e-9  # true lexical-type switch
EVIDENCE_GRID = (0.30, 0.45, 0.60)  # dev-sweep grid (recorded; mixture only)
HARD_GAP = 0.75               # anchor hypothesis == production detector
BOUNDARY_BONUS = 0.25
COMPLEXITY_PENALTY = 0.03
TAU = 1.2                     # mixture temperature (killed arm, kept frozen)

# Pre-registered gates (written BEFORE the sealed attempt).
DEV_SEED_START = 20500924     # disjoint from learn/test/credit/heldout ranges
EVAL_SEED_START = 20510924    # untouched by tuning
GATE_LOGLOSS_SLACK = 0.05


@dataclass(frozen=True)
class Hypothesis:
    starts: tuple[int, ...]
    score: float
    weight: float


def boundary_evidence(observations: Sequence[Observation], parser) -> list[float]:
    """Per-position boundary evidence s_i in [0,1]; position 0 gets 0.0.

    Three deterministic signals, fused linearly:
    - gap:    time since previous observation exceeding the world's
              within-event spacing;
    - phase:  state-signature change;
    - lex:    lexicon-switch evidence (lexical->different-type lexical,
              or lexical->distractor), which survives signature corruption.
    """
    scores = [0.0]
    for position in range(1, len(observations)):
        previous = observations[position - 1]
        current = observations[position]
        gap = max(0.0, current.timestamp - previous.timestamp)
        gap_signal = min(1.0, max(0.0, (gap - GAP_FLOOR) / GAP_SPAN))
        phase_signal = 1.0 if current.state_signature != previous.state_signature else 0.0
        previous_type = parser.token_type(previous.token)
        current_type = parser.token_type(current.token)
        if previous_type is not None and current_type is not None and previous_type != current_type:
            lex_signal = LEX_SWITCH
        elif previous_type is not None and current_type is None:
            lex_signal = LEX_TO_DISTRACTOR
        else:
            lex_signal = 0.0
        scores.append(W_GAP * gap_signal + W_PHASE * phase_signal + W_LEX * lex_signal)
    return scores


def _starts_from_rule(evidence: Sequence[float], rule) -> tuple[int, ...]:
    return (0,) + tuple(
        position for position in range(1, len(evidence)) if rule(evidence[position])
    )


def fused_rule(s: float) -> bool:
    """Frozen detector-v2 rule: phase change OR true lexical-type switch.

    The weaker lexical->distractor signal (0.175) must NOT fire here: it
    also occurs at the last position inside an event (dev bug found and
    fixed 2026-09-25 before freezing).
    """
    return s >= BOUNDARY_RULE_PHASE or s >= BOUNDARY_RULE_LEX


def _plausibility(events, weights, regime: str) -> float:
    """Mean per-transition log-duration likelihood under learned hazard tables.

    Mean semantics (not sum): keeps hypotheses of different event counts
    comparable. A sum variant was tried in dev tuning and ABANDONED: it
    over-rewards fine segmentations because each extra pair adds
    ~-log(sd) > 0 regardless of fit (found and reverted 2026-09-25).
    """
    if len(events) < 2:
        return -1.0  # a single merged group carries no duration evidence
    total = 0.0
    for current, following in zip(events, events[1:]):
        gap = max(0.0, following.start - current.end)
        _, mean, sd = weights.hazard_stats(regime, current.event_type, following.event_type)
        sd = max(sd, MIN_SD)
        total += -0.5 * ((gap - mean) / sd) ** 2 - math.log(sd)
    return total / (len(events) - 1)


MIN_SD = 0.15


def _hypothesis_score(starts: tuple[int, ...], plausibility: float, evidence: Sequence[float]) -> float:
    """Total boundary evidence (a genuine evidence-accumulation prior: more
    boundaries must be justified by more total evidence), minus complexity."""
    bonus = BOUNDARY_BONUS * sum(evidence[position] for position in starts[1:])
    return plausibility + bonus - COMPLEXITY_PENALTY * (len(starts) - 1)


def _regime_of(observations: Sequence[Observation]) -> str:
    for observation in observations:
        regime = observation.features.get("regime")
        if regime:
            return str(regime)
    return "stable"


def _retyped_final(events: list[Event], observations: Sequence[Observation], starts: Sequence[int], parser) -> list[Event]:
    """Recency typing: the final group's prediction type is the type of its
    LAST lexical token (compiled majority as fallback when the group has no
    lexical token at all). This is what lets a merged group still predict
    from the state that actually ended."""
    if not events:
        return events
    final_start = starts[-1]
    final_group = observations[final_start:]
    recency_type = None
    for observation in reversed(final_group):
        token_type = parser.token_type(observation.token)
        if token_type is not None:
            recency_type = token_type
            break
    if recency_type is None or recency_type == events[-1].event_type:
        return events
    last = events[-1]
    retyped = Event(
        event_id=last.event_id,
        event_type=recency_type,
        start=last.start,
        end=last.end,
        source_indices=last.source_indices,
        confidence=1.0,
        regime=last.regime,
        goal=last.goal,
        effects=last.effects,
        causal_parents=last.causal_parents,
        temporal_relations=dict(last.temporal_relations),
        semantic_tags=last.semantic_tags,
        provenance=dict(last.provenance, recency_typed=True),
    )
    return events[:-1] + [retyped]


class FusedSegMind(TAECMind):
    """TAECMind with the frozen detector-v2 + recency typing (v2 operator).

    The inherited hard path stays untouched; fused prediction is an explicit
    alternative entry point so the ablation compares operators, not
    codepaths-by-accident. Banks are never written by this class.
    """

    OPERATOR = "TAECMind.v2-fusedseg"

    def fused_starts(self, observations: Sequence[Observation]) -> list[int]:
        if not observations:
            return [0]
        evidence = boundary_evidence(observations, self.compiler.parser)
        return list(_starts_from_rule(evidence, fused_rule))

    def predict_next_fused(
        self,
        observations: Sequence[Observation],
        regime: str = "stable",
        trace_id: str = "live",
        origin_id: str | None = None,
    ) -> MindPrediction:
        """Compile with fused boundaries, recency-type the final group, predict."""
        starts = self.fused_starts(observations)
        graph = self.compiler.compile(
            list(observations), trace_id=trace_id, starts=starts
        )
        events = _retyped_final(
            list(graph.events), list(observations), starts, self.compiler.parser
        )
        prediction = self.predict_next(events, regime=regime, origin_id=origin_id)
        provenance = dict(prediction.forecast.provenance)
        provenance.update(
            {
                "operator": self.OPERATOR,
                "fused_starts": [int(position) for position in starts],
                "recency_typed": bool(events) and events[-1].provenance.get("recency_typed", False),
            }
        )
        forecast = type(prediction.forecast)(
            forecast_id=prediction.forecast.forecast_id,
            origin_event_id=prediction.forecast.origin_event_id,
            horizon=prediction.forecast.horizon,
            candidates=prediction.forecast.candidates,
            mode=prediction.forecast.mode,
            created_at=prediction.forecast.created_at,
            provenance=provenance,
        )
        return MindPrediction(
            probabilities=prediction.probabilities,
            forecast=forecast,
            knowledge_ids=prediction.knowledge_ids,
            mind_status=prediction.mind_status,
        )


class SoftSegMind(TAECMind):
    """KILLED research arm (P8): n-best hypotheses + duration-plausibility
    softmax mixture. Kept exactly as tuned so the recorded ablation stays
    reproducible; NOT a candidate for solving."""

    OPERATOR = "TAECMind.v2-softseg-killed"

    def hypotheses(self, observations: Sequence[Observation]) -> list[Hypothesis]:
        if not observations:
            return [Hypothesis((0,), -1.0, 1.0)]
        evidence = boundary_evidence(observations, self.compiler.parser)
        regime = _regime_of(observations)
        candidates: list[tuple[int, ...]] = []
        # H-merge: a single merged group (the degenerate no-boundary case).
        candidates.append((0,))
        # H-anchor: production detector semantics (gap threshold OR phase change).
        candidates.append(tuple(self.compiler.detector.boundary_positions(list(observations))))
        # H-grid: fused-evidence threshold sweep (nested fine -> coarse).
        for threshold in EVIDENCE_GRID:
            candidates.append(_starts_from_rule(evidence, lambda s, t=threshold: s >= t))
        # H-lex: the fused rule (same as detector v2).
        candidates.append(_starts_from_rule(evidence, fused_rule))
        seen: set[tuple[int, ...]] = set()
        scored: list[tuple[float, tuple[int, ...]]] = []
        for starts in candidates:
            if starts in seen:
                continue
            seen.add(starts)
            graph = self.compiler.compile(list(observations), trace_id="hyp", starts=list(starts))
            plaus = _plausibility(graph.events, self.weights, regime=regime)
            scored.append((_hypothesis_score(starts, plaus, evidence), starts))
        scored.sort(key=lambda item: (-item[0], item[1]))
        top = scored[0][0] if scored else 0.0
        exponents = [TAU * (score - top) for score, _ in scored]
        denominator = sum(math.exp(value) for value in exponents) or 1.0
        return [
            Hypothesis(starts=starts, score=score, weight=math.exp(value) / denominator)
            for (score, starts), value in zip(scored, exponents)
        ]

    def predict_next_from_observations(
        self,
        observations: Sequence[Observation],
        regime: str = "stable",
        trace_id: str = "live",
        origin_id: str | None = None,
    ) -> MindPrediction:
        """Mixture of next-event forecasts over n-best segmentations."""
        hypotheses = self.hypotheses(observations)
        mixture: dict[str, float] = {label: 0.0 for label in self.labels}
        base: MindPrediction | None = None
        knowledge_ids: tuple[str, ...] = ()
        weight_entropy = 0.0
        for hypothesis in hypotheses:
            graph = self.compiler.compile(
                list(observations), trace_id=trace_id, starts=list(hypothesis.starts)
            )
            prediction = self.predict_next(graph.events, regime=regime, origin_id=origin_id)
            for label, probability in prediction.probabilities.items():
                mixture[label] += hypothesis.weight * probability
            if base is None:
                base = prediction
                knowledge_ids = prediction.knowledge_ids
        mixture = normalize(mixture, self.labels)
        for hypothesis in hypotheses:
            if hypothesis.weight > 0.0:
                weight_entropy -= hypothesis.weight * math.log(hypothesis.weight)
        assert base is not None
        candidates = [
            type(candidate)(
                event_type=candidate.event_type,
                probability=mixture[candidate.event_type],
                time_window=candidate.time_window,
                conditions=candidate.conditions,
                leading_indicators=candidate.leading_indicators,
                disconfirming_signals=candidate.disconfirming_signals,
                causal_path=candidate.causal_path,
                consequence=candidate.consequence,
                expiry=candidate.expiry,
            )
            for candidate in base.forecast.candidates
        ]
        candidates = sorted(candidates, key=lambda c: (-c.probability, c.event_type))
        provenance = dict(base.forecast.provenance)
        provenance.update(
            {
                "operator": self.OPERATOR,
                "n_hypotheses": len(hypotheses),
                "top_weight": round(hypotheses[0].weight, 6),
                "weight_entropy": round(weight_entropy, 6),
                "modal_starts": [int(position) for position in hypotheses[0].starts],
            }
        )
        forecast = type(base.forecast)(
            forecast_id=base.forecast.forecast_id,
            origin_event_id=base.forecast.origin_event_id,
            horizon=base.forecast.horizon,
            candidates=tuple(candidates),
            mode=base.forecast.mode,
            created_at=base.forecast.created_at,
            provenance=provenance,
        )
        return MindPrediction(
            probabilities=mixture,
            forecast=forecast,
            knowledge_ids=knowledge_ids,
            mind_status=self.status,
        )

    def modal_boundaries(self, observations: Sequence[Observation]) -> list[int]:
        """Boundaries of the highest-weight hypothesis (for boundary F1)."""
        hypotheses = self.hypotheses(observations)
        return [int(position) for position in hypotheses[0].starts[1:]]


# ---------------------------------------------------------------------------
# Pre-registered ablation: hard vs (killed) mixture vs v2 fused operator on
# the SAME frozen banks. Inference-only; banks are never saved here.
# ---------------------------------------------------------------------------

def _next_event_tasks(traces: list[Trace]):
    for trace in traces:
        for index in range(len(trace.truth_events) - 1):
            cutoff = trace.truth_events[index].source_indices[-1]
            observations = list(trace.observations[: cutoff + 1])
            truth = trace.truth_events[index + 1].event_type
            yield trace, observations, truth


def _boundary_truth(traces: list[Trace]) -> list[int]:
    truth: list[int] = []
    offset = 0
    for trace in traces:
        truth.extend(offset + event.source_indices[0] for event in trace.truth_events[1:])
        offset += len(trace.observations)
    return truth


def _predict_hard(mind: TAECMind, traces: list[Trace]):
    targets: list[str] = []
    predictions: list[dict[str, float]] = []
    boundaries: list[int] = []
    offset = 0
    for trace, observations, truth in _next_event_tasks(traces):
        graph = mind.compile(observations, trace_id=trace.trace_id)
        result = mind.predict_next(graph.events, regime=trace.regime)
        targets.append(truth)
        predictions.append(result.probabilities)
    for trace in traces:
        graph = mind.compile(trace.observations, trace_id=trace.trace_id)
        boundaries.extend(offset + event.source_indices[0] for event in graph.events[1:])
        offset += len(trace.observations)
    return targets, predictions, boundaries


def _predict_soft(mind: SoftSegMind, traces: list[Trace]):
    targets: list[str] = []
    predictions: list[dict[str, float]] = []
    boundaries: list[int] = []
    offset = 0
    for trace, observations, truth in _next_event_tasks(traces):
        result = mind.predict_next_from_observations(
            observations, regime=trace.regime, trace_id=trace.trace_id
        )
        targets.append(truth)
        predictions.append(result.probabilities)
    for trace in traces:
        boundaries.extend(offset + position for position in mind.modal_boundaries(trace.observations))
        offset += len(trace.observations)
    return targets, predictions, boundaries


def _predict_fused(mind: FusedSegMind, traces: list[Trace]):
    targets: list[str] = []
    predictions: list[dict[str, float]] = []
    boundaries: list[int] = []
    offset = 0
    for trace, observations, truth in _next_event_tasks(traces):
        result = mind.predict_next_fused(
            observations, regime=trace.regime, trace_id=trace.trace_id
        )
        targets.append(truth)
        predictions.append(result.probabilities)
    for trace in traces:
        boundaries.extend(offset + position for position in mind.fused_starts(trace.observations)[1:])
        offset += len(trace.observations)
    return targets, predictions, boundaries


def run_softseg_eval(
    dev_seed_start: int = DEV_SEED_START,
    eval_seed_start: int = EVAL_SEED_START,
    n_dev: int = 24,
    n_eval: int = 24,
    difficulty: str = "hard",
    brain_dir: str | Path | None = None,
    report_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Three-arm ablation with pre-registered gates A1-A3 on the untouched
    eval split, scored for the v2 fused operator (the adoption candidate)."""
    mind = TAECMind(brain_dir=brain_dir) if brain_dir else TAECMind()
    soft = SoftSegMind(brain_dir=mind.brain_dir)
    fused = FusedSegMind(brain_dir=mind.brain_dir)

    started = time.perf_counter()
    dev = build_dataset(n_dev, seed_start=dev_seed_start,
                        regimes=("stable", "stressed", "drift"), difficulty=difficulty)
    evaluation = build_dataset(n_eval, seed_start=eval_seed_start,
                               regimes=("stable", "stressed", "drift"), difficulty=difficulty)

    def _arm(split):
        hard_t, hard_p, hard_b = _predict_hard(mind, split)
        mix_t, mix_p, mix_b = _predict_soft(soft, split)
        v2_t, v2_p, v2_b = _predict_fused(fused, split)
        hard_metrics = summarize_classification(hard_t, hard_p, LABELS)
        mix_metrics = summarize_classification(mix_t, mix_p, LABELS)
        v2_metrics = summarize_classification(v2_t, v2_p, LABELS)
        truth_b = _boundary_truth(split)
        hard_metrics["boundary"] = boundary_f1(truth_b, hard_b)
        mix_metrics["boundary"] = boundary_f1(truth_b, mix_b)
        v2_metrics["boundary"] = boundary_f1(truth_b, v2_b)
        return {"hard": hard_metrics, "softmix": mix_metrics, "v2_fused": v2_metrics}

    dev_arm = _arm(dev)
    eval_arm = _arm(evaluation)
    elapsed = time.perf_counter() - started

    def _delta(key: str) -> float:
        return eval_arm["v2_fused"][key] - eval_arm["hard"][key]

    gates = {
        "A1_v2_acc_gt_hard": _delta("accuracy") > 0.0,
        "A2_v2_boundary_f1_gt_hard": (
            eval_arm["v2_fused"]["boundary"]["f1"] > eval_arm["hard"]["boundary"]["f1"]
        ),
        "A3_v2_logloss_beats_or_within_slack": (
            _delta("log_loss") <= GATE_LOGLOSS_SLACK
        ),
    }
    report: dict[str, Any] = {
        "status": "PROTOCOL_TEST_ONLY",
        "claim_scope": "inference-time operator ablation on frozen banks; synthetic only",
        "operator": FusedSegMind.OPERATOR,
        "killed_arm": SoftSegMind.OPERATOR,
        "config": {
            "dev_seed_start": dev_seed_start, "eval_seed_start": eval_seed_start,
            "n_dev": n_dev, "n_eval": n_eval, "difficulty": difficulty,
            "brain_dir": str(mind.brain_dir), "weights_updates": mind.weights.meta.get("updates", 0),
        },
        "dev_split": dev_arm,
        "eval_split": eval_arm,
        "gates": gates,
        "verdict": "PASS" if all(gates.values()) else "FAIL",
        "kill_condition": (
            "if verdict FAIL: v2 operator DISABLED for solving (research-only); "
            "hard detector remains default; roll back is trivial because banks are untouched"
        ),
        "cost": {
            "wall_seconds_total": round(elapsed, 3),
            "v2_extra_cost": "one fused-evidence pass + one retyped prediction per task",
        },
    }
    if report_dir is not None:
        directory = Path(report_dir)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "softseg-ablation.json").write_text(
            json.dumps(to_dict(report), indent=2, sort_keys=True), encoding="utf-8")
        (directory / "softseg-ablation.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TAEC Lab — Soft Segmentation Ablation (phase 4)",
        "",
        "> STATUS: PROTOCOL_TEST_ONLY. Inference-time operator ablation on frozen banks.",
        "",
        f"- Candidate: `{report['operator']}` (killed arm kept for the record: `{report['killed_arm']}`)",
        f"- Verdict: **{report['verdict']}**",
        "",
        "| gate | result |",
        "|---|:---:|",
    ]
    for gate, passed in report["gates"].items():
        lines.append(f"| {gate} | {'✅' if passed else '❌'} |")
    for split in ("dev_split", "eval_split"):
        arm = report[split]
        lines += [
            "",
            f"## {split}",
            "",
            "| arm | accuracy | log loss | Brier | ECE | boundary F1 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for name in ("hard", "softmix", "v2_fused"):
            metrics = arm[name]
            lines.append(
                f"| {name} | {metrics['accuracy']:.6f} | {metrics['log_loss']:.6f} | "
                f"{metrics['brier']:.6f} | {metrics['ece']:.6f} | {metrics['boundary']['f1']:.6f} |"
            )
    lines += [
        "",
        "## Reading",
        "",
        "- Same banks, same traces; only the segmentation/typing operator differs.",
        "- The n-best duration-plausibility mixture was KILLED in dev tuning: it never",
        "  rescued a wrong anchor and its softmax flattening taxed log-loss; the bank's",
        "  hazard durations conflate easy/hard gap regimes, biasing toward merged hypotheses.",
        "- The surviving v2 operator is simpler: fused-evidence boundaries + recency typing.",
        "- PASS unlocks a sealed held-out attempt; FAIL disables the operator (kill condition).",
        "- Still synthetic: no capability claim is licensed by this table.",
    ]
    return "\n".join(lines) + "\n"
