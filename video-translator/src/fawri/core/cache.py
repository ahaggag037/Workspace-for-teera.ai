"""
الذرة الذاكرة — الترجمة التي **تبقى**.

الفكرة التي لا تنتبه لها الأدوات الأخرى:
الترجمة ليست «ناتجاً يُستهلك» بل **أصل يُراكم**.
كل قطعة تُترجم تُخزَّن للأبد بمفتاح = (بصمة الملف + حزمة الموديلات + اللهجة).

النتيجة الانبثاقية:
    المرة الأولى : ترجمة متدرّجة (مسودة → ثابت → محسّن)
    المرة الثانية : ترجمة كاملة فورية بصفر حساب
    المرة الثالثة : أفضل من الثانية (تحسينات سابقة محفوظة)

الملف **يتحسّن مع كل مشاهدة** — وهذا سلوك لا يملكه أي نظام يعالج ثم ينسى.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .models import Segment, Tier

__all__ = ["Cache", "file_fingerprint", "modelset_key"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    hash      TEXT PRIMARY KEY,
    path      TEXT,
    duration  REAL,
    created   REAL
);
CREATE TABLE IF NOT EXISTS segments (
    file_hash TEXT NOT NULL,
    modelset  TEXT NOT NULL,
    dialect   TEXT NOT NULL,
    idx       INTEGER NOT NULL,
    start     REAL NOT NULL,
    end       REAL NOT NULL,
    src       TEXT NOT NULL,
    tgt       TEXT NOT NULL,
    tier      INTEGER NOT NULL,
    quality   REAL NOT NULL,
    speaker   TEXT,
    PRIMARY KEY (file_hash, modelset, dialect, idx)
);
CREATE INDEX IF NOT EXISTS ix_seg_lookup ON segments (file_hash, modelset, dialect);
"""


def file_fingerprint(path: str | Path, sample: int = 1 << 20) -> str:
    """بصمة سريعة: الحجم + أول وآخر ميجابايت.

    لماذا لا نقرأ الملف كله؟ لأن فيديو ٤ جيجا لا يستحق ٣٠ ثانية من التجزئة
    لنعرف هل ترجمناه من قبل. البصمة الطرفية + الحجم تكاد تضمن التفرد
    وتكلف أجزاءً من الثانية.
    """
    p = Path(path)
    h = hashlib.sha256()
    h.update(str(p.stat().st_size).encode())
    with p.open("rb") as f:
        h.update(f.read(sample))
        if p.stat().st_size > sample * 2:
            f.seek(-sample, 2)
            h.update(f.read(sample))
    return h.hexdigest()[:32]


def modelset_key(asr: str, mt: str, dialect: str, version: str = "1") -> str:
    """مفتاح حزمة الموديلات — لأن تغيير الموديل يعني أن الكاش **قديم**.

    حذف هذا المفتاح ينتج خطأً خفياً وخطيراً: ترجمات رديئة قديمة تُقدَّم
    للمستخدم بعد أن ركّب موديلاً أفضل، فيظنّ أن التحسين لم يحدث.
    """
    raw = f"{asr}|{mt}|{dialect}|v{version}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class Cache:
    """ذاكرة ترجمة دائمة فوق SQLite (مكتبة قياسية — بلا تبعيات)."""

    db_path: str | Path = ":memory:"

    def __post_init__(self) -> None:
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # ───────────────────────── كتابة ─────────────────────────
    def touch_file(self, file_hash: str, path: str, duration: float) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO files (hash, path, duration, created) VALUES (?,?,?,?)",
            (file_hash, path, duration, time.time()),
        )
        self._conn.commit()

    def save(
        self,
        file_hash: str,
        modelset: str,
        dialect: str,
        segments: list[Segment],
    ) -> int:
        """يحفظ/يحدّث القطع. **لا يكتب فوق طبقة أعلى بطبقة أدنى** (رتابة الكاش أيضاً)."""
        rows = 0
        for i, s in enumerate(segments):
            if not s.tgt_text:
                continue
            cur = self._conn.execute(
                "SELECT tier FROM segments WHERE file_hash=? AND modelset=? AND dialect=? AND idx=?",
                (file_hash, modelset, dialect, i),
            ).fetchone()
            if cur and int(cur[0]) > int(s.tier):
                continue  # المحفوظ أفضل — لا نُفسده
            self._conn.execute(
                "INSERT OR REPLACE INTO segments "
                "(file_hash, modelset, dialect, idx, start, end, src, tgt, tier, quality, speaker) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    file_hash,
                    modelset,
                    dialect,
                    i,
                    s.start,
                    s.end,
                    s.src_text,
                    s.tgt_text,
                    int(s.tier),
                    s.quality,
                    s.speaker,
                ),
            )
            rows += 1
        self._conn.commit()
        return rows

    # ───────────────────────── قراءة ─────────────────────────
    def load(self, file_hash: str, modelset: str, dialect: str) -> list[Segment]:
        rows = self._conn.execute(
            "SELECT idx, start, end, src, tgt, tier, quality, speaker FROM segments "
            "WHERE file_hash=? AND modelset=? AND dialect=? ORDER BY idx",
            (file_hash, modelset, dialect),
        ).fetchall()
        out: list[Segment] = []
        for idx, start, end, src, tgt, tier, quality, speaker in rows:
            seg = Segment(
                id=f"{idx}",
                start=start,
                end=end,
                src_text=src,
                tgt_text=tgt,
                tier=Tier(int(tier)),
                quality=quality,
                speaker=speaker,
            )
            out.append(seg)
        return out

    def has(self, file_hash: str, modelset: str, dialect: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM segments WHERE file_hash=? AND modelset=? AND dialect=? LIMIT 1",
            (file_hash, modelset, dialect),
        ).fetchone()
        return row is not None

    def stats(self) -> dict[str, float]:
        n = self._conn.execute("SELECT COUNT(*) FROM segments").fetchone()[0]
        files = self._conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        return {"segments": float(n), "files": float(files)}

    # ───────────────────────── تصدير ─────────────────────────
    def export_json(self, file_hash: str, modelset: str, dialect: str) -> str:
        segs = self.load(file_hash, modelset, dialect)
        return json.dumps(
            [
                {
                    "start": s.start,
                    "end": s.end,
                    "src": s.src_text,
                    "tgt": s.tgt_text,
                    "tier": s.tier.name,
                }
                for s in segs
            ],
            ensure_ascii=False,
            indent=2,
        )

    def close(self) -> None:
        self._conn.close()
