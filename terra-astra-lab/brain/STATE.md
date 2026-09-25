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
- open: `ECE-vs-uniform is a degenerate comparison (uniform is trivially calibrated at acc≈1/7); read ECE only jointly with accuracy. Typing accuracy still ~0.53: transition-statistic saturation under corruption is the remaining bottleneck — next frontier is corruption-robust typing features and a compositional held-out (novel tokens/regime mixes).`
- claim_scope: `synthetic protocol + sealed synthetic held-out; no model-weight or consciousness claim`
