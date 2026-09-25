# TAEC Lab Progress

## 2026-09-24 — phase 3: hardness, multiseed, sealed held-out, self-grading bank

Status: `WARM / HELDOUT_PASS (synthetic, sealed)`

What ran (all real, stdlib-only, deterministic):

- `multiseed easy` (3 seeds, 40/20): PASS 3/3 — dAcc +0.432, dLL +0.754, dBrier +0.257.
- `multiseed hard` (3 seeds, 40/20): PASS 3/3 on accuracy — dAcc +0.162, dBrier +0.027, dLL −0.044.
- `heldout easy pack` (disjoint seeds 999001.., seal OK): warm-v1 PASS 4/4 — acc 0.442 vs 0.083, F1 1.000.
- `heldout hard pack` (seal OK): warm-v1 PASS 4/4 — acc 0.519 vs 0.122, F1 0.939.
- `incremental hard learn` (updates=2, 80 traces): hard-v2 PASS 4/4 — acc 0.513, dLL +0.678; FLAT vs v1.
- `credit --apply`: 156 dev predictions, 14/14 lessons graded (reliability 0.29–0.86), counts persisted.
- Tests: 14/14 green, including a tie-break regression test.

Failures found and fixed (the loop working as designed):

1. Hard mode exposed unsmoothed zero probabilities → log-loss catastrophe (−6.8). Fixed with Laplace smoothing.
2. Exposed sharp-but-wrong-state overconfidence → added P5 humility flattening (support + event-confidence driven).
3. Found JSON `sort_keys` changing argmax tie-breaks → order-independent alphabetical tie-break + regression test.
4. Incremental hard training went FLAT → honest conclusion: the bottleneck is now segmentation under corruption,
   not transition statistics. Next gate: boundary-uncertainty-aware prediction (soft segmentation).

Standing cautions:

- ECE-vs-uniform is degenerate (uniform is trivially calibrated near acc≈1/7); ECE is reported but never used alone.
- All gates are still synthetic; the next frontier is non-synthetic task families, then a model-runner adapter.

## 2026-09-24 — external mind (weights + knowledge bank)

Status: `WARM / PROTOCOL_RAN`

The lab now persists learning across runs in workspace-side banks:

- `brain/WEIGHTS.json`: transition counts, successor matrix, hazard durations.
- `brain/KNOWLEDGE.jsonl`: 14 transition lessons with confidence/use tracking.
- `brain/BOOT.md`, `brain/POLICIES.md`, `brain/STATE.md`: auto-load protocol.
- `/home/user/TAEC-MIND.md`: root pointer so every future turn boots the Mind first.

Executed:

- `python -m unittest discover -s tests -v` → 9 tests passed.
- `python -m taec_lab.cli learn --seed 20260924 --train 40` → WARM, 14 lessons.
- `python -m taec_lab.cli memory-eval` → cold acc 0.096 → warm acc 0.488 (Δ +0.392),
  Brier Δ +0.253, log-loss Δ +0.332, ECE Δ +0.014 on 260 unseen predictions.

Scope: synthetic external-memory transfer only. Model weights unchanged;
behavior changes via workspace banks. Held-out still `NOT_RUN`.

## 2026-09-24 — first vertical slice

Status: `IMPLEMENTED / PROTOCOL_RAN`

Implemented contracts, Event Compiler, EventGraph, raw/event/successor baselines, hazard model, scoring, synthetic event world, CLI, and deterministic tests.

Executed:

- `python -m unittest discover -s tests -v` → 6 tests passed.
- `python -m taec_lab.cli protocol --seed 20260924 --train 40 --test 20` → completed; report written to `reports/protocol-f1-f3.{json,md}`.

The run is `PROTOCOL_TEST_ONLY`; held-out status remains `NOT_RUN`.

Scope: synthetic implementation protocol only. No model weights, no Fawri changes, no held-out capability claim.
