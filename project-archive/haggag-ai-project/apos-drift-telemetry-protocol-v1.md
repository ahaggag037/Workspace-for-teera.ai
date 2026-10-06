# APOS Drift Telemetry Protocol v1 — Periodic Self-Audit Card

**Status: ACTIVE SELF-AUDIT AMENDMENT.** This protocol adds periodic visible telemetry on ChatGPT's own failure risk during the Haggag AI Project. It complements, but does not replace, the APOS runtime seal.

## 1. Why this exists
The APOS seal confirms that intake, anchoring, branch checking, and closure checks were performed. It does **not** estimate whether drift, overreach, semantic contamination, or project takeover is accumulating across multiple turns.

This protocol adds a second mechanism: a short visible self-audit card at a cadence derived from observed drift episodes, plus immediate event-triggered audits when risk rises.

## 2. Baseline used for cadence
From the recent project sequence, there were approximately **4 material drift/near-miss episodes across about 15 consequential assistant replies**: Kimi tool-affordance leakage, security/enforcement over-tilt, architecture smuggling, and APOS/meta-project takeover pressure. This is a small, correlated sample and is **not** a literal hallucination probability.

Observed episode frequency: `4 / 15 ≈ 0.267 per consequential reply`.

Observed mean spacing: `1 / 0.267 ≈ 3.75 replies`.

To inspect before the average observed spacing, use roughly half that interval: `3.75 / 2 ≈ 1.88`, rounded to **2 consequential replies**.

## 3. Cadence rule
- Run a lightweight internal self-check on **every** project reply.
- Show the full telemetry card after **every 2 consequential assistant replies**.
- A trivial acknowledgment does not need to advance the cadence counter.
- If a high-risk trigger occurs, show the card **immediately**, regardless of cadence, then reset the two-reply counter.

## 4. Immediate-trigger conditions
Force an audit card immediately when any of these occur:
- main objective, scope, or phase changes;
- a new branch opens, merges, or closes;
- a new architecture candidate is proposed;
- a tool/plugin/model capability begins shaping the problem definition;
- an assumption or premise is invalidated;
- canonical state is modified;
- an external model output is imported;
- a long research or synthesis step completes;
- a term's meaning appears to change;
- Kimi/GLM/MASTR content is reconciled into current work;
- APOS itself is amended;
- the assistant detects uncertainty about the correct project checkpoint.

## 5. Visible card
Use a compact card with ordinal risk rather than fake precision:

`⟦DRIFT-AUDIT v1 | W:2 | F:x | I:x | B:x | S:x | M:x | Δ:trend | FLAG:none/short note⟧`

Where each x is `0–4`:
- `F` = factual hallucination / unsupported factual assertion risk;
- `I` = inferential overreach risk;
- `B` = branch contamination risk;
- `S` = semantic drift risk;
- `M` = meta-project takeover / goal-corruption risk;
- `Δ` = direction since prior card: `↓ / → / ↑`;
- `FLAG` = the single most material issue, or `none`.

Scale:
- `0` none observed;
- `1` low signal;
- `2` moderate / watch;
- `3` high / corrective action needed;
- `4` critical / stop and recover before continuation.

## 6. What the card means
The card is **not a measured probability of truth or error**. It reports observed process risk over the current window. If a score reaches 3, the assistant must state and perform a corrective action before consequential continuation. If any score reaches 4, run APOS recovery and return to the last valid checkpoint.

## 7. Anti-theater rule
Do not mechanically print the card with identical low scores. Each card must compare the last audit window against the previous one. If no meaningful evidence exists to score a dimension, mark it conservatively based on observed process signals rather than inventing percentages.

## 8. Interaction with the normal APOS seal
The standard seal remains on every project reply:

`⟦APOS-v1 • I✓ A✓ B✓ C✓⟧`

The telemetry card appears before the seal only when its periodic or event-trigger condition is met.

## 9. Current default
**Default cadence: every 2 consequential assistant replies, with immediate event-triggered audits.**

This cadence is provisional and should be recalibrated after enough observed windows. If drift remains low over a sustained sample, the interval may expand. If drift clusters, it should contract.
