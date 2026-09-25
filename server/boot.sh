#!/usr/bin/env bash
# TAEC workspace server boot layer.
# The sandbox wipes processes (and non-/home/user state) between sessions;
# everything durable lives in this repo and is re-declared here, so one
# command per component restores the full server capability set.
#
# Usage: boot.sh {api|watchdog|scheduler|install|status|doctor}
# Components run in the FOREGROUND (launch each via a process manager /
# start_process so the platform keeps it alive for the session).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAB="$ROOT/terra-astra-lab"
PORT="${MIND_API_PORT:-8000}"

case "${1:-status}" in
  api)
    cd "$LAB"
    echo "[boot] Mind API (v2) on 0.0.0.0:${PORT}"
    MIND_API_PORT="$PORT" exec python3 -m taec_lab.mind_api
    ;;
  watchdog)
    echo "[boot] watchdog: will keep the Mind API alive (check 5s, restart after 2 fails)"
    exec python3 "$ROOT/server/watchdog.py"
    ;;
  scheduler)
    echo "[boot] scheduler: ops-learn tick then every 60s (idempotent)"
    exec python3 "$ROOT/server/scheduler.py"
    ;;
  install)
    # Platform allowlist permits PyPI; PEP 668 needs --break-system-packages.
    # Session-scoped by design (snapshot excludes site-packages): boot.sh
    # reinstalls declaratively after each sandbox revival.
    pip3 install --user --break-system-packages -r "$ROOT/server/requirements.txt"
    echo "[boot] requirements installed (session-scoped; rerun after revival)"
    ;;
  status)
    if curl -sf -m 2 "http://127.0.0.1:${PORT}/health"; then
      echo
      echo "UP (port ${PORT})"
    else
      echo "DOWN (port ${PORT})"
      exit 1
    fi
    ;;
  doctor)
    echo "== TAEC server doctor =="
    printf "sudo            : %s\n" "$(sudo -n whoami 2>/dev/null || echo NO)"
    printf "pypi reachable  : %s\n" "$(curl -s -m 4 -o /dev/null -w '%{http_code}' https://pypi.org)"
    printf "github reachable: %s\n" "$(curl -s -m 4 -o /dev/null -w '%{http_code}' https://github.com)"
    printf "sqlite (stdlib) : %s\n" "$(python3 -c 'import sqlite3; print(sqlite3.sqlite_version)' 2>/dev/null || echo MISSING)"
    printf "psutil          : %s\n" "$(python3 -c 'import psutil; print(psutil.__version__)' 2>/dev/null || echo 'missing (run: boot.sh install)')"
    printf "cpus / mem      : %s / %s MiB\n" "$(nproc)" "$(free -m | awk 'NR==2{print $2}')"
    printf "disk free       : %s\n" "$(df -h / | awk 'NR==2{print $4}')"
    printf "mind api        : $(curl -s -o /dev/null -w '%{http_code}' -m 2 "http://127.0.0.1:${PORT}/health" 2>/dev/null || echo DOWN)\n"
    ;;
  *)
    echo "usage: boot.sh {api|watchdog|scheduler|install|status|doctor}" >&2
    exit 2
    ;;
esac
