# TAEC Lab — Multi-Seed Memory Transfer

> STATUS: PROTOCOL_TEST_ONLY. Synthetic transfer across disjoint seeds.

- Seeds: `[20260924, 424242, 777777]` (k=3)
- Train/test: `40/20`
- Difficulty: `easy`
- Consistency: `3/3` → **PASS**

## Aggregate delta (warm − cold; + means memory helped)

| metric | mean | sd | min | max | ±95% CI |
|---|---:|---:|---:|---:|---:|
| accuracy | +0.432051 | 0.062912 | +0.373077 | +0.519231 | 0.071192 |
| log_loss | +0.753689 | 0.025827 | +0.724147 | +0.787061 | 0.029226 |
| brier | +0.257079 | 0.011865 | +0.244243 | +0.272857 | 0.013427 |
| ece | -0.072232 | 0.043861 | -0.122841 | -0.015867 | 0.049634 |

## Per-seed accuracy (cold → warm)

| seed | cold | warm | delta |
|---|---:|---:|---:|
| 20260924 | 0.0731 | 0.4462 | +0.3731 |
| 424242 | 0.0615 | 0.5808 | +0.5192 |
| 777777 | 0.1000 | 0.5038 | +0.4038 |

## Reading

- PASS requires warm to beat cold on accuracy in every seed.
- This rules out single-seed luck, not synthetic-world bias.
- The sealed held-out pack is the next independent gate.
