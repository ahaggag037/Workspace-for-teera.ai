# 03 — المعمارية التقنية (Tech Architecture)

> الهدف من الملف ده: يبقى وثيقة executable — نقدر نديها لـ Codex وهو يبدأ يبني.

---

## 1. قرارات التكنولوجيا (وليه)

| الطبقة | القرار | البديل المرفوض | ليه |
|---|---|---|---|
| لغة | **Python 3.12** | Rust/C++ | أسرع تطوير، أغنى ML ecosystem، وCodex ممتاز فيه. الأداء الحرج كله جوه موديلات C++ أصلاً |
| UI | **PySide6 (Qt 6)** | Electron/Tauri | Qt فيه **HarfBuzz** → تشكيل عربي و RTL مظبوط أوتوماتيك. وElectron تقيل |
| تشغيل الفيديو | **libmpv** عبر `python-mpv`، تضمين في Qt بـ `--wid` | QtMultimedia / VLC | mpv يشغّل أي كودك، A/V sync ممتاز، تحكم كامل في التأخير والسرعة |
| الصوت (ملف) | **ffmpeg subprocess** → s16le 16kHz mono | PyAV | أبسط، وأقل تعقيد بناء |
| الصوت (نظام) | **pyaudiowpatch** (WASAPI loopback) على Windows / `soundcard`跨平台 | — | — |
| VAD | **Silero VAD v5** (ONNX, CPU, 2MB) | WebRTC VAD | أدق، خفيف |
| ASR | **Qwen3-ASR** (أساسي) / **faster-whisper turbo** (بديل+pre-pass) | — | شوف 01-research |
| MT | **Qwen3-4B-Instruct GGUF** عبر **llama.cpp** (Vulkan/CUDA/CPU) + **NLLB-200-1.3B CTranslate2** كـ draft | transformers فقط | llama.cpp يشتغل على AMD/Intel/NVIDIA بنفس binary |
| IPC داخلي | **Python asyncio + queues** مؤقتاً (قابل للاستبدال بـ ZeroMQ لو احتجنا عمليات منفصلة) | microservices | تعقيد أقل في البداية |
| التغليف | **PyInstaller** → portable ZIP + installer اختياري | — | "افتح واشتغل" |
| المنصة الأولى | **Windows 10/11 x64** | — | السوق + loopback أسهل |

---

## 2. البنية الكبيرة (Big Picture)

```
                        ┌──────────────────────────────────────────┐
                        │            UI Layer (PySide6)            │
                        │  MainWindow │ PlayerWidget │ OverlayWin   │
                        │  Settings │ TrayIcon │ Drag&Drop          │
                        └───────────────┬──────────────────────────┘
                                        │ signals (Qt)
┌───────────────────────────────────────▼──────────────────────────────────────┐
│                          Orchestrator  (core/engine.py)                      │
│   يملك الـ session، يحسب الوقت، يقرر: draft vs solid vs refined، ويدير الكاش  │
└───┬──────────────┬──────────────┬───────────────┬───────────────┬────────────┘
    │              │              │               │               │
┌───▼───┐   ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ Audio │   │     VAD     │ │    ASR    │ │  Translator │ │  Subtitle   │
│ Source│   │  Silero v5  │ │ Qwen3-ASR │ │ Qwen3-4B +  │ │  Composer   │
│       │   │             │ │ / whisper │ │ NLLB        │ │  (RTL/CPS)  │
│ ffmpeg│   │             │ │           │ │ + Context   │ │             │
│ loopbk│   │             │ │           │ │ + Glossary  │ │             │
└───────┘   └─────────────┘ └───────────┘ └─────────────┘ └──────┬──────┘
                                                                  │
                                                          ┌───────▼───────┐
                                                          │  Overlay /    │
                                                          │  mpv sub /    │
                                                          │  SRT export   │
                                                          └───────────────┘

        ╔══════════════════════════════════════════════════════════╗
        ║  PrePass Worker (خلفية) — نفس المكونات، بس بلا pacing     ║
        ║  يقرأ الصوت كله بأسرع ما يمكن ويملأ الكاش قبل الـplayhead ║
        ╚══════════════════════════════════════════════════════════╝
                                    │
                          ┌─────────▼──────────┐
                          │  Cache (SQLite)    │
                          │  key: filehash +   │
                          │  modelset + dialect│
                          └────────────────────┘
```

