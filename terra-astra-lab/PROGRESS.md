# TAEC Lab Progress

## 2026-09-25 — phase 5: first REAL-trace task family (worklog tap + pilot PASS with honest caveats)

Status: `WARM / PILOT_REAL_TRACE (worklog.jsonl, pre-registered gates)`

The lab crossed the synthetic boundary. Roadmap gate #8 (first half) is now
started: a REAL, non-synthetic task family — the agent's own work stream.

Built (all real, stdlib-only, deterministic):

- `telemetry/worklog.jsonl`: append-only ledger of REAL work events
  (42 rows from the phase-4 session, each corroborated by an artifact or
  git ref; failures included). New rows append live via
  `python -m taec_lab.cli worklog-record` (now part of BOOT protocol step 6).
- `taec_lab/realtrace.py`: deterministic verb→7-type ontology lexicon
  (OPS_LEXICON), observation adapter (sequence time; wall time not recorded
  this session), temporal 60/40 split, four pre-registered arms
  (uniform / freq_prior / synth_zero_shot / real_learned) and gates
  R1-R4 written BEFORE the first eval run.
- Pilot result (17-point test segment): real_learned acc 0.3529 /
  ll 1.8375 beats freq_prior acc 0.0588 / ll 1.9082 → R2+R3 PASS.
- NEGATIVE FINDING (recorded as such): synth_zero_shot acc 0.0588 /
  ll 2.1889 — the synthetic banks do NOT transfer zero-shot to real work
  streams (R4 false). Real-session brains are now mandatory for ops tasks;
  this is exactly the failure mode real pilots exist to expose.
- CAVEAT (recorded, not patched post-hoc): the uniform arm degenerates to
  "always create" via alphabetical tie-break (acc 0.4706); real_learned
  beats it on log-loss (1.84 vs 1.95) and Brier but not accuracy. Next eval
  adds a pre-registered train-majority constant baseline arm.
- Tests: 26/26 green (4 new real-trace tests incl. fixture-ledger
  INCONCLUSIVE path and synthetic-brain isolation).

Honesty: pilot scale, one session, small-n — directional, not confirmatory.
The synthetic brain remains the only brain for the synthetic protocol;
real-trace learning uses a separate temp brain and never writes the
synthetic banks.

## 2026-09-25 — phase 4: soft segmentation resolved via fused-evidence boundaries + recency typing

Status: `WARM / HELDOUT_PASS (pack-hard-v2, sealed)`

Goal (from roadmap #5): boundary-uncertainty-aware prediction, because
incremental hard learning was FLAT and the bottleneck was segmentation
under corruption. Tuning happened on dev seeds 20500924.. ONLY; the eval
split (20510924..) and the sealed pack (999601..) were untouched until the
operator was frozen.

What ran (all real, stdlib-only, deterministic; banks unchanged):

- n-best mixture arm (`TAECMind.v2-softseg-killed`): KILLED in dev. It
  never rescued a wrong anchor (6 correct→wrong vs 0 wrong→correct flips)
  and its softmax flattening taxed log-loss. Root cause: the bank's hazard
  duration tables conflate easy/hard gap regimes, so merged hypotheses fit
  the learned durations better than the true segmentation. Also tried and
  killed: transition-likelihood plausibility (merged typing still yields
  plausible transitions).
- surviving v2 operator (`TAECMind.v2-fusedseg`), simpler than what it
  replaced: per-position fused evidence (gap + phase + lexicon-switch) with
  the frozen rule "phase change OR true lexical-type switch", plus recency
  typing (the final group's prediction type = type of its last lexical
  token, so a merged group still predicts from the state that ended).
- `softseg-eval` (pre-registered gates A1–A3, untouched eval split): PASS.
  v2 acc 0.5032 vs hard 0.4679 (+0.0353), log-loss 1.1902 vs 1.2578
  (−0.0676), boundary F1 0.9903 vs 0.9495. Dev split agrees (acc +0.016,
  dLL −0.075, bF1 +0.036).
- Sealed `heldout/pack-hard-v2` (12 traces, 156 next-event tasks, seeds
  999601..999612, sha256 seal verified): `mind:WARM+fusedseg-v2` PASS 4/4 —
  acc 0.5321 vs cold 0.1410 (dAcc +0.3910, dLL −0.7628), bF1 0.9903.
  Against the production hard detector on the same sealed pack:
  dAcc +0.0321, dLL −0.0538, dbF1 +0.0373.
- Tests: 22/22 green (8 new phase-4 tests, incl. fixed-seed dominance
  regression and a sealed-pack solve round-trip).

Failures found and fixed (the loop working as designed):

1. Sum-semantics duration likelihood over-rewarded fine segmentations
   (each extra pair adds ~−log(sd) > 0 regardless of fit) → reverted to
   mean semantics with an evidence-accumulation boundary bonus.
2. The H-lex rule fired on lexical→distractor inside events (the last
   offset can be a distractor 15% of the time) → restricted the rule to
   true lexical-type switches.
3. The mixture's plausibility signal itself was the problem: the bank's
   hazard durations mix easy (1.0–1.25) and hard (0.2–0.4) gap regimes, so
   merged hypotheses scored as MORE plausible than the truth. Killing the
   arm and replacing the signal (lexical evidence + recency typing) was
   the fix, not more tuning.

Standing cautions:

- Boundary F1 for the cold baseline is already ~0.95 on this world, so
  boundary gains saturate near 0.99; accuracy (~0.53) is now limited by
  transition statistics under corruption, not boundaries.
- All gates remain synthetic; next frontier is a compositional held-out
  (novel tokens / regime mixes) and then a non-synthetic task family.

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
