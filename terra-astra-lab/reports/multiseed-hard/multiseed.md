# TAEC Lab — Multi-Seed Memory Transfer

> STATUS: PROTOCOL_TEST_ONLY. Synthetic transfer across disjoint seeds.

- Seeds: `[20260924, 424242, 777777]` (k=3)
- Train/test: `40/20`
- Difficulty: `hard`
- Consistency: `3/3` → **PASS**

## Aggregate delta (warm − cold; + means memory helped)

| metric | mean | sd | min | max | ±95% CI |
|---|---:|---:|---:|---:|---:|
| accuracy | +0.161538 | 0.015702 | +0.142308 | +0.180769 | 0.017768 |
| log_loss | -0.044319 | 0.028352 | -0.067658 | -0.004415 | 0.032083 |
| brier | +0.027218 | 0.005793 | +0.019419 | +0.033291 | 0.006556 |
| ece | -0.040981 | 0.015467 | -0.051994 | -0.019107 | 0.017503 |

## Per-seed accuracy (cold → warm)

| seed | cold | warm | delta |
|---|---:|---:|---:|
| 20260924 | 0.0923 | 0.2538 | +0.1615 |
| 424242 | 0.0615 | 0.2423 | +0.1808 |
| 777777 | 0.0962 | 0.2385 | +0.1423 |

## Reading

- PASS requires warm to beat cold on accuracy in every seed.
- This rules out single-seed luck, not synthetic-world bias.
- The sealed held-out pack is the next independent gate.