---

## 3. نموذج البيانات (Data Model)

```python
@dataclass
class Segment:
    id: str                    # uuid
    start: float               # ثانية من بداية الملف
    end: float
    src_text: str              # نص أصلي (مُفرّغ)
    src_lang: str              # "en", "ja", ...
    tgt_text: str              # الترجمة
    tier: Literal["draft","solid","refined"]
    quality: float             # ثقة اختيارية
    displayed: bool = False    # ⚠️ لو True → ممنوع التغيير (قاعدة عدم الرفرفة)
```

```sql
-- cache.sqlite
CREATE TABLE files (
  hash TEXT PRIMARY KEY,      -- SHA256 لأول+آخر 1MB + الحجم
  path TEXT, duration REAL
);
CREATE TABLE segments (
  file_hash TEXT, modelset TEXT, dialect TEXT,
  idx INTEGER, start REAL, end REAL,
  src TEXT, tgt TEXT, tier TEXT,
  PRIMARY KEY (file_hash, modelset, dialect, idx)
);
```

---

## 4. خط الأنابيب بالتفصيل

### 4.1 مصدر الصوت
```python
class AudioSource(Protocol):
    def read(self, n_frames) -> np.ndarray: ...   # s16le 16kHz mono
    @property
    def clock(self) -> float: ...                 # موضع التشغيل الحالي (ثانية)

class FileAudioSource(AudioSource):
    """ffmpeg -i FILE -vn -f s16le -ac 1 -ar 16000 -  → pipe
       يقرأ **أسرع** من realtime (غير مقيد بالتشغيل) → يغذي الـ pre-pass"""

class LoopbackAudioSource(AudioSource):
    """WASAPI loopback → realtime فقط"""
```

> 🔑 **السر:** `FileAudioSource` مش بيتبع التشغيل. الـ pre-pass يقدر يعالج ٣ دقائق من الصوت في ١٠ ثواني.

### 4.2 VAD + Segmentation
- Silero VAD → جُمل (utterances) بين ١.٢ث و ١٥ث (قص قسري عند ١٥ث).
- `min_silence_ms = 400` قابل للضبط (بيأثر على الـ latency مباشرة).
- كل utterance → `Segment(start, end, audio_slice)`.

### 4.3 ASR
```
interface ASR:
    transcribe(audio_slice) -> (text, lang)          # offline / prepass
    stream() -> AsyncIterator[(partial_text, final)]  # live
```
- Backend A: `Qwen3ASRBackend` (llama-server + mmproj، أو vLLM على WSL/Linux)
- Backend B: `FasterWhisperBackend` (CTranslate2، `turbo`) + LocalAgreement للستريمنج
- Backend C: `MockASR` (للاختبارات بدون موديلات) ✅ لازم من أول يوم

### 4.4 الترجمة (Translator)
```python
class Translator:
    def translate(self, segments: list[Segment], ctx: Context) -> list[Segment]
        # ctx = last K segments + glossary + domain + dialect profile + length rules
```

**البرومبت (نموذج أولي):**
```
أنت مترجم محترف من {SRC} إلى العربية ({DIALECT_PROFILE}).

السياق السابق (لا تترجمه، استخدمه للاتساق فقط):
{LAST_K}

قاموس المصطلحات (التزم به):
{GLOSSARY}

مجال الفيديو: {DOMAIN}

قواعد صارمة:
- ترجم السطور التالية فقط. رقم كل سطر: [1] [2] ...
- كل سطر ≤ 42 حرفاً، سطرين كحد أقصى.
- استخدام {DIALECT_RULES}
- بدون تشكيل. علامات عربية (، ؛ ؟). أرقام غربية.
- حافظ على المعنى والروح، مش الحرفية.
- لا تضف شروحات ولا تعليقات.

النص:
{SEGMENTS}
```
> 💡 **تجميع الدفعات (batching):** نترجم ٤–٨ سطور في نداء واحد (الأسطر القصيرة) لأجل السرعة، وسطر واحد للأسطر الطويلة.

