"""
الذرة الأولى — Segment.

لماذا هذه «ذرة»؟ لأنها أصغر وحدة تحمل **قراراً غير قابل للتجزئة**:
«هل يجوز تغيير هذا السطر؟» كل شيء آخر في النظام يتفرّع عن هذا القرار.

الرابطة الذرّية (THE BOND):
    displayed == True  ⇒  tgt_text / start / end / lines  تصبح **غير قابلة للتغيير**

لا توجد هذه الرابطة في أي مكوّن بمفرده. الـ ASR لا يعرفها. الـ MT لا يعرفها.
واجهة المستخدم لا تعرفها. إنها **رابطة بين الذرات** — وكما في الفولاذ،
الصلابة (هنا: انعدام الرفرفة) خاصية **انبثاقية** للشبكة لا للمكوّن.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

__all__ = [
    "Tier",
    "Segment",
    "Task",
    "ImmutableCueError",
    "TIER_NAME",
]


class Tier(IntEnum):
    """طبقات الجودة — **رتيبة**: يُسمح بالترقية فقط، ولا يُسمح بالتنزيل أبداً.

    الرتابة هنا ليست تفضيلاً جمالياً: هي ما يجعل «عدم الرفرفة» قابلاً للإثبات.
    لو سُمح بالتنزيل، لأمكن أن تظهر نسخة أسوأ بعد نسخة أفضل = رفرفة مقنّعة.
    """

    DRAFT = 0    # ستريمنج حي — سريع، جودة مقبولة
    SOLID = 1    # pre-pass — نص ثابت أدق
    REFINED = 2  # تمريرة تحسين بموديل أكبر + سياق أوسع


TIER_NAME = {Tier.DRAFT: "مسودة", Tier.SOLID: "ثابت", Tier.REFINED: "محسّن"}

# الحقول التي تتجمّد بعد العرض —— هذه هي الرابطة الذرّية ذاتها
_FROZEN_AFTER_DISPLAY = frozenset({"tgt_text", "start", "end", "lines"})


class ImmutableCueError(RuntimeError):
    """يُرمى عند محاولة تغيير سطر **عُرِض بالفعل**.

    هذا الاستثناء ليس حماية من خطأ برمجي — إنه **تجسيد لقاعدة المنتج الأولى**.
    لو رأيته في سجلّاتك، فالمشروع انكسر من جذوره، لا في تفصيلة.
    """


@dataclass
class Segment:
    """وحدة ترجمة واحدة = سطر (أو سطران) يظهران على الشاشة في فترة زمنية.

    الحقول «الذرّية»:
        id         : هوية ثابتة لا تتغيّر (تربط Segment بـ Task)
        start/end  : نافذة العرض بالثواني من بداية الملف
        src_text   : النص المُفرَّغ من الصوت
        tgt_text   : الترجمة العربية
        tier       : طبقة الجودة (رتيبة ↑ فقط)
        quality    : تقدير جودة ٠..١ (من QE أو المجدول)
        displayed  : هل ظهر على الشاشة؟ ← **المفتاح الذرّي**
        speaker    : هوية المتكلّم (للجندر والسجل)
        lines      : السطور بعد التقطيع العربي
    """

    id: str
    start: float
    end: float
    src_text: str = ""
    src_lang: str = ""
    tgt_text: str = ""
    tier: Tier = Tier.DRAFT
    quality: float = 0.0
    displayed: bool = False
    speaker: str | None = None
    lines: tuple[str, ...] = field(default_factory=tuple)

    # ───────────────────────── الرابطة الذرّية ─────────────────────────
    def __setattr__(self, name: str, value: object) -> None:
        """يفرض التجمّد بعد العرض على مستوى **اللغة نفسها**، لا على مستوى الاصطلاح.

        اخترنا `__setattr__` لا دالة حارس، لأن الحارس يُنسى ويُنسى،
        أما هذا فيُطبَّق حتى على كود لم يقرأ الوثيقة.
        """
        if name in _FROZEN_AFTER_DISPLAY and getattr(self, "displayed", False):
            current = getattr(self, name, None)
            if current != value:
                raise ImmutableCueError(
                    f"محاولة تغيير '{name}' في السطر {self.id!r} بعد عرضه. "
                    f"الحالي={current!r} الجديد={value!r}. "
                    f"هذا يكسر قاعدة المنتج الأولى: السطر المعروض لا يتغيّر أبداً."
                )
        object.__setattr__(self, name, value)

    # ───────────────────────── انتقالات الحالة ─────────────────────────
    def mark_displayed(self) -> None:
        """يُستدعى من العارض لحظة ظهور السطر. بعدها: تجمّد نهائي."""
        object.__setattr__(self, "displayed", True)

    def render_text(self) -> str:
        """النص المُرسَم: السطور المقطّعة إن وُجدت، وإلا النص الخام."""
        return "\n".join(self.lines) if self.lines else self.tgt_text

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def __repr__(self) -> str:  # تشخيص مقروء
        return (
            f"<Segment {self.id} [{self.start:.2f}→{self.end:.2f}] "
            f"{TIER_NAME[self.tier]}{' 👁' if self.displayed else ''} "
            f"{self.render_text()!r}>"
        )


@dataclass
class Task:
    """الذرة المقابلة لـ Segment **في فضاء الجدولة** — الرابطة بينهما هي `id`.

    لماذا فصلناهما؟ لأن المجدول يرى أبعاداً لا تعرفها الترجمة:
        release         : متى يصبح العمل ممكناً (٠ في وضع الملف — كل شيء متاح الآن)
        deadline        : الموعد النهائي = زمن الظهور على الشاشة
        mandatory_cost  : تكلفة المسوّدة (إلزامية)
        difficulty κ    : صعوبة القطعة ← يحدّد كم تستفيد من التحسين
    تكفي نظرة واحدة لترى أن **كل هذه الأبعاد زمنية** — والترجمة لا تعرف الزمن،
    والمجدول لا يعرف اللغة. الرابطة (`seg_id`) هي ما يخلق النظام الواحد.
    """

    seg_id: str
    release: float = 0.0
    deadline: float = 0.0
    mandatory_cost: float = 1.0
    difficulty: float = 1.0
    spent: float = 0.0

    @property
    def done_mandatory(self) -> bool:
        return self.spent >= self.mandatory_cost - 1e-9

    @property
    def slack(self) -> float:
        return self.deadline - self.release
