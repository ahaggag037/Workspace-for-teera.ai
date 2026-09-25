"""
الشبكة — المُنسِّق: حيث تترابط كل الذرّات.

إن قرأت ملفاً واحداً لتفهم المشروع فليكن هذا.
هنا تلتقي:
    Segment (الحالة)  ←→  Task (الزمن)      عبر seg_id
    Scheduler (الحساب) ←→ Composer (اللغة)  عبر tier
    Engine (الزمن)    ←→ Cache (الذاكرة)    عبر file_hash

كل رابطة ضعيفة بمفردها. شبكتكما هي ما ينتج «الصلابة».
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..mt.glossary import Glossary
from ..subs.arabic import normalize_arabic
from ..subs.composer import APPLIED, Composer
from .models import Segment, Task, Tier

__all__ = ["Engine", "EngineConfig", "DisplayEvent"]


@dataclass
class EngineConfig:
    """كل أرقام النظام في مكان واحد — لأن الأرقام المبعثرة تُنسى وتتضارب."""

    delta: float = 4.0            # تأخير الراحة Δ (ثوانٍ) — يُحسب لاحقاً بـ recommend_delta
    throughput: float = 8.0       # حِساب-ثانية متاحة لكل ثانية زمنية (٨x realtime)
    quantum: float = 0.05
    dialect: str = "egyptian"     # "msa" | "egyptian"
    modelset: str = "dev"
    q_floor: float = 0.80         # جودة دنيا مقبولة للقطع الأولى


@dataclass
class DisplayEvent:
    """لحظة ظهور سطر — **نقطة اللاعودة**.

    بعد هذه اللحظة: `segment.displayed == True`، وأي تحديث يرمي ImmutableCueError.
    """

    seg: Segment
    at: float


@dataclass
class Engine:
    """المُنسِّق. لا يعرف شيئاً عن الموديلات — بل يستقبل نصوصاً جاهزة.

    لماذا هذا الفصل؟ لأن المُنسِّق يجب أن يكون **قابلاً للاختبار بلا GPU وبلا
    ٦ جيجا موديلات**. كل ما يحتاجه: (نص، طبقة، زمن).
    """

    config: EngineConfig = field(default_factory=EngineConfig)
    composer: Composer = field(default_factory=Composer)
    glossary: Glossary = field(default_factory=Glossary)

    segments: list[Segment] = field(default_factory=list)
    tasks: dict[str, Task] = field(default_factory=dict)
    now: float = 0.0

    # ───────────────────────── التحميل ─────────────────────────
    def load(self, cues: list[tuple[float, float, str, str | None]]) -> None:
        """يحمّل قطعاً (بداية، نهاية، نص أصلي، متكلّم) ويبني مهامها الزمنية.

        ملاحظة ذرّية: `release = 0` للجميع. هذا سطر واحد، لكنه **كل الفكرة**.
        في نظام بثّ حيّ يكون `release = start` — وهنا يضيع الاستباق كله.
        """
        self.segments = []
        self.tasks = {}
        for i, (start, end, src, speaker) in enumerate(cues):
            seg = Segment(id=f"s{i}", start=start, end=end, src_text=src, speaker=speaker)
            self.segments.append(seg)
            self.tasks[seg.id] = Task(
                seg_id=seg.id,
                release=0.0,                      # ← الملف محلي: كل شيء متاح الآن
                deadline=start + self.config.delta,
                mandatory_cost=0.35,              # تكلفة مسوّدة (GPU-ثوانٍ/ثانية صوت)
                difficulty=self._difficulty(src),
            )

    @staticmethod
    def _difficulty(src: str) -> float:
        """κ — صعوبة تقديرية: طول + كثافة مصطلحات + علامات استفهام.

        تقدير بدائي متعمَّد: المبدأ أن تكون κ **رخيصة**، لأن دقتها المطلقة
        أقل أهمية من ترتيبها النسبي (water-filling يحتاج ترتيباً لا قياساً دقيقاً).
        """
        words = max(1, len(src.split()))
        rarity = sum(1 for w in src.split() if len(w) > 9) / words
        questions = src.count("?") * 0.15
        length = min(1.0, words / 25.0)
        return round(0.4 + 1.6 * (0.5 * length + 0.4 * rarity + questions), 3)

    # ───────────────────────── التقديم ─────────────────────────
    def submit(self, seg_id: str, text: str, tier: Tier, quality: float | None = None) -> str:
        """يُدخل ترجمة جديدة. المُلحِّن يقرّر القبول (عرض/تنزيل/معايير).

        الترتيب هنا **هو** ضمان عدم الرفرفة:
        المُلحِّن يرفض ما عُرِض، ويرفض التنزيل. المُنسِّق لا يتدخّل.
        """
        seg = self.by_id(seg_id)
        if seg is None:
            return "rejected:unknown"
        text = self.glossary.apply_to(text)
        if self.config.dialect == "egyptian":
            from ..mt.dialect_linter import enforce_dialect

            text = enforce_dialect(text)
        return self.composer.apply(seg, text, tier, quality).status

    # ───────────────────────── الزمن ─────────────────────────
    def advance_to(self, t: float) -> list[DisplayEvent]:
        """يتقدّم بالزمن ويُعيد السطور التي **ظهرت الآن**.

        هذه هي النقطة التي يتحوّل فيها الكائن إلى تجربة مستخدم:
        قبلها كل شيء قابل للتغيير، بعدها كل شيء متجمّد.
        """
        events: list[DisplayEvent] = []
        for seg in self.segments:
            if seg.displayed:
                continue
            if self.tasks[seg.id].deadline <= t + 1e-9 and seg.lines:
                seg.mark_displayed()
                events.append(DisplayEvent(seg=seg, at=t))
        self.now = t
        return events

    def pending(self, t: float) -> list[Segment]:
        """السطور التي يحين موعدها ولم تُترجم بعد — هذه أولوية الإسعاف."""
        return [
            s
            for s in self.segments
            if not s.displayed and not s.lines and self.tasks[s.id].deadline <= t + 1e-9
        ]

    # ───────────────────────── مساعدات ─────────────────────────
    def by_id(self, seg_id: str) -> Segment | None:
        for s in self.segments:
            if s.id == seg_id:
                return s
        return None

    def timeline(self) -> None:
        """يضبط الخط الزمني: مدة كافية للقراءة + لا تداخل."""
        self.composer.enforce_timeline(self.segments)

    def snapshot(self) -> list[dict[str, object]]:
        return [
            {
                "id": s.id,
                "start": round(s.start, 2),
                "end": round(s.end, 2),
                "tier": s.tier.name,
                "displayed": s.displayed,
                "quality": round(s.quality, 3),
                "lines": list(s.lines),
                "src": normalize_arabic(s.src_text)[:40],
            }
            for s in self.segments
        ]
