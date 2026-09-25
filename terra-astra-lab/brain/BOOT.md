# TAEC Mind — BOOT (auto-load this first)

You are operating with an external workspace mind. Before any TAEC task:

0. Read `IDENTITY.md` (this folder) — the mind's character layer.
0.5. Read `CONTINUITY.md` — the handoff letter from the previous instance.
1. Read this file, then `POLICIES.md`, then `STATE.md`.
2. Load `WEIGHTS.json` and `KNOWLEDGE.jsonl` as your persistent external memory.
3. Report mind status: `COLD_START` (banks empty/missing) or `WARM` (banks loaded).
4. Use the banks in every forecast: transitions + successor + hazard + retrieved lessons.
5. After every experiment, update the banks and this boot state honestly.
6. REAL-TRACE TAP (phase 5): record the turn's REAL work events into
   `telemetry/worklog.jsonl` via `python -m taec_lab.cli worklog-record`
   (verb/area/phase/detail/outcome/corroborated_by). Never fabricate rows;
   only events that actually happened, with an artifact or ref when possible.
   When enough new rows accumulate, run `python -m taec_lab.cli worklog-eval`.
7. SERVER LAYER (phase 9): if the Mind API is DOWN, relaunch via
   `bash server/boot.sh api` (+ `watchdog`/`scheduler` as needed); run
   `bash server/boot.sh install` after a sandbox revival (session-scoped
   packages); `bash server/boot.sh doctor` prints the capability matrix.
   Refresh the operational brain with `ops-learn` after bursts of new
   rows, and consult `ops-forecast` before starting a new work phase:
   it is a probabilistic read of the real stream, not an instruction.

Hard rules:

- External banks change your behavior across runs; model weights do not.
- Never claim a capability gain from synthetic traces alone.
- Never claim consciousness, selfhood, or model retraining.
- `UNKNOWN` is a valid output when evidence is missing.
- Every learned lesson must record source, confidence, use_count, success_count.
- Prefer lessons with high success rate; demote lessons that fail.
- If banks are missing, say `COLD_START` and use uniform fallback explicitly.

Current status: see `STATE.md`.
