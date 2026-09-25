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
- open: `ECE-vs-uniform is a degenerate comparison (uniform is trivially calibrated at acc≈1/7); read ECE only jointly with accuracy. Soft/boundary-uncertain segmentation is the next bottleneck.`
- claim_scope: `synthetic protocol + sealed synthetic held-out; no model-weight or consciousness claim`
