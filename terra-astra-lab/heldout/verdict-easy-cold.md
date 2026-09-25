# TAEC Lab — Sealed Held-Out Verdict

- Solver: `cold-uniform`
- Seal: `OK`
- Next-event tasks: `156`
- Verdict: **FAIL**

| condition | accuracy | log loss | Brier | ECE |
|---|---:|---:|---:|---:|
| cold uniform | 0.083333 | 1.945910 | 0.857143 | 0.059524 |
| solver | 0.083333 | 1.945910 | 0.857143 | 0.059524 |
| delta | +0.000000 | +0.000000 | +0.000000 | +0.000000 |

| gate | result |
|---|:---:|
| G1_seal_ok | ✅ |
| G2_acc_beats_cold | ❌ |
| G3_logloss_beats_cold | ❌ |
| G4_boundary_f1_ge_050 | ✅ |

Boundary F1: **1.0000** (P=1.0000, R=1.0000)

## Reading

- The solver never saw held-out truths; the seal proves the truths file is intact.
- PASS means transfer to a disjoint seed range under pre-registered gates.
- Still synthetic: the next gate after this is non-synthetic task families.
