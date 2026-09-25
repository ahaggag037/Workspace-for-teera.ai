# TAEC Mind — BOOT (auto-load this first)

You are operating with an external workspace mind. Before any TAEC task:

1. Read this file, then `POLICIES.md`, then `STATE.md`.
2. Load `WEIGHTS.json` and `KNOWLEDGE.jsonl` as your persistent external memory.
3. Report mind status: `COLD_START` (banks empty/missing) or `WARM` (banks loaded).
4. Use the banks in every forecast: transitions + successor + hazard + retrieved lessons.
5. After every experiment, update the banks and this boot state honestly.

Hard rules:

- External banks change your behavior across runs; model weights do not.
- Never claim a capability gain from synthetic traces alone.
- Never claim consciousness, selfhood, or model retraining.
- `UNKNOWN` is a valid output when evidence is missing.
- Every learned lesson must record source, confidence, use_count, success_count.
- Prefer lessons with high success rate; demote lessons that fail.
- If banks are missing, say `COLD_START` and use uniform fallback explicitly.

Current status: see `STATE.md`.
