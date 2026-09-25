# Research Sources

## 2026-09-25 — operator-level web research (first recorded research pass)

Provenance: performed by the operating agent via the platform's `web_search`
tool (2 queries, 8 sources retrieved). This is OPERATOR-LEVEL research done
outside any deterministic protocol run. Per AGENTS.md rule 5, no network is
used inside protocol/eval execution; this file is exactly where such research
must be recorded (as design context, never as performance evidence).

Queries:
1. "process mining directly-follows graphs event log next activity prediction"
2. "next event prediction business process logs transition matrix baseline accuracy"

### Key findings relevant to the real-trace work (phase 5–7)

1. The worklog/ops-brain construct has a mature academic name: **process
   mining** — discovering, conformance-checking, and enhancing process models
   from execution event logs
   (overview: https://apromore.com/process-mining-101 ;
    https://grokipedia.com/page/Process_mining ).
2. Our `pair_counts` table IS a **Directly-Follows Graph (DFG)** — the
   standard baseline discovery artifact built by counting how often one
   activity directly follows another (Foundations of Process Discovery,
   Springer: https://link.springer.com/chapter/10.1007/978-3-031-08848-3_2 ).
3. Next-activity prediction from trace prefixes is a standard task
   ("predictive process monitoring"); an **annotated transition system with
   transition probabilities** is a recognized baseline, and LSTM models reach
   ~71–76% accuracy on REAL logs with thousands of cases (Springer
   https://link.springer.com/chapter/10.1007/978-3-319-59536-8_30 ). Our
   0.35 accuracy at n≈50 transitions is consistent with a tiny-data
   transition baseline — honest context, not a red flag.
4. Heuristics Miner handles noisy logs by **dependency-threshold filtering**
   instead of raw frequencies — a candidate upgrade for the ops brain's pair
   counts (grokipedia.com/page/Process_mining).
5. Standard event-log schema expects **case identifiers and completion
   timestamps**; our ledger lacks both. Adding `case_id` (a work
   session/turn as a case) and wall-clock `ts` unlocks per-case DFGs,
   variants, and real time-to-event metrics.
6. Recent frontier: graph pretraining across logs for predictive monitoring
   (ProcessGFM, 2025: https://www.mdpi.com/2227-7390/13/24/3991 ) — context
   for the far horizon only; the lab remains stdlib-only.

### Design implications adopted (recorded, not yet implemented)

- Ledger schema v2: add `case_id` and `ts` (wall clock) columns; keep the
  old fields so v1 rows stay readable.
- Ops brain upgrade path: dependency-threshold filtering (Heuristics-Miner
  style) before Laplace smoothing.
- Reporting: always state n and compare against field baselines, never
  against vibes ("0.35 at n=50" needs the LSTM-on-BPI context above).

Implementation boundary (unchanged): direct evidence is not imported as
proof that the lab mechanism matches any biology or that TAEC beats these
methods — the synthetic protocol results remain engineering/protocol
evidence only, and the real-trace pilot is directional at pilot scale.
