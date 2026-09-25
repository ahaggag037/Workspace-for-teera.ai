"""Knowledge bank: persistent workspace-side information store.

Deterministic, stdlib-only retrieval. Each item tracks use/success so the
Mind can prefer knowledge that actually helped forecasts.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

_TOKEN = re.compile(r"[a-z0-9_]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


@dataclass
class KnowledgeItem:
    item_id: str
    title: str
    content: str
    tags: tuple[str, ...] = ()
    source: str = "lab"
    confidence: float = 0.5
    use_count: int = 0
    success_count: int = 0

    def text(self) -> str:
        return f"{self.title} {self.content} {' '.join(self.tags)}"

    def score(self, query: str) -> float:
        q = _tokens(query)
        if not q:
            return 0.0
        doc = _tokens(self.text())
        overlap = len(q & doc)
        if overlap == 0:
            return 0.0
        precision = overlap / len(q)
        recall = overlap / max(1, len(doc))
        base = 2 * precision * recall / (precision + recall + 1e-9)
        reliability = 0.5 + 0.5 * (self.success_count / self.use_count) if self.use_count else 0.5
        return base * (0.5 + 0.5 * self.confidence) * (0.7 + 0.3 * reliability)


class KnowledgeBank:
    def __init__(self) -> None:
        self.items: dict[str, KnowledgeItem] = {}

    def add(self, item: KnowledgeItem) -> None:
        self.items[item.item_id] = item

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeItem]:
        ranked = sorted(
            (item for item in self.items.values()),
            key=lambda item: item.score(query),
            reverse=True,
        )
        return [item for item in ranked[:top_k] if item.score(query) > 0]

    def record_use(self, item_id: str, success: bool) -> None:
        item = self.items.get(item_id)
        if item is None:
            return
        item.use_count += 1
        if success:
            item.success_count += 1

    def to_jsonl(self) -> str:
        lines = []
        for item in self.items.values():
            payload = asdict(item)
            payload["tags"] = list(payload["tags"])
            lines.append(json.dumps(payload, sort_keys=True))
        return "\n".join(lines) + ("\n" if lines else "")

    @classmethod
    def from_jsonl(cls, text: str) -> "KnowledgeBank":
        bank = cls()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            payload["tags"] = tuple(payload.get("tags", ()))
            bank.add(KnowledgeItem(**payload))
        return bank

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.to_jsonl(), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "KnowledgeBank":
        p = Path(path)
        if not p.exists():
            return cls()
        return cls.from_jsonl(p.read_text(encoding="utf-8"))

    def __len__(self) -> int:
        return len(self.items)