### 4.5 الملحن (SubtitleComposer) — الشغل العربي الحقيقي
- يقبل الترجمة → يطبق:
  - **تنظيف**: إزالة أي هلوسة/تكرار/وسوم
  - **DialectLinter** (للمصري): كشف الفصحى المتسللة + إعادة الصياغة
  - **تقطيع**: ⚠️ **المعايير الدولية للغات RTL/العربية تختلف عن الإنجليزية**:
    - **CPL (حرف/سطر): ٣٢–٣٦ للعربية** (لا ٤٢ —那是 للاتينية)
      [5](https://www.studio-fugu.com/blog-posts/your-ultimate-guide-to-multilingual-subtitling)
    - **CPS (حرف/ثانية): الهدف ١٣–١٥، الحد الأقصى ١٥–١٨**
      (SUBTLE: متوسط ١٢–١٥، أقصى ١٦–١٧؛ TED يتساهل حتى ٢١)
      [2](https://subtle-subtitlers.org.uk/wp-content/uploads/2023/01/SUBTLE-Recommended-Quality-Criteria-for-Subtitling.pdf)
    - **المدة**: الأدنى ~١ث (تجنّب أقل من ١ث)، الأقصى ٦ث
      [2](https://subtle-subtitlers.org.uk/wp-content/uploads/2023/01/SUBTLE-Recommended-Quality-Criteria-for-Subtitling.pdf)
    - **يمنع الكسر عند**: `الـ+`، حروف الجر، `و` العطف، الضمائر المتصلة
    - **تفريع الأسطر بالتساوي** قدر الإمكان، والكسر عند علامات الترقيم
  - ⚠️ **تصحيح مُسجَّل (2026-09-24)**: كنت افترضت ٤٢ حرف/١٤ CPS في النسخة الأولى —
    البحث صحّح ذلك. العربية RTL تحتاج سطراً أقصر ووقتاً أطول.
  - **منع التداخل** بين السطور
  - **قاعدة عدم الرفرفة**: لو `segment.displayed == True` → ارفض أي تحديث

### 4.6 العرض (Renderer)
- **Qt widget** شفاف، `Qt.WindowStaysOnTopHint`، `Qt.FramelessWindowHint`، اختياري `WA_TransparentForMouseEvents`
- الرسم عبر `QTextDocument` + `QTextOption(textDirection=RightToLeft)` → **HarfBuzz يتكفل بالتشكيل والوصل**
- الخيارات: خط (Cairo / Noto Naskh / Amiri / Tajawal مضمّنة)، حجم، لون، حد (outline)، ظل، خلفية شبه شفافة
- نفس الـ widget يُستخدم في:
  1. وضع المشغّل (موضعه فوق منطقة الفيديو)
  2. وضع "ترجم كل حاجة" (fullscreen bottom bar)

---

## 5. ميزانية التأخير (Latency Budget)

### مسار الستريمنج (tier = draft)
| المرحلة | التأخير |
|---|---|
| VAD endpointing (صمت ٤٠٠ms) | ٣٠٠–٦٠٠ ms |
| ASR streaming delay (Voxtral 480ms / Qwen window) | ٤٠٠–٨٠٠ ms |
| تثبيت الجملة + LocalAgreement | ١٠٠–٢٠٠ ms |
| MT أول توكن (Qwen3-4B Q4 على GPU متوسط) | ٢٠٠–٥٠٠ ms |
| الملحن + الرسم | ~٣٣ ms |
| **المجموع** | **~1.1 – 2.0 ثانية** |

### واللي المستخدم بيحسّه
| الوضع | الإحساس |
|---|---|
| `live` (بدون تأخير تشغيل) | تأخير ملحوظ ~1.5ث — مقبول |
| **`comfort` (الافتراضي): نأخر التشغيل ٤ ثواني** | **صفر إحساس بالتأخير — الترجمة سابقة** |
| `cinema` (pre-pass يسبق) | مثالي ١٠٠٪، نص ثابت |

> 🎯 **الافتراضي = `comfort`**: نأخر الفيديو ٣–٥ ثواني (الناس أصلاً بتأخر الترجمة يدوياً)، ونكسب وقت كافي إن النص يوصل **نهائي مش مسوّدة**. تجربة "الترجمة جاهزة قبل الكلمة".

---

## 6. حسابات الـ Pre-pass (إثبات الجدوى)

فيديو ٦٠ دقيقة، GPU متوسط (RTX 3060 12GB):
```
ASR  : Qwen3-ASR / whisper-turbo   ~8-15x realtime →  4 - 8 دقيقة
MT   : ~9000 سطر ÷ batches         ~600 tok/s      →  4 - 7 دقيقة
───────────────────────────────────────────────────────────────
الإجمالي                                             8 - 15 دقيقة
لكنه أسرع من التشغيل بـ ~5x → بعد ٢-٤ دقائق من بداية الفيلم،
الـ pre-pass يبقى ahead للأبد → بقية الفيلم بجودة "solid/refined"
```
وعلى CPU بس؟ whisper-small/base يوصل ١٥–٢٠x realtime → الـ pre-pass لسه أسرع من realtime ✅ (الستريمنج بس هيبقى بطيء → نعطّله).

---

## 7. ملفات التعريف حسب الجهاز (Hardware Profiles)

| الملف | VRAM | ASR | MT | الستريمنج |
|---|---|---|---|---|
| **High** (≥12GB) | 12GB+ | Qwen3-ASR-1.7B | Qwen3-8B / ALLaM-7B | ✅ ممتاز |
| **Medium** (8GB) | 8GB | Qwen3-ASR-1.7B (int8) | Qwen3-4B Q5_K_M | ✅ جيد |
| **Low** (4–6GB) | 4GB | faster-whisper turbo | Qwen3-4B Q4 + NLLB draft على CPU | ⚠️ مقبول |
| **CPU-only** | — | faster-whisper small/base | NLLB-1.3B CTranslate2 (سريع على CPU!) | ❌ → pre-pass فقط |

> **ملاحظة ذهبية:** CTranslate2 + NLLB-1.3B سريع بما يكفي على CPU → لحد الأجهزة الضعيفة نقدر نديها "pre-pass أوفلاين" يقبل (دقيقتين) بدل الستريمنج.

**الاكتشاف أوتوماتيكي:**
```python
def detect_profile() -> Profile:   # VRAM via torch/nvidia-smi, RAM, CPU cores
    ...
```
+ تحذير صريح للمستخدم لو جهازه تحت الحد، مع خيار "جّرب على أي حال".

---

## 8. هيكل المستودع (Repo Layout)

```
video-translator/
├─ README.md
├─ pyproject.toml
├─ src/fawri/
│  ├─ __init__.py
│  ├─ app.py                     # نقطة الدخول، Qt application
│  ├─ core/
│  │  ├─ engine.py               # الـ Orchestrator (قلب النظام)
│  │  ├─ models.py               # Segment, Context, Profile, dataclasses
│  │  ├─ scheduler.py            # draft/solid/refined tiers + playhead tracking
│  │  ├─ cache.py                # SQLite translation memory
│  │  └─ config.py               # إعدادات + persistence
│  ├─ audio/
│  │  ├─ base.py                 # AudioSource protocol
│  │  ├─ file_source.py          # ffmpeg decode
│  │  ├─ loopback_source.py      # WASAPI
│  │  └─ vad.py                  # Silero
│  ├─ asr/
│  │  ├─ base.py
│  │  ├─ qwen3_asr.py
│  │  ├─ faster_whisper.py
│  │  ├─ whisper_streaming.py    # LocalAgreement
│  │  └─ mock.py                 # ⚠️ مهم جداً للتطوير بدون GPU
│  ├─ mt/
│  │  ├─ base.py
│  │  ├─ llm_translator.py       # llama.cpp server / llama-cpp-python
│  │  ├─ nllb.py                 # CTranslate2
│  │  ├─ prompts/                # system + few-shot per dialect
│  │  │  ├─ msa.j2
│  │  │  └─ egyptian.j2
│  │  ├─ glossary.py             # استخراج أسماء/مصطلحات
│  │  └─ dialect_linter.py       # كشف الفصحى + إعادة الصياغة
│  ├─ subs/
│  │  ├─ composer.py             # تنظيف + تقطيع + توقيت
│  │  ├─ arabic.py               # أدوات عربية (تشكيل/أرقام/ترقيم/CPS)
│  │  ├─ srt.py / vtt.py / txt.py
│  │  └─ renderer.py             # Qt overlay widget
│  ├─ ui/
│  │  ├─ main_window.py
│  │  ├─ player.py               # mpv embed
│  │  ├─ settings_dialog.py
│  │  └─ tray.py
│  ├─ workers/
│  │  ├─ prepass.py              # المعالجة الخلفية السريعة
│  │  └─ refine.py               # pass التحسين
│  └─ platform/
│     └─ windows.py              # WASAPI, DPI, autostart
├─ tests/
├─ tools/
│  ├─ download_models.py
│  ├─ benchmark.py               # قياس WER / COMET / latency على عينة
│  └─ build_portable.py
└─ docs/
```

---

## 9. المخاطر وخطط التخفيف

| الخطر | الاحتمال | التخفيف |
|---|---|---|
| Qwen3-ASR ستريمنج على Windows معقد (vLLM Linux فقط) | عالي | abstraction + `faster-whisper` كبديل فوري + [qwen3-asr-stream](https://github.com/HambaliMarcel/qwen3-asr-stream) عبر llama-server |
| جودة المصري ضعيفة | عالي | prompting → linter → fine-tune على ArzEn-MultiGenre |
| استهلاك VRAM (ASR + MT معاً) | متوسط | تحميل كسول + تفريغ الموديل الخامل + خيار "pre-pass فقط" |
| مزامنة الترجمة مع الفيديو عند السرعات/القفز | متوسط | نربط كل شيء بـ `playhead` من mpv مش بساعة النظام؛ التعامل الصريح مع seek/pause/speed |
| الرفرفة (flicker) | متوسط | قاعدة `displayed` الصارمة + LocalAgreement |
| حجم التحميل (موديلات ~6-10GB) | متوسط | مثبّت بيختار بروفايل الجهاز ويحمّل المطلوب فقط + تنزيل تدريجي مع شريط تقدم |
| ترخيص TTS تجاري | منخفض (مرحلة ٣) | نبدأ بـ Apache-2.0 فقط (Qwen3-TTS) أو نأجل الدبلجة |

---

## 10. مقاييس النجاح (KPIs نقيسها فعلياً)

1. **Time-to-first-subtitle** < ٢ ثانية (من لحظة Play)
2. **Latency محسوس** = ٠ في الوضع الافتراضي
3. **Flicker rate** = ٠ (أي سطر ظهر لا يتغير)
4. **COMET / BLEU** على عينة ٣٠ دقيقة (en→ar) — نقارن: NLLB فقط vs LLM بالسياق
5. **Egyptian acceptability**: تقييم بشري ١–٥ على ١٠٠ جملة (هدف ≥ ٤.٠)
6. **Pre-pass speed** ≥ ٥x realtime على كرت متوسط
7. **RAM/VRAM ceiling**: يعمل على ٦GB VRAM بدون كراش

---

**التالي:** `04-roadmap.md` (خطة التنفيذ على مراحل)
