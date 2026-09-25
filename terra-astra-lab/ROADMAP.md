# TAEC Lab Roadmap

## Completed in this slice

- [x] Isolated lab outside Fawri.
- [x] Typed event/forecast/residual/pathway contracts.
- [x] Boundary detector and EventGraph.
- [x] Raw-token and event-transition baselines.
- [x] Dependency-free successor representation primitive.
- [x] Basic hazard/time-window model.
- [x] Proper-score and calibration metrics.
- [x] Synthetic F1–F3 protocol and deterministic tests.
- [x] First actual protocol run with report artifacts and no Fawri changes.

## Next gates

1. ~~Persist banks across runs~~ DONE — `brain/` is WARM with 14 lessons.
2. ~~Sealed evaluator + independent held-out pack~~ DONE — easy + hard packs, seal-verified, warm PASS 4/4 on both.
3. ~~Three seeds with confidence intervals~~ DONE — multiseed easy/hard, PASS 3/3 on accuracy with full deltas.
4. ~~Lesson credit assignment~~ DONE — `credit --apply` persists use/success per lesson.
5. ~~Boundary-uncertainty-aware prediction (soft segmentation)~~ DONE (2026-09-25) —
   `TAECMind.v2-fusedseg`: fused-evidence boundaries + recency typing;
   dev-tuned, eval-split PASS, sealed pack-hard-v2 PASS 4/4 with
   dAcc +0.0321 / dLL −0.0538 / dbF1 +0.0373 vs the hard detector.
   The n-best duration-plausibility mixture arm was killed in dev (P8).
6. Compositional held-out: novel tokens and novel regime mixes never seen in training.
7. Corruption-robust typing: accuracy (~0.53) is now bounded by transition
   statistics under corruption, not boundaries — richer observation
   features or type marginalization inside merged groups.
8. First non-synthetic task family — **PILOT STARTED (2026-09-25)**: real
   work-event ledger (`telemetry/worklog.jsonl` + `worklog-record` live tap)
   and `worklog-eval` pilot PASSED its pre-registered gates (real_learned
   beats freq_prior; zero-shot synthetic transfer FAILED and was recorded).
   Next: accumulate live rows across turns, add train-majority constant
   baseline, record wall-clock time, then re-evaluate.
3. Add explicit counterfactual/intervention branches (F4–F5).
4. Add early-warning regime-shift fixtures (F6).
5. Add prospective-memory cue/expiry fixtures (F8).
6. Add a model-runner adapter only after deterministic protocol passes.
7. Compare TAEC v0, COK/RCC ablations, and Event Compiler conditions.

## Kill conditions

- Do not merge an operator that fails held-out or increases cost by >25% without a pre-registered utility gain.
- Do not claim capability from synthetic or mock traces.
- Disable successor maps on detected regime drift until a drift-conditioned variant passes.
