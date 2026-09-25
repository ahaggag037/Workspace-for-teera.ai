"""Recall Vault: FTS5-powered semantic-ish retrieval over the mind's memory.

Upgrade path (2026-09-25 cardiac workup finding): 7/21 lessons had NEVER
been retrieved because the KnowledgeBank's token-overlap scoring misses
paraphrases. FTS5 gives ranked full-text search (BM25) with prefix and
NEAR queries, zero dependencies (stdlib sqlite3).

Two indexes, rebuilt from source-of-truth files on every open (cheap at
this scale, always consistent):
  lessons  <- brain/KNOWLEDGE.jsonl
  ledger   <- telemetry/worklog.jsonl
CLI: python3 -m taec_lab.cli recall2 "query" [--k 5]
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .mind import default_brain_dir

VAULT_PATH = Path(default_brain_dir()).parent / "telemetry" / "recall-vault.db"

SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS lessons USING fts5(
    item_id, title, content, tags, source, confidence, use_count, success_count
);
CREATE VIRTUAL TABLE IF NOT EXISTS ledger USING fts5(
    seq, verb, area, phase, detail, outcome, source
);
"""


def _connect(path: Path = VAULT_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.executescript(SCHEMA)
    return conn


def rebuild(path: Path = VAULT_PATH) -> dict:
    """Drop and reindex from source-of-truth files."""
    brain = Path(default_brain_dir())
    lessons = [json.loads(l) for l in (brain / "KNOWLEDGE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ledger = [json.loads(l) for l in (brain.parent / "telemetry" / "worklog.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    conn = _connect(path)
    conn.execute("DELETE FROM lessons")
    conn.execute("DELETE FROM ledger")
    for l in lessons:
        conn.execute(
            "INSERT INTO lessons VALUES (?,?,?,?,?,?,?,?)",
            (l["item_id"], l["title"], l["content"], " ".join(l["tags"]), l["source"],
             str(l["confidence"]), str(l["use_count"]), str(l["success_count"])),
        )
    for r in ledger:
        conn.execute(
            "INSERT INTO ledger VALUES (?,?,?,?,?,?,?)",
            (str(r["seq"]), r["verb"], r.get("area",""), r.get("phase",""),
             r.get("detail",""), r.get("outcome","ok"), r.get("source","")),
        )
    conn.commit()
    counts = {"lessons": len(lessons), "ledger": len(ledger)}
    conn.close()
    return counts


def search_lessons(query: str, k: int = 5, path: Path = VAULT_PATH) -> list[dict]:
    """BM25-ranked lesson retrieval; prefix-matching so 'WAL' finds 'WALs'."""
    rebuild_if_stale(path)
    conn = _connect(path)
    q = " ".join(f'"{w}"*' for w in query.split())
    rows = conn.execute(
        "SELECT item_id, title, snippet(lessons, 2, '>>', '<<', '...', 12), bm25(lessons), "
        "use_count, success_count FROM lessons WHERE lessons MATCH ? ORDER BY bm25(lessons) LIMIT ?",
        (q, k),
    ).fetchall()
    conn.close()
    out = []
    for item_id, title, snip, rank, use, succ in rows:
        reliability = (float(succ) / float(use)) if float(use) > 0 else 0.5
        out.append({
            "item_id": item_id, "title": title, "snippet": snip,
            "bm25": round(rank, 3), "reliability": round(reliability, 2),
            "use_count": int(use),
        })
    return out


def search_ledger(query: str, k: int = 5, path: Path = VAULT_PATH) -> list[dict]:
    rebuild_if_stale(path)
    conn = _connect(path)
    q = " ".join(f'"{w}"*' for w in query.split())
    rows = conn.execute(
        "SELECT seq, verb, phase, snippet(ledger, 4, '>>', '<<', '...', 12), bm25(ledger) "
        "FROM ledger WHERE ledger MATCH ? ORDER BY bm25(ledger) LIMIT ?",
        (q, k),
    ).fetchall()
    conn.close()
    return [{"seq": int(s), "verb": v, "phase": ph, "snippet": sn, "bm25": round(rank,3)}
            for s, v, ph, sn, rank in rows]


def rebuild_if_stale(path: Path = VAULT_PATH) -> None:
    """Reindex only when the ledger grew since last index (freshness check).

    Bug fixed (2026-09-25): on the very first call the .meta file doesn't
    exist, and `last = -1.0` accidentally compared EQUAL to a fresh-empty
    DB — so the first search used to run against an EMPTY vault. Now the
    absence of .meta is treated as stale, forcing an initial rebuild.
    """
    brain = Path(default_brain_dir())
    ledger_path = brain.parent / "telemetry" / "worklog.jsonl"
    meta_path = path.with_suffix(".meta")
    current = ledger_path.stat().st_mtime if ledger_path.exists() else 0.0
    try:
        last = float(meta_path.read_text())
    except Exception:
        last = None  # never indexed before: treat as stale
    if last is None or current != last:
        rebuild(path)
        meta_path.write_text(str(current))
