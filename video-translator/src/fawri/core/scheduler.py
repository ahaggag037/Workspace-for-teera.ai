"""
الشبكة البلورية — المجدول (DQC: Deadline-aware Quality Cascade).

هنا تتحوّل البصيرة إلى **رياضيات قابلة للإثبات**.

النموذج
-------
كل قطعة ترجمة `i` هي مهمة زمن-حقيقي:

    release  r_i = 0                     (وضع الملف: الصوت كله متاح من الثانية صفر)
    deadline d_i = a_i + Δ               (الموعد = بداية نطقها + تأخير الراحة)
    mandatory m_i                        (مسوّدة — إن فات موعدها: شاشة بلا ترجمة)
    optional  o_i                        (تحسين — كل وحدة ترفع الجودة بعائد متناقص)

الجودة كدالة في الحساب (مقعّرة، متزايدة، متشبعة):

    Q_i(c) = 0                                            إن c < m_i
           = q_base + (q_max - q_base)·(1 - e^{-κ_i·(c-m_i)})   иначе

المسألة:
    maximize   Σ Q_i(c_i)
    subject to Σ_{j: d_j ≤ t} c_j ≤ C(t)   ∀t          (سعة GPU التراكمية)

لماذا هذا «ترتيب ذرّات» لا مجرد كود؟
    لأن الخاصية التي نريدها — «القطعة تصل في موعدها وبأعلى جودة ممكنة» —
    لا يملكها المجدول وحده، ولا نموذج الجودة وحده، ولا الموديل وحده.
    إنها تنبثق من **تلازم الثلاثة** في شبكة واحدة.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .models import Task

__all__ = [
    "Q_BASE",
    "Q_CEILING",
    "quality_of",
    "marginal_gain",
    "is_schedulable",
    "simulate",
    "recommend_delta",
    "DQCScheduler",
]

Q_BASE = 0.62     # جودة المسوّدة (ستريمنج حي)
Q_CEILING = 1.00  # سقف الجودة (تحسين لانهائي)

_EPS = 1e-9


# ──────────────────────────── دالة الجودة ────────────────────────────
def quality_of(
    task: Task,
    cost: float | None = None,
    base: float = Q_BASE,
    ceiling: float = Q_CEILING,
) -> float:
    """Q_i(c) — الجودة المتوقّعة لقطعة بعد إنفاق `cost` من الحساب.

    κ (الصعوبة) تحدّد **سرعة الإشباع**: قطعة صعبة (κ كبير) تستفيد أسرع من
    التحسين لأن المسوّدة فيها أخطاء أكثر قابلة للتصحيح. هذا هو بالضبط ما يجعل
    الـ water-filling يوجّه الحساب للقطع الصعبة تلقائياً — بلا قاعدة يدوية.
    """
    c = task.spent if cost is None else cost
    if c < task.mandatory_cost - _EPS:
        return 0.0
    extra = max(0.0, c - task.mandatory_cost)
    return base + (ceiling - base) * (1.0 - math.exp(-task.difficulty * extra))


def marginal_gain(task: Task, quantum: float = 0.05) -> float:
    """dQ/dc — الكسب الحدي لكل وحدة حساب. هذا هو «قانون الترابط» في الشبكة:
    الوحدة التالية من الحساب تذهب إلى حيث تعطي أكبر كسب، لا إلى حيث تصادف.
    """
    if not task.done_mandatory:
        return math.inf  # الإلزامي أولاً: كسبه غير منتهٍ (بدونه لا يظهر شيء)
    return (quality_of(task, task.spent + quantum) - quality_of(task)) / quantum


# ──────────────────────────── الجدولية ────────────────────────────
def is_schedulable(tasks: list[Task], throughput: float, utilization: float = 1.0) -> bool:
    """اختبار الجدولية لجهاز واحد بترتيب EDF.

    الشرط الكلاسيكي: لكل مهمة بترتيب المواعيد،
        Σ_{j: d_j ≤ d_i} m_j  ≤  d_i · throughput · utilization

    لماذا يهمّنا؟ لأنه **يستبدل جدول البروفايلات المكتوب باليد**:
    بدل أن نقول «هذا الجهاز متوسط»، نقول: «هذا الجهاز لا يستطيع جدولة
    الأجزاء الإلزامية عند Δ = ٤ث ⇒ انتقال تلقائي إلى وضع pre-pass فقط».
    قرار مستنبَط، لا تخمين.
    """
    if throughput <= 0:
        return False
    cumulative = 0.0
    for t in sorted(tasks, key=lambda x: x.deadline):
        cumulative += t.mandatory_cost
        if cumulative > t.deadline * throughput * utilization + _EPS:
            return False
    return True


# ──────────────────────────── المحاكاة ────────────────────────────
def simulate(
    tasks: list[Task],
    throughput: float,
    quantum: float = 0.05,
    base: float = Q_BASE,
    ceiling: float = Q_CEILING,
) -> dict[str, float]:
    """يحاكي تشغيل النظام كاملاً ويعيد جودة كل قطعة.

    الآلية (وهي جوهر التصميم):
      ١. نعالج الأجزاء **الإلزامية** بترتيب EDF (الموعد الأقرب أولاً).
      ٢. كل فائض زمن قبل الموعد التالي ننفقه على **أعلى كسب حدّي**
         بين القطع التي (أ) أنهت الإلزامي، و(ب) موعدها لم يفت بعد.

    النتيجة الانبثاقية — وهي بيت القصيد:
        القطعة الأولى ميزانيتها = (a₁ + Δ) · throughput فقط  ⇒  محرومة حسابياً
        القطعة الأخيرة أمامها كل السعة                        ⇒  غنية حسابياً
        ⇒ **Δ هو المتغيّر الذي يشتري جودة الدقائق الأولى.**
    """
    if throughput <= 0:
        return {t.seg_id: 0.0 for t in tasks}

    work = [replace(t, spent=0.0) for t in tasks]
    work.sort(key=lambda t: t.deadline)

    qualities: dict[str, float] = {}
    now = 0.0

    for t in work:
        # ١) الجزء الإلزامي
        now += t.mandatory_cost / throughput
        t.spent += t.mandatory_cost
        if now > t.deadline + _EPS:
            qualities[t.seg_id] = 0.0  # فاتها الموعد → لا ترجمة
            continue

        # ٢) استثمار الفائض قبل موعد هذه القطعة
        slack_wall = t.deadline - now
        budget = slack_wall * throughput
        while budget > _EPS:
            candidates = [
                x
                for x in work
                if x.done_mandatory
                and now < x.deadline - _EPS            # ← لا تحسين بعد موعد القطعة نفسها
                and quality_of(x, base=base, ceiling=ceiling) < ceiling - 1e-3
            ]
            if not candidates:
                break
            best = max(candidates, key=lambda x: marginal_gain(x, quantum))
            step = min(quantum, budget)
            best.spent += step
            budget -= step

        now = t.deadline  # استهلكنا الفائض كاملاً في التحسين
        qualities[t.seg_id] = quality_of(t, base=base, ceiling=ceiling)

    return qualities


def recommend_delta(
    tasks: list[Task],
    throughput: float,
    q_floor: float = 0.80,
    delta_max: float = 15.0,
    critical_prefix: int | None = None,
    tol: float = 0.05,
) -> float | None:
    """يحسب `Δ*` — **أصغر** تأخير يضمن جودة دنيا للقطع الأولى.

    هذا هو الفرق بين «مهندس يضبط رقماً» و«مهندس يشتقّ رقماً»:
    Δ عندنا ليس معلمة ضبط (tuning knob) بل **حلّ معادلة**.

    يبحث أصغر Δ يحقق:  Q_i ≥ q_floor  لكل قطعة في البادئة الحرجة.
    يُعيد None إن لم يوجد حلّ حتى Δ_max ⇒ **اختبار الجدولية فشل**
    ⇒ القرار: نُعطّل الستريمنج وننتقل إلى pre-pass فقط.
    """
    if not tasks:
        return 0.0
    base_deadlines = [t.deadline for t in tasks]
    n = critical_prefix or max(1, min(len(tasks), 8))

    def quality_at(delta: float) -> float:
        shifted = [replace(t, deadline=d + delta) for t, d in zip(tasks, base_deadlines)]
        q = simulate(shifted, throughput)
        ordered = [q[t.seg_id] for t in sorted(shifted, key=lambda x: x.deadline)[:n]]
        return min(ordered) if ordered else 0.0

    if quality_at(delta_max) < q_floor:
        return None  # الجهاز لا يستطيع — حتى مع أقصى تأخير

    lo, hi = 0.0, delta_max
    while hi - lo > tol:
        mid = (lo + hi) / 2.0
        if quality_at(mid) >= q_floor:
            hi = mid
        else:
            lo = mid
    return round(hi, 2)


# ──────────────────────────── المجدول الحي ────────────────────────────
@dataclass
class DQCScheduler:
    """المجدول أثناء التشغيل: قرار واحد في كل «نبضة» — ماذا نحسب الآن؟

    القاعدتان (بهذا الترتيب الحرفي):
      ١. إن وُجدت مهمة إلزامية → نفّذ أقربها موعداً (EDF). هذه قاطعة: لا مفاضلة.
      ٢. وإلا → نفّذ الأعلى **كسباً حدّياً** بين القطع التي لم يفت موعدها.

    لماذا EDF أولاً؟ لأن الكسب الحدّي للإلزامي = ∞ رياضياً:
    بلا مسوّدة لا يظهر شيء، وكل تحسين لاحق بلا قيمة.
    """

    throughput: float = 1.0
    quantum: float = 0.05

    def pick(self, tasks: list[Task], now: float) -> Task | None:
        """يختار المهمة التالية. `now` بالثواني من بداية الجلسة."""
        live = [t for t in tasks if t.deadline > now + _EPS]

        # ١) الإلزامي أولاً — EDF
        mandatory = [t for t in live if not t.done_mandatory]
        if mandatory:
            return min(mandatory, key=lambda t: t.deadline)

        # ٢) التحسين — أعلى كسب حدّي (water-filling)
        refinable = [
            t
            for t in live
            if quality_of(t) < Q_CEILING - 1e-3 and t.slack > _EPS
        ]
        if not refinable:
            return None
        return max(refinable, key=lambda t: marginal_gain(t, self.quantum))

    def step(self, tasks: list[Task], now: float) -> tuple[Task | None, float]:
        """يختار مهمة **ويتقدّم بالزمن**. يُعيد (المهمة، الزمن المستهلك)."""
        task = self.pick(tasks, now)
        if task is None:
            return None, 0.0
        cost = min(self.quantum, max(0.0, task.deadline - now) * self.throughput)
        if cost <= _EPS:
            return None, 0.0
        task.spent += cost
        return task, cost / self.throughput
