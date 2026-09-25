# Server capability layer (phase 9)

The Arena sandbox wipes **processes and non-workspace state** every session
revival, while `/home/user` (this repo) persists. This directory is the
declarative answer: the server's full capability set is code here, rebuilt
with one command per component.

## Why this exists (measured, not assumed)

Empirical probe (2026-09-25, see worklog + RESEARCH_SOURCES):
- passwordless `sudo` available; 2 CPUs, ~4 GB RAM, ~20 GB disk free
- outbound network IS available from the sandbox: pypi.org and github.com
  reachable (HTTP 200); ubuntu archive blocked (platform allowlist)
- processes die on revival → services must be restartable by declaration

## Components

| component | command (foreground) | what it does |
|---|---|---|
| Mind API v2 | `boot.sh api` | read-only mind surface: `/` dashboard (RTL), `/status`, `/forecast`, `/lessons`, `/ledger`, `/health`, `/metrics` (SQLite-persisted counters at `telemetry/mind-api.db`) |
| Watchdog | `boot.sh watchdog` | polls `/health` every 5 s, respawns the API after 2 consecutive failures; actions logged to `watchdog.log` |
| Scheduler | `boot.sh scheduler` | idempotent `ops-learn` tick (immediate, then every 60 s) → `heartbeat.log` |
| Installer | `boot.sh install` | installs `requirements.txt` (psutil) — session-scoped by design, rerun after revival |
| Doctor | `boot.sh doctor` | capability matrix: sudo/network/sqlite/psutil/resources/api |
| Status | `boot.sh status` | is the API up? (exit code reflects state) |

## Acceptance checks (pre-registered before build; all verified live)

- C1 `boot.sh api` lifts `/health` DOWN→200 within ~5 s ✔
- C2 watchdog detects a killed API and restores it (watchdog.log evidence) ✔
- C3 `/metrics` counters accumulate and SURVIVE an API restart (SQLite) ✔
- C4 scheduler tick recorded; `ops-learn` stays idempotent ✔
- C5 pip install works (psutil imported into `/health`) ✔

## Honest limits (what this layer cannot do)

- Cannot modify the host platform, the preview proxy, or survive the
  sandbox revival itself — it re-declares itself instead.
- Installed packages are session-scoped (snapshot excludes site-packages);
  `boot.sh install` re-fetches from PyPI (reachable) after revival.
- No inbound internet: ports are exposed only through the platform proxy.
