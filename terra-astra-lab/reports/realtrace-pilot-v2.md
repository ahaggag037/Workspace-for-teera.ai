# TAEC Lab — Real-Trace Pilot (phase 5)

> STATUS: PILOT_REAL_TRACE. First non-synthetic task family; small-n by design.

- Verdict: **PASS**
- Ledger: `/home/user/Workspace-for-teera.ai/terra-astra-lab/telemetry/worklog.jsonl` — 50 real events (train 30 / test 20)

| arm | accuracy | log loss | Brier | ECE |
|---|---:|---:|---:|---:|
| uniform | 0.550000 | 1.945910 | 0.857143 | 0.407143 |
| freq_prior | 0.000000 | 1.797700 | 0.854931 | 0.378378 |
| synth_zero_shot | 0.150000 | 2.171866 | 0.921855 | 0.108887 |
| real_learned | 0.350000 | 1.834885 | 0.821113 | 0.215761 |
| markov | 0.350000 | 1.706772 | 0.776674 | 0.131201 |
| phase_markov | 0.350000 | 1.708696 | 0.779428 | 0.133423 |

| gate | result |
|---|:---:|
| R1_min_test | ✅ |
| R2_real_acc_gt_freq_legacy | ✅ |
| R3_real_ll_lt_freq_legacy | ❌ |
| R4_synth_acc_gt_uniform_reported | ❌ |
| R5_phase_acc_gt_const | ✅ |
| R6_phase_ll_lt_const | ✅ |
| R7_phase_acc_ge_markov | ✅ |
| R8_phase_ll_le_markov | ❌ |

## Reading

- Same frozen protocol as the synthetic phases, applied to REAL work events.
- `synth_zero_shot` tests zero-shot ontology transfer from the synthetic banks.
- `real_learned` is trained only on the real train segment (fresh brain, separate dir).
- Sequence time only: time-window metrics are not meaningful in this pilot.
- Pilot scale: verdicts are directional, not confirmatory.
