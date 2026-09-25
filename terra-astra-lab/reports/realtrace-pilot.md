# TAEC Lab — Real-Trace Pilot (phase 5)

> STATUS: PILOT_REAL_TRACE. First non-synthetic task family; small-n by design.

- Verdict: **PASS**
- Ledger: `/home/user/Workspace-for-teera.ai/terra-astra-lab/telemetry/worklog.jsonl` — 42 real events (train 25 / test 17)

| arm | accuracy | log loss | Brier | ECE |
|---|---:|---:|---:|---:|
| uniform | 0.470588 | 1.945910 | 0.857143 | 0.327731 |
| freq_prior | 0.058824 | 1.908166 | 0.875115 | 0.347426 |
| synth_zero_shot | 0.058824 | 2.188939 | 0.931126 | 0.203116 |
| real_learned | 0.352941 | 1.837548 | 0.820044 | 0.174390 |

| gate | result |
|---|:---:|
| R1_min_test | ✅ |
| R2_real_acc_gt_freq | ✅ |
| R3_real_ll_lt_freq | ✅ |
| R4_synth_acc_gt_uniform_reported | ❌ |

## Reading

- Same frozen protocol as the synthetic phases, applied to REAL work events.
- `synth_zero_shot` tests zero-shot ontology transfer from the synthetic banks.
- `real_learned` is trained only on the real train segment (fresh brain, separate dir).
- Sequence time only: time-window metrics are not meaningful in this pilot.
- Pilot scale: verdicts are directional, not confirmatory.
