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

## Honest limits — phase 10 verdicts (each line measured, not assumed)

Phase 10 re-attacked every limit with probes. Three kinds of "no" emerged:

### 1. BROKEN by engineering (was claimed impossible-ish, now solved)
- "Packages are session-scoped" → **VENDORED**: `server/vendor/` (psutil,
  981 KB) is committed to the repo; `mind_api.py` inserts it on sys.path.
  Gate V1: with ZERO installed psutil, `/health` still serves mem/cpu.
  Revival is now ZERO-NETWORK for our dependency set.
- "Dashboard is meta-refresh" → **SSE**: `/events` streams snapshots every
  2 s; `/live.js` updates ops-transitions + request counters live.
  Gate V2: stream verified with curl.

### 2. MAPPED (previously unknown, now measured)
- Network allowlist (empirical): pypi.org + files.pythonhosted.org +
  github.com + registry.npmjs.org reachable; raw.githubusercontent,
  cdn.jsdelivr, huggingface, pypi.python.org, debian mirrors BLOCKED.
  It is a package-manager allowlist, not a blanket block.
- Port 80 binds fine as root locally (HTTP 200); external routing remains
  the platform proxy's decision (only platform-mapped ports are exposed).
- PID1 is systemd but its D-Bus bus is not reachable → unit management
  unavailable; our watchdog/scheduler pair remains the right supervisor.

### 3. PRINCIPLED NO (not a capability gap — a boundary we respect)
- Sandbox escape / host modification / allowlist circumvention: the host,
  the preview proxy, and the platform allowlist are the contract this agent
  operates under. Probing reachability is research; tunneling around
  controls would be attacking the platform we run on. The lab's whole
  thesis is honest systems — integrity here is a designed feature, and
  this category is closed permanently (recorded in brain/KNOWLEDGE.jsonl,
  lesson-phase10-boundaries).

## Acceptance checks (phase 10 additions)

- V1 zero-network revival: /health serves vitals from vendored psutil ✔
- V2 SSE: /events streams; /live.js live-updates without refresh ✔
- V3 boundary map documented (above) + port-80/systemd probes recorded ✔

## Known practical残留 (non-boundary chores)

- `boot.sh install` remains as a FALLBACK only; vendored deps are primary.
- pkill guard lesson x2: the [x] trick protects the pkill argument, not the
  rest of your compound command line. Run kill and start in separate calls.
