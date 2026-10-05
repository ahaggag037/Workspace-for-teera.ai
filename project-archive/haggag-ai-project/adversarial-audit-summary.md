# Independent Adversarial Audit — Preserved Findings

## Provenance
This file preserves the substantive findings of an independent adversarial audit supplied by the user on 2026-10-05. The audit is evidence to inspect, not an authority.

## Auditor's executive verdict
The prior research was characterized as source-disciplined but temporally weak, vendor-concentrated, and increasingly design-shaped. The auditor judged the project's central model-independent-layer hypothesis **SPECULATIVE** because no direct controlled evidence showed stable multi-model uplift.

## Findings the audit said survived
- External outcome validation is stronger than agent self-report.
- Separating context/memory/machine state/artifacts/evidence is operationally useful.
- MCP-style hints/annotations are not security enforcement.
- Multi-agent overhead can be large in at least one documented research system.
- Source discipline was stronger than average, though not error-free.

## Methodological failures identified
- Capability evidence was not refreshed aggressively enough.
- A genuine falsification pass came too late.
- Vendor sources were overrepresented.
- Production incidents were underused.
- Some VERIFIED/CORROBORATED labels were stronger than evidence warranted.
- Design vocabulary accumulated during discovery.
- The tension between “prefer simplicity” and an expanding capability map was unresolved.
- Negative results and failed searches were under-recorded.

## Missing evidence classes elevated by the audit
1. Production incident forensics, including EchoLeak and other real-world failures.
2. Capability/time-horizon trends such as METR.
3. Containment / blast-radius engineering.
4. Legal/accountability precedents.
5. Capability-based security.
6. Verification economics.
7. Critical cognitive-science work on executive-function terminology.
8. Monitoring/approval fatigue.

## Audit-of-audit corrections
- The audit's rejection of the OSWorld 500-step detail was itself incorrect.
- Its attempted 20.6% → ~72.6% OSWorld capability trajectory was not accepted without proving benchmark/protocol equivalence.
- METR trend direction is relevant, but exact figures must be tied to the exact update and uncertainty bounds.
- Air Canada is a useful accountability case, not a universal legal rule.

## Current merged keep / revise / discard
### KEEP
- Outcome validation over self-report.
- Explicit separation of major state/evidence categories.
- “Hints are not enforcement.”
- Strong source-provenance discipline.
- Explicit caution around preprints and draft standards.

### REVISE
- Every capability claim should carry version/date/protocol and a freshness trigger.
- Memory findings must include pollution, expiration, provenance, and rollback risk.
- Strong vendor claims should be paired with independent evidence or marked vendor-specific.
- Cross-disciplinary terms should describe measurable functions rather than imply biological or architectural equivalence.

### DISCARD / QUARANTINE
- Any use of a historical benchmark point as evidence of permanent model weakness.
- Incorrect Hindsight citation linkage.
- Incorrect or stale publication dates.
- Any implicit commitment to a control-plane/gateway/etc. before evidence establishes the need.
