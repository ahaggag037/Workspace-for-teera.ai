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
5. Boundary-uncertainty-aware prediction (soft segmentation / n-best boundaries) — current bottleneck.
6. Compositional held-out: novel tokens and novel regime mixes never seen in training.
7. First non-synthetic task family (e.g. log-like or tool-trace prediction) before any model-runner claim.
3. Add explicit counterfactual/intervention branches (F4–F5).
4. Add early-warning regime-shift fixtures (F6).
5. Add prospective-memory cue/expiry fixtures (F8).
6. Add a model-runner adapter only after deterministic protocol passes.
7. Compare TAEC v0, COK/RCC ablations, and Event Compiler conditions.

## Kill conditions

- Do not merge an operator that fails held-out or increases cost by >25% without a pre-registered utility gain.
- Do not claim capability from synthetic or mock traces.
- Disable successor maps on detected regime drift until a drift-conditioned variant passes.
