"""Watchdog: keeps the Mind API alive for the session.

The sandbox kills all processes between sessions, and long-lived services
can crash mid-session. This supervisor polls /health every 5 seconds and,
after 2 consecutive failures, respawns `python3 -m taec_lab.mind_api`
as a child process (same lifetime as the watchdog itself). Actions are
logged to server/watchdog.log so recovery is auditable, not silent.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import time
import urllib.request

SERVER_DIR = pathlib.Path(__file__).resolve().parent

def _acquire_single_instance(name: str):
    """fcntl lock so two copies never run (double watchdog = API spawn wars)."""
    import fcntl
    lock_path = pathlib.Path("/tmp") / f"taec-{name}.lock"
    handle = open(lock_path, "w")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print(f"[{name}] another instance already holds {lock_path} — exiting", flush=True)
        raise SystemExit(0)
    return handle

ROOT = SERVER_DIR.parent
LAB = ROOT / "terra-astra-lab"
API_LOG = SERVER_DIR / "mind-api.log"
WATCH_LOG = SERVER_DIR / "watchdog.log"
PORT = os.environ.get("MIND_API_PORT", "8000")
URL = f"http://127.0.0.1:{PORT}/health"
CHECK_SECONDS = 5
FAILS_BEFORE_RESTART = 2


def log(message: str) -> None:
    with open(WATCH_LOG, "a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def healthy() -> bool:
    try:
        with urllib.request.urlopen(URL, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def restart() -> None:
    log("respawning mind_api")
    API_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(API_LOG, "ab") as sink:
        subprocess.Popen(
            [sys.executable, "-m", "taec_lab.mind_api"],
            cwd=str(LAB),
            env=dict(os.environ, MIND_API_PORT=PORT),
            stdout=sink,
            stderr=subprocess.STDOUT,
        )
    time.sleep(3)  # give the child a moment before the next poll


def main() -> None:
    _lock = _acquire_single_instance("watchdog")
    log(f"watchdog start (url={URL}, check={CHECK_SECONDS}s, restart_after={FAILS_BEFORE_RESTART})")
    failures = 0
    while True:
        if healthy():
            failures = 0
        else:
            failures += 1
            log(f"health check FAILED ({failures}/{FAILS_BEFORE_RESTART})")
            if failures >= FAILS_BEFORE_RESTART:
                restart()
                failures = 0
        time.sleep(CHECK_SECONDS + (os.getpid() % 3) * 0.1)  # tiny deterministic jitter


if __name__ == "__main__":
    main()
