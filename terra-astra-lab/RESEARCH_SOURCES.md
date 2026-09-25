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


## 2026-09-25 — deep self-system session (RESEARCH-OS applied to our own server)

Method: the 10-layer Fawri Research OS (video-translator/meta/RESEARCH-OS.md)
applied to the TAEC server itself. SKELETON: unknowns U1-U7 about concurrency,
signals, observability. FANOUT: 3 parallel searches. GRADE + TRIANGULATE below.
Sources (retrieved 2026-09-25):

1. [A] SQLite concurrency engineering — WAL + busy_timeout>=5000ms +
   synchronous=NORMAL + small write transactions; gotcha: busy_timeout does
   not cover read->write upgrades
   (https://tenthousandmeters.com/blog/sqlite-concurrent-writes-and-database-is-locked-errors/)
   — triangulated by dbpro.app + ai2sql builder guides (same pragma trio).
2. [A] Graceful SIGTERM for http.server: shutdown() MUST run from a thread
   other than serve_forever(); server_close() in finally
   (https://oneuptime.com/blog/post/2026-01-16-docker-graceful-shutdown-signals/view)
   — consistent with the classic gevent #1817 discussion.
3. [B] Health-check orthodoxy: liveness = cheap always-200, no dependency
   calls; readiness = deep; /metrics for counters
   (https://codelit.io/blog/health-check-monitoring-patterns) — our /health
   is liveness-style; enriched it with /proc reads (loadavg, fd usage) that
   stay cheap and dependency-free; RED method completed with an errors
   counter (5xx convention).

Adopted into mind_api v3: WAL+busy_timeout+synchronous on the metrics DB;
graceful SIGTERM/SIGINT (verified live: 'graceful shutdown: signal 15 →
server closed cleanly'); /health v3 with /proc/loadavg + fd-usage vs
RLIMIT_NOFILE=1024 (works with zero psutil); /metrics errors_total (5xx).
Adopted into server supervisors: fcntl single-instance locks (double
watchdog now exits cleanly — verified) + deterministic micro-jitter.

Honesty: sources are engineering references, not proof of superiority;
all claims above were re-verified by live probes on our own server.
