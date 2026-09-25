# TAEC Lab — Sealed Held-Out Verdict

- Solver: `mind:WARM`
- Seal: `OK`
- Next-event tasks: `156`
- Verdict: **PASS**

| condition | accuracy | log loss | Brier | ECE |
|---|---:|---:|---:|---:|
| cold uniform | 0.121795 | 1.945910 | 0.857143 | 0.021062 |
| solver | 0.512821 | 1.267470 | 0.628915 | 0.148376 |
| delta | +0.391026 | +0.678441 | +0.228228 | -0.127314 |

| gate | result |
|---|:---:|
| G1_seal_ok | ✅ |
| G2_acc_beats_cold | ✅ |
| G3_logloss_beats_cold | ✅ |
| G4_boundary_f1_ge_050 | ✅ |

Boundary F1: **0.9388** (P=1.0000, R=0.8846)

## Reading

- The solver never saw held-out truths; the seal proves the truths file is intact.
- PASS means transfer to a disjoint seed range under pre-registered gates.
- Still synthetic: the next gate after this is non-synthetic task families.
