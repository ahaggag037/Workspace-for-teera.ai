"""
ذرّة الجهاز — من مواصفات **مقيسة** إلى ثوابت **مشتقّة**.

هذه الذرة وُجدت لتقتل الفرضيتين المعلَّمتين بـ ⚠️ في الوثيقة 07:
    · Q_BASE         (جودة المسوّدة)
    · mandatory_cost (تكلفة المسوّدة)

`mandatory_cost` لم يعد رقماً مكتوباً باليد. صار **دالّة**:

    m_i =  dur_i / ASR_speedup(الجهاز)  +  out_tokens_i / capacity_tok_s(الجهاز, batch)

════════════════════════════════════════════════════════════════════
⚠️ التصحيح المفاهيمي الذي أجبرنا عليه الاختبار (سجّله: هو أهم ما فيها)
════════════════════════════════════════════════════════════════════
النموذج الأول كان يقيس التكلفة بـ «رموز/ثانية **لكل تسلسل**».
وهذا **خطأ فيزيائي**، والاختبار كشفه.

الجهاز **مورد مشترك**: لو شغّلت ١٦ تسلسلاً في دفعة واحدة، الجهاز مشغول
نفس الوقت، لكنه أنتج ١٦× عملاً مفيداً. فما يهمّ في «هل نلحق بمؤشر
التشغيل؟» ليس سرعة تسلسل واحد، بل:

        العمل المفيد لكل ثانية من زمن الجهاز = الإنتاجية **الإجمالية**

    batch=1  : ٢٦٫٤ رمز/ث  ⇒ تكلفة ١٤ رمز = ٠٫٥٣٠ ثانية-جهاز
    batch=16 : ٤٢١   رمز/ث ⇒ تكلفة ١٤ رمز = ٠٫٠٣٣ ثانية-جهاز   ← أرخص ١٦×

وسرعة التسلسل الواحد **لا تتحسّن** بالتجميع (بل تنقص قليلاً بذاكرة KV) —
التجميع يعطي **إنتاجية** (throughput) لا **استجابة** (latency).
هذا الفرق هو بالضبط ما يميّز وضع الستريمنج عن وضع الـ pre-pass.
════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# ثوابت فيزيائية/تجريبية
KV_BYTES_PER_TOKEN = 0.0001      # ≈100KB لكل رمز سياق لموديل 600M (K و V، fp16)
EFFICIENCY = 0.55                # كفاءة تحقيق السقف النظري على كروت قديمة
VRAM_RESERVE_GB = 0.60           # احتياطي للسائق/السياق/التشتيت
DEFAULT_BATCH = 8                # دفعة الـ pre-pass الاعتيادية

# مرساة معايرة: RTX 4070 — أرقام منشورة لسرعة ASR (batched)
ANCHOR_TFLOPS = 35.0
ANCHOR_BW_GBS = 504.0
ANCHOR_ASR_REALTIME: dict[str, float] = {
    "tiny": 300.0, "base": 120.0, "small": 45.0, "medium": 15.0, "large": 5.0,
}

# أوزان الموديلات بالجيجابايت (int8 ما أمكن)
MODEL_WEIGHTS_GB: dict[str, float] = {
    "nllb-600M-int8": 0.60,
    "nllb-1.3B-int8": 1.30,
    "whisper-base-int8": 0.10,
    "whisper-small-int8": 0.28,
    "whisper-tiny-int8": 0.05,
    "qwen3-0.6B-q4": 0.40,
    "qwen3-1.7B-q4": 1.10,
    "qwen3-4B-q4": 2.50,
}

MODEL_PARAMS: dict[str, float] = {
    "nllb-600M-int8": 0.6e9, "nllb-1.3B-int8": 1.3e9,
    "qwen3-0.6B-q4": 0.6e9, "qwen3-1.7B-q4": 1.7e9, "qwen3-4B-q4": 4.0e9,
}


def quant_efficiency(compute_cap: str) -> float:
    """هل INT8 مدعوم عتادياً؟
    ≥ 7.5 → INT8 Tensor Cores (Turing+)      : 1.00
    ≥ 6.1 → DP4A (Pascal)                    : 0.85
    ≥ 5.x → Maxwell وأقدم: **محاكاة** لا عتاد : 0.70
    ⇒ نصيحة «استخدم int8 لتسريع 3-4×» **لا تنطبق** على Maxwell.
      int8 يقلّل حركة الذاكرة (مكسب)، لكن الحساب يبقى fp32 (خسارة)."""
    try:
        cap = float(compute_cap)
    except (TypeError, ValueError):
        return 1.0
    if cap >= 7.5:
        return 1.00
    if cap >= 6.1:
        return 0.85
    return 0.70


@dataclass(frozen=True)
class DeviceProfile:
    """بطاقة تعريف الجهاز — كل حقل إما **مقيس** أو **موسوم بأنه تقدير**."""

    name: str = "unknown"
    backend: str = "cpu"              # cuda | directml | cpu
    compute_cap: str = ""
    vram_gb: float = 0.0
    bandwidth_gbs: float = 0.0        # عرض النطاق الفعّال (GB/s)
    fp32_tflops: float = 0.0
    fp16_tflops: float = 0.0          # صفر إن لم تكن FP16 مفيدة
    measured: bool = False            # ⚠️ هل الأرقام من نواة قياس حقيقية؟
    cpu_cores: int = 0
    ram_gb: float = 0.0
    avx2: bool | None = None
    second_devices: tuple[str, ...] = field(default_factory=tuple)

    def tflops(self) -> float:
        """أفضل دقة حسابية متاحة فعلاً.
        على Maxwell (sm_50) لا توجد Tensor Cores، وFP16 قد لا يكون أسرع من FP32،
        فنأخذ الأكبر تحفّظاً بدل افتراض تسريع غير موجود."""
        return max(self.fp32_tflops, self.fp16_tflops)

    def is_gpu(self) -> bool:
        return self.backend in ("cuda", "directml")


# ══════════════════════════════════════════════════════════════════
def capacity_tok_s(
    p: DeviceProfile,
    weights_gb: float,
    params: float | None = None,
    batch: int = 1,
    efficiency: float = EFFICIENCY,
    quantization: str = "int8",
) -> float:
    """★★ الإنتاجية **الإجمالية** — العمل المفيد لكل ثانية جهاز. ★★

    هذا هو المقاس الصحيح لحساب التكلفة، لأن الجهاز مورد مشترك.

        aggregate = B · BW·η / (W + B·L·kv)      ← مقيد بالذاكرة
                    مقارنةً بـ
                    TFLOPS·η / (2·params)         ← مقيد بالحساب
        ويُضرب η في معامل كفاءة التكميم (إن كان int8 على عتاد قديم).
    """
    if p.bandwidth_gbs <= 0 or weights_gb <= 0 or batch < 1:
        return 0.0
    eff = efficiency * (quant_efficiency(p.compute_cap) if quantization == "int8" else 1.0)
    denom = weights_gb + batch * KV_BYTES_PER_TOKEN
    bw_bound = batch * p.bandwidth_gbs * eff / denom
    if params and p.tflops() > 0:
        compute_bound = p.tflops() * 1e12 * eff / (2.0 * params)
        return min(bw_bound, compute_bound)
    return bw_bound


def latency_tok_s(p: DeviceProfile, weights_gb: float, params: float | None = None,
                  batch: int = 1) -> float:
    """سرعة **التسلسل الواحد** — مقياس الاستجابة لا السعة.
    التجميع لا يحسّنها (بل تنقص قليلاً بزيادة حركة KV).
    تُستخدم للحكم على وضع الستريمنج الحرِج زمنياً."""
    return capacity_tok_s(p, weights_gb, params, batch) / max(1, batch)


def estimate_asr_speedup(p: DeviceProfile, model: str = "base") -> float:
    """سرعة ASR مقابل الزمن الحقيقي (× realtime).
    تحجيم **هندسي** (حساب × نطاق ترددي) من مرساة RTX 4070:
    كلا الموردين لازم، فلا يعوّض أحدهما الآخر."""
    base = ANCHOR_ASR_REALTIME.get(model, ANCHOR_ASR_REALTIME["base"])
    if not p.is_gpu():
        # ⚠️ كان هذا المسار يتجاهل `model` بالكامل (خطأ كشفه المِسبار)
        cpu_base = 0.6 * (p.cpu_cores / 8.0) * (1.5 if p.avx2 else (1.0 if p.avx2 is None else 0.7))
        rel = base / ANCHOR_ASR_REALTIME["base"]
        return cpu_base * rel
    cr = min(1.0, p.tflops() / ANCHOR_TFLOPS)
    br = min(1.0, p.bandwidth_gbs / ANCHOR_BW_GBS)
    return base * math.sqrt(max(cr, 1e-9) * max(br, 1e-9))


def mandatory_cost(
    p: DeviceProfile,
    duration_s: float,
    out_tokens: int = 14,
    asr_model: str = "base",
    mt_model: str = "nllb-600M-int8",
    batch: int = DEFAULT_BATCH,
) -> float:
    """★★ هذه هي الدالّة التي تحلّ محل الثابت ⚠️ `mandatory_cost = 0.35` ★★

    تكلفة المسوّدة لقطعة = حصة ASR + حصة الترجمة من **سعة الجهاز**.
    """
    asr_x = estimate_asr_speedup(p, asr_model)
    if asr_x <= 0:
        return float("inf")
    cost_asr = duration_s / asr_x
    weights = MODEL_WEIGHTS_GB.get(mt_model, 0.6)
    params = MODEL_PARAMS.get(mt_model)
    tot_s = capacity_tok_s(p, weights, params, batch)
    if tot_s <= 0:
        return float("inf")
    return cost_asr + out_tokens / tot_s


def fits_in_vram(p: DeviceProfile, models: list[str], reserve: float = VRAM_RESERVE_GB) -> bool:
    return sum(MODEL_WEIGHTS_GB.get(m, 0.0) for m in models if m) + reserve <= p.vram_gb


def vram_budget(p: DeviceProfile, models: list[str], reserve: float = VRAM_RESERVE_GB) -> dict:
    need = sum(MODEL_WEIGHTS_GB.get(m, 0.0) for m in models if m) + reserve
    return {
        "needed_gb": round(need, 2),
        "available_gb": round(p.vram_gb, 2),
        "headroom_gb": round(p.vram_gb - need, 2),
        "fits": need <= p.vram_gb,
    }


def realtime_headroom(stack: dict, p: DeviceProfile, duration_s: float = 3.0,
                      out_tokens: int = 14, batch: int = DEFAULT_BATCH) -> float:
    """كم مرة أسرع من الزمن الحقيقي يستطيع الجهاز إنتاج المسوّدات؟
    > 1 ⇒ يلحق. < 1 ⇒ يجب pre-pass كامل قبل التشغيل."""
    cost = mandatory_cost(p, duration_s, out_tokens, stack["asr"], stack["mt"], batch)
    if stack.get("refiner"):
        w = MODEL_WEIGHTS_GB[stack["refiner"]]
        par = MODEL_PARAMS[stack["refiner"]]
        tot = capacity_tok_s(p, w, par, batch)
        if tot > 0:
            cost += out_tokens / tot
    return duration_s / cost if cost > 0 else 0.0


# ══════════════════════════════════════════════════════════════════
_MT_ORDER = ("nllb-1.3B-int8", "nllb-600M-int8")
_REFINER_ORDER = ("qwen3-1.7B-q4", "qwen3-0.6B-q4", None)
_ASR_ORDER = ("small", "base", "tiny")


def recommend_model_stack(p: DeviceProfile, min_headroom: float = 1.5) -> dict:
    """اختيار حزمة الموديلات **الممكنة فعلاً** — بحث معجمي (أفضل جودة تفي بالقيود).

    القيود: (١) تتّسع في VRAM  (٢) هامش الزمن الحقيقي ≥ min_headroom في وضع الدفعات.
    المنطق ليس «أفضل موديل» بل «أفضل موديل يستطيع اللحاق بمؤشر التشغيل».
    """
    headroom_ok = 1.0 if not p.is_gpu() else min_headroom
    for mt in _MT_ORDER:
        for refiner in _REFINER_ORDER:
            for asr in _ASR_ORDER:
                stack = {"asr": asr, "mt": mt, "refiner": refiner}
                models = [mt, f"whisper-{asr}-int8"] + ([refiner] if refiner else [])
                if not fits_in_vram(p, models):
                    continue
                if realtime_headroom(stack, p, batch=DEFAULT_BATCH) >= headroom_ok:
                    return stack
    # لا شيء يفي ⇒ أصغر حزمة ممكنة، موسومة صراحةً بأنها دون المستوى
    return {"asr": "tiny", "mt": "nllb-600M-int8", "refiner": None,
            "degraded": True,
            "note": "لا حزمة تفي بالحد الأدنى — النظام سيعمل في وضع pre-pass كامل"}


def batch_gain(p: DeviceProfile, model: str = "nllb-600M-int8",
               batch: int = DEFAULT_BATCH) -> float:
    """مكاسب التجميع: كم مرة أنتج الجهاز عملاً مفيداً أكثر بنفس ثانية الجهاز؟"""
    w = MODEL_WEIGHTS_GB.get(model, 0.6)
    par = MODEL_PARAMS.get(model)
    one = capacity_tok_s(p, w, par, 1)
    many = capacity_tok_s(p, w, par, batch)
    return many / one if one > 0 else 0.0
