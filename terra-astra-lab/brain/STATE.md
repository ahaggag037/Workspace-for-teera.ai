# TAEC Mind — State

- status: `WARM`
- weights: `WEIGHTS.json` — updates=2, train_traces=80 (40 easy + 40 hard), seeds=[20260924, 20270001]
- knowledge: `KNOWLEDGE.jsonl` — 14 lessons, credit-applied (156 dev predictions, acc=0.513, reliability 0.29–0.86)
- inference: `TAECMind.v1` + Laplace smoothing + P5 humility flattening
- multiseed_easy: `PASS 3/3` — dAcc=+0.432, dLL=+0.754, dBrier=+0.257
- multiseed_hard: `PASS 3/3 (accuracy gate)` — dAcc=+0.162, dLL=−0.044, dBrier=+0.027
- heldout_easy: `PASS 4/4 gates` — acc=0.442 vs cold 0.083, F1=1.000, seal OK
- heldout_hard: `PASS 4/4 gates` — acc=0.513 vs cold 0.122, F1=0.939, seal OK
- incremental_hard: `FLAT` — v2 acc 0.513 vs v1 0.519; bottleneck moved to segmentation
- softseg_phase4: `RESOLVED / SEALED PASS` — operator `TAECMind.v2-fusedseg`
  (fused-evidence boundaries + recency typing); n-best duration-plausibility
  mixture arm KILLED in dev (never rescued a wrong anchor: 6 correct→wrong
  vs 0 wrong→correct flips; bank hazard durations conflate easy/hard gap
  regimes and bias toward merged hypotheses)
- softseg_ablation: `PASS A1-A3` on untouched eval split (seeds 20510924..):
  v2 acc 0.5032 vs hard 0.4679 (+0.0353), dLL −0.0676, bF1 0.9903 vs 0.9495
- heldout_pack_v2 (seeds 999601..999612, seal OK): `PASS 4/4 gates`
  — fusedseg-v2 acc=0.5321 vs cold 0.1410, dLL=−0.7628, bF1=0.9903;
  vs production hard detector: dAcc=+0.0321, dLL=−0.0538, dbF1=+0.0373
- banks: UNCHANGED by phase 4 (inference-time operator only; ablation ran
  on the same frozen banks; updates=2, 14 lessons)
- realtrace_pilot (phase 5, 2026-09-25): `PASS on pre-registered gates R1-R3`
  — first NON-SYNTHETIC task family. Ledger: telemetry/worklog.jsonl (42 real
  session events, artifact-corroborated). Temporal 60/40 split (25/17).
  real_learned acc 0.3529 / ll 1.8375 beats freq_prior 0.0588 / 1.9082.
  NEGATIVE FINDING: synth_zero_shot (acc 0.0588, ll 2.1889) did NOT transfer
  to real traces (R4 false) — the synthetic world's grammar is not the real
  work-stream's grammar; real-session brains are now mandatory for ops tasks.
  CAVEAT: uniform arm degenerates to "always create" via alphabetical
  tie-break (acc 0.4706) — real_learned beats it on log-loss/Brier but not
  accuracy; add a train-majority constant baseline arm in future evals.
- open: `ECE-vs-uniform is a degenerate comparison (uniform is trivially calibrated at acc≈1/7); read ECE only jointly with accuracy. Typing accuracy still ~0.53: transition-statistic saturation under corruption is the remaining bottleneck — next frontier is corruption-robust typing features and a compositional held-out (novel tokens/regime mixes).`
- ops_brain (phase 6, 2026-09-25): `LIVE` — persistent phase-conditioned
  brain at `brain-ops/ops-brain.json` (49 transitions, 17 pair keys, updates=1)
- realtrace_pilot_v2: `PASS on primary gates R5/R6` — phase_markov acc 0.3500 /
  ll 1.7087 beats constant train prior acc 0.0000 / ll 1.7977. R7 tie (acc =
  markov), R8 slight loss (ll 1.7087 vs 1.7068): phase conditioning NOT yet
  proven at n=50 — arms stay separated. markov/phase_markov are the best
  calibrated arms by proper scoring; the always-create artifact (uniform,
  acc 0.5500) wins raw accuracy only via train→test distribution shift
  (observe-heavy train, create-heavy test)
- self_audit (2026-09-25, INTROSPECTION_ONLY): found+fixed live defect
  (ops-learn idempotency; 108->59 transitions, regression test, 34/34);
  operator profile: failure incidence 2/7, fail->fix latency 1.3 events,
  0 protocol violations; full dialogue + ranked needs in reports/self-audit.md;
  next gate proposed: pre-registered operator self-eval loop
- open_real: `accumulate live rows (ops-learn after bursts); re-run worklog-eval when n_test >= 25; add wall-clock timestamps; then decide whether phase_markov replaces markov as the ops-forecast operator; ops-forecast is advisory, never an instruction.`
- claim_scope: `synthetic protocol + sealed synthetic held-out + PILOT-scale real-trace PASS; no model-weight or consciousness claim`
