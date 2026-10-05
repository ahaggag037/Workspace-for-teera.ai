# Evidence Ledger & Robust Findings

> Stored memory is state, not truth. Status labels below preserve historical epistemic state and can be revised by later evidence.

## Reconstructed MASTER evidence

- `obj_c7f0a96206334e66` — **VERIFIED at recording** — simple composable primitives first; add multi-agent structure only for concrete parallelism/context/tool/policy reasons.
- `obj_577e25a5acc44369` — **VERIFIED at recording** — separate active context, reusable memory, durable artifacts, and execution state; chat history alone is not robust long-horizon memory.
- `obj_6513abc47ab64389` — **VERIFIED at recording** — evals, traces, regressions, outcome checks, and human calibration are first-class engineering artifacts.
- `obj_3b1c1b2f91804d1f` — **VERIFIED at recording** — action-taking-agent security is a system property spanning model, tool surface, harness, execution environment, and external content.
- `obj_f861e05adf774680` — **CORROBORATED** — memory capacity and tool availability are not sufficient proxies for executive control or reliable performance.
- `obj_fedecfacf7ff48f9` — **CORROBORATED** — persistent memory creates a distinct security boundary because harmful content may persist across sessions.
- `obj_dad15e3ad70c4cc0` — **CORROBORATED** — self-reported confidence is not a universal reliability signal.

## Current robust/high-confidence findings after independent audit + audit-of-audit

1. External outcome validation is stronger than an agent's self-report that it succeeded.
2. Context, persistent memory, machine state, artifacts, and evidence/provenance should not be collapsed into one concept.
3. Prompt wording, tool descriptions, and annotations are not hard security enforcement.
4. Long-running action-taking agents inherit distributed-systems failure modes such as retries, duplicates, partial failure, stale state, recovery problems, and non-idempotent side effects.
5. Human approval can degrade through approval fatigue; it is not automatically a strong safety boundary.
6. Persistent memory can expand attack surface and preserve malicious influence across sessions.
7. Production incidents are essential evidence for reliability research; benchmark-only reasoning is insufficient.
8. Capability claims require explicit model, benchmark/protocol, date, and freshness checks.
9. There is still no direct evidence in this project that a universal model-independent external cognition layer reliably improves multiple models across domains.

## Audit-of-audit corrections

- The adversarial auditor's claim that OSWorld 2.0 lacked a 500-step basis was rejected after checking official OSWorld 2.0 material.
- A claimed 20.6% → ~72.6% OSWorld trend was not accepted as apples-to-apples without benchmark/version/protocol equivalence.
- METR capability-growth direction is important, but exact numbers must remain tied to the exact update and uncertainty bounds.
- Air Canada is useful as an accountability case, not as a universal legal rule across jurisdictions.
