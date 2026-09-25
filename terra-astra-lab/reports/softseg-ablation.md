# TAEC Lab — Soft Segmentation Ablation (phase 4)

> STATUS: PROTOCOL_TEST_ONLY. Inference-time operator ablation on frozen banks.

- Candidate: `TAECMind.v2-fusedseg` (killed arm kept for the record: `TAECMind.v2-softseg-killed`)
- Verdict: **PASS**

| gate | result |
|---|:---:|
| A1_v2_acc_gt_hard | ✅ |
| A2_v2_boundary_f1_gt_hard | ✅ |
| A3_v2_logloss_beats_or_within_slack | ✅ |

## dev_split

| arm | accuracy | log loss | Brier | ECE | boundary F1 |
|---|---:|---:|---:|---:|---:|
| hard | 0.503205 | 1.254540 | 0.620733 | 0.145014 | 0.954774 |
| softmix | 0.490385 | 1.267209 | 0.629090 | 0.142642 | 0.975369 |
| v2_fused | 0.519231 | 1.179677 | 0.597713 | 0.159387 | 0.990291 |

## eval_split

| arm | accuracy | log loss | Brier | ECE | boundary F1 |
|---|---:|---:|---:|---:|---:|
| hard | 0.467949 | 1.257778 | 0.628628 | 0.106348 | 0.949495 |
| softmix | 0.455128 | 1.279159 | 0.636011 | 0.112603 | 0.963455 |
| v2_fused | 0.503205 | 1.190225 | 0.603624 | 0.139800 | 0.990291 |

## Reading

- Same banks, same traces; only the segmentation/typing operator differs.
- The n-best duration-plausibility mixture was KILLED in dev tuning: it never
  rescued a wrong anchor and its softmax flattening taxed log-loss; the bank's
  hazard durations conflate easy/hard gap regimes, biasing toward merged hypotheses.
- The surviving v2 operator is simpler: fused-evidence boundaries + recency typing.
- PASS unlocks a sealed held-out attempt; FAIL disables the operator (kill condition).
- Still synthetic: no capability claim is licensed by this table.
