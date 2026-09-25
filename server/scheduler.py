"""Scheduler: a session-scoped background tick for the operational mind.

Every 60 seconds (first tick immediate) it runs the IDEMPOTENT `ops-learn`
(only new ledger rows are absorbed since the phase-7 fix) and appends a
heartbeat line with the live transition count. This turns the ops brain
from something refreshed manually into a continuously-maintained organ.

Heartbeats go to server/heartbeat.log (infrastructure), NOT the worklog —
the worklog records real work events only.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

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
HEARTBEAT = SERVER_DIR / "heartbeat.log"
INTERVAL_SECONDS = 60


def tick() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "taec_lab.cli", "ops-learn"],
        cwd=str(LAB), capture_output=True, text=True, timeout=30,
    )
    try:
        payload = json.loads(result.stdout)
        line = (
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} tick transitions="
            f"{payload.get('n_transitions')} absorbed={payload.get('rows_absorbed')} "
            f"last_seq={payload.get('last_seq_learned')}"
        )
    except Exception:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} tick ERROR rc={result.returncode} {result.stderr[:120]}"
    with open(HEARTBEAT, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def main() -> None:
    _lock = _acquire_single_instance("scheduler")
    while True:
        try:
            tick()
        except Exception as error:  # never die on a bad tick
            with open(HEARTBEAT, "a", encoding="utf-8") as handle:
                handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} tick EXCEPTION {error!r}\n")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
