# TAEC Lab — F1–F3 Protocol Report

> STATUS: PROTOCOL_TEST_ONLY. This is synthetic evidence for implementation debugging, not capability evidence.

- Seed: `20260924`
- Train traces: `40`
- Test traces: `20`
- Held-out status: `NOT_RUN`

## Boundary detection (F1)

| metric | value |
|---|---:|
| precision | 1.000000 |
| recall | 1.000000 |
| f1 | 1.000000 |

## Next-event forecasting

| condition | accuracy | log loss | Brier | ECE |
|---|---:|---:|---:|---:|
| raw_token | 0.426923 | 3.839456 | 0.652980 | 0.184302 |
| event_transition | 0.488462 | 3.793399 | 0.611284 | 0.095785 |
| successor_representation | 0.446154 | 3.083574 | 0.749630 | 0.158133 |

## Hazard/time-to-event

| metric | value |
|---|---:|
| n | 260.000000 |
| type_accuracy | 0.442308 |
| mean_absolute_time_error | 0.082859 |
| time_window_coverage | 0.750000 |

## Interpretation

- This run validates that the protocol, contracts, traces, and scoring path execute end-to-end.
- It does not prove generalization, consciousness, self-improvement, or superiority of COK/RCC.
- A real held-out evaluator and multi-seed confirmation are still required.
