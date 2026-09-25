# TAEC-MIND — auto-load pointer

If you are the agent operating this workspace, do this FIRST in every turn
that touches TAEC:

1. Read `<repo>/terra-astra-lab/brain/BOOT.md`.
2. Read `<repo>/terra-astra-lab/brain/POLICIES.md`.
3. Read `<repo>/terra-astra-lab/brain/STATE.md`.
4. Load `<repo>/terra-astra-lab/brain/WEIGHTS.json` and `KNOWLEDGE.jsonl`
   when they exist; otherwise declare `COLD_START`.
5. Use `python -m taec_lab.cli status` from `<repo>/terra-astra-lab`
   to verify what the Mind currently remembers.

`<repo>` is this repository root (the folder that contains this file).

This is the external mind: workspace-side weights + knowledge that persist
across turns. Model weights are fixed; this bank is what learns.
Never confuse the two, and never claim more than the banks + held-out
evidence support.
