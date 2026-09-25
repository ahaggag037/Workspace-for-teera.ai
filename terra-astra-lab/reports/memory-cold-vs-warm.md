# TAEC Lab — Cold Start vs Warm Memory

> STATUS: PROTOCOL_TEST_ONLY. Synthetic transfer of workspace-side memory only.

- Seed: `20260924`
- Train: `40` traces
- Test: `20` traces
- Lessons stored: `14`

| condition | accuracy | log loss | Brier | ECE |
|---|---:|---:|---:|---:|
| cold (no memory) | 0.096154 | 1.945910 | 0.857143 | 0.046703 |
| warm (external memory) | 0.488462 | 1.614264 | 0.603741 | 0.032677 |
| delta (warm-cold, +good except logloss/brier/ece shown as cold-warm) | +0.392308 | +0.331646 | +0.253402 | +0.014027 |

## Reading

- Positive delta means the saved workspace banks helped on unseen synthetic traces.
- This is external-memory learning, not a change to model weights.
- Held-out confirmation with an independent evaluator is still required.
