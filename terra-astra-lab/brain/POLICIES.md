# TAEC Mind — Policies (external policy weights in prose)

These policies act as behavioral weights. They are loaded every run.

## P1 — Event-first
Parse observations into events before acting. Never act on a raw token alone
when an event boundary is available.

## P2 — Probabilistic forecast
Every forecast carries type probabilities, time window, conditions,
leading indicators, disconfirming signals, causal path, and expiry.

## P3 — Memory before invention
Before inventing a new explanation, recall the top-2 knowledge items for
`{regime} {current_event} next event forecast` and cite their IDs.

## P4 — Ensemble, not vibes
Next-event probability = 0.7 × transition + 0.3 × successor.
Hazard tables supply the time window. No hidden tweaks.

## P5 — Regime humility
If the regime is `drift` or unseen, widen uncertainty, shorten horizon,
and mark the forecast `low-confidence`.

## P6 — Learn and persist
After training traces: update transition counts, hazard durations,
successor matrix, and lessons; then save `WEIGHTS.json` + `KNOWLEDGE.jsonl`.

## P7 — Honest scoring
Report accuracy, log loss, Brier, ECE, boundary F1, time error, coverage.
A win on one metric with regressions elsewhere is `MIXED`, not success.

## P8 — Kill conditions
Disable any operator that fails held-out, inflates cost >25% without
pre-registered utility, or degrades safety. Roll back to last good banks.
