# TAEC Lab — Sealed Held-Out Verdict

- Solver: `mind:WARM+fusedseg-v2`
- Seal: `OK`
- Next-event tasks: `156`
- Verdict: **PASS**

| condition | accuracy | log loss | Brier | ECE |
|---|---:|---:|---:|---:|
| cold uniform | 0.141026 | 1.945910 | 0.857143 | 0.001832 |
| solver | 0.532051 | 1.183125 | 0.601975 | 0.178505 |
| delta | +0.391026 | +0.762785 | +0.255168 | -0.176673 |

| gate | result |
|---|:---:|
| G1_seal_ok | ✅ |
| G2_acc_beats_cold | ✅ |
| G3_logloss_beats_cold | ✅ |
| G4_boundary_f1_ge_050 | ✅ |

Boundary F1: **0.9903** (P=1.0000, R=0.9808)

## Reading

- The solver never saw held-out truths; the seal proves the truths file is intact.
- PASS means transfer to a disjoint seed range under pre-registered gates.
- Still synthetic: the next gate after this is non-synthetic task families.
