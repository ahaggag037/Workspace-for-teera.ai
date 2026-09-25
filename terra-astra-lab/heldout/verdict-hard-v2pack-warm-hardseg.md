# TAEC Lab — Sealed Held-Out Verdict

- Solver: `mind:WARM`
- Seal: `OK`
- Next-event tasks: `156`
- Verdict: **PASS**

| condition | accuracy | log loss | Brier | ECE |
|---|---:|---:|---:|---:|
| cold uniform | 0.141026 | 1.945910 | 0.857143 | 0.001832 |
| solver | 0.500000 | 1.236941 | 0.621147 | 0.146815 |
| delta | +0.358974 | +0.708969 | +0.235996 | -0.144984 |

| gate | result |
|---|:---:|
| G1_seal_ok | ✅ |
| G2_acc_beats_cold | ✅ |
| G3_logloss_beats_cold | ✅ |
| G4_boundary_f1_ge_050 | ✅ |

Boundary F1: **0.9530** (P=1.0000, R=0.9103)

## Reading

- The solver never saw held-out truths; the seal proves the truths file is intact.
- PASS means transfer to a disjoint seed range under pre-registered gates.
- Still synthetic: the next gate after this is non-synthetic task families.
