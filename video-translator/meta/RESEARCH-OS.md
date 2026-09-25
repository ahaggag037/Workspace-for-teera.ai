# 🧠 Fawri Research OS v1.0 — نظام البحث الداخلي

> **وثيقة مُلزِمة.** هذه هي الطريقة التي أبحث بها دائماً.
> مبنية على: دراسات وكلاء البحث العميق + قياسات BrowseComp + أدبيات استرجاع المعلومات.
> **القاعدة الذهبية المستخرجة من الأدبيات:** في اختبار Oracle على BrowseComp-Plus،
> لما الأداة كانت مضمونة، GPT-4.1 وصل **93.5%** دقة — مقابل ~35% مع استرجاع عادي.
> ⇒ **عنق الزجاجة هو جودة الاسترجاع، لا قوة التفكير.**
> ⇒ أي جهد يُبذل في "التفكير الأفضل" بلا مصادر أفضل = تزيين للخطأ.

---

## المعمارية: ١٠ طبقات

```
  1. SKELETON      تفكيك النية → هيكل إجابة + قائمة مجاهيل مصنّفة
        ↓
  2. LATTICE       توليد "شبكة استعلامات" ٧ محاور لكل مجهول
        ↓
  3. FANOUT        إطلاق متوازٍ (كل الاستعلامات المستقلة في كتلة واحدة)
        ↓
  4. GRADE         تقييم كل دليل A/B/C/D + فلترة الروابط الميتة
        ↓
  5. TRIANGULATE   تثليث: كل دعامة تحتاج مصدرين مستقلين
        ↓
  6. ATTACK        الهجوم المضاد: ابحث بنشاط عن ما يهدم استنتاجك
        ↓
  7. FRESHNESS     فحص الزمن (اليوم: 2026-09-24) وصلاحية الروابط
        ↓
  8. CLOSE         قاعدة التوقف + إعلان صريح بما لا أعرفه
        ↓
  9. SYNTHESIZE    عقد إخراج: قرار + ثقة + ما يغيّر رأيي + الخطوة التالية
        ↓
 10. COMPOUND      تحديث "خريطة المصادر" — ذاكرة تتراكم ولا تُفقد
```

---

## ١) SKELETON — الهيكل قبل البحث

قبل أي استعلام، أكتب (داخلياً أو في الملف):

```
السؤال الحقيقي: ...
القرار الذي سيتخذه المستخدم بناءً على إجابتي: ...
شكل الإجابة المثالية: ...
المجاهيل (مرقمة ومصنّفة):
  U1 [FACT]     حقيقة قابلة للتحقق (رقم/تاريخ/مواصفة)
  U2 [STATE]    حالة التقنية/السوق الآن
  U3 [NUMBER]   قياس أداء / ميزانية / تكلفة
  U4 [PRACTICE] كيف يفعلها الناس فعلاً (gotchas)
  U5 [OPINION]  مسألة خلافية
  U6 [PRIOR]    هل سبقني أحد لهذه الفكرة؟ ← الأهم للابتكار
  U7 [VOID]     ما لا أعرف أنني لا أعرفه (يُكتشف أثناء البحث)
```

> ⚠️ **U6 إلزامي قبل الادعاء بأي ابتكار.** لا أقول "لم يسبقني أحد" إلا بعد بحث مخصص.

---

## ٢) LATTICE — شبكة الاستعلامات (٧ محاور)

لكل مجهول، أُولّد ٤–٨ استعلامات **ليست** إعادة صياغة، بل **زوايا هجوم مختلفة**:

| المحور | الوصف | مثال (على مشروع فوري) |
|---|---|---|
| **L1 · المصطلح** | الاسم التقني الدقيق | `streaming ASR Arabic Apache 2.0` |
| **L2 · المرادف** | التسمية البديلة في المجتمع | `realtime speech recognition local offline` |
| **L3 · الحل** | سمِّ ما تتوقعه — محرّكات البحث تحب الأسماء | `Voxtral Realtime 4B latency benchmark` |
| **L4 · المقارنة** | `X vs Y` — يكشف جداول ومراجعات | `Qwen3-ASR vs faster-whisper benchmark` |
| **L5 · الانعكاس** ⭐ | ابحث عن الفشل والقيود | `streaming ASR causes high WER overlapping speech` |
| **L6 · الزمن** | أضف السنة — يحارب المحتوى القديم | `real-time translation 2026 local GPU` |
| **L7 · المصدر/القيد** | نوع المصدر + قيد المستخدم | `site:github.com WASAPI loopback Python subtitles` |

### قواعد صياغة الاستعلامات (Query Craft)
- ✅ **عبارات اسمية** لا أسئلة كاملة: `streaming ASR latency` ≫ `how fast is streaming ASR?`
- ✅ أسماء نماذج/إصدارات/dates: `Qwen3-ASR-1.7B`, `2026`, `v2`
- ✅ `benchmark`, `comparison`, `evaluation`, `limitations`, `failure modes`, `arxiv`
- ✅ `github` للتنفيذ، `reddit`/`hackernews` للـ gotchas الواقعية، `huggingface` للموديلات
- ❌ ممنوع: استعلام واحد ثم استنتاج. ❌ ممنوع: الاستعلام الذي أتوقع إجابته فقط.
- ❌ ممنوع: الاستعلام عن رأيي (`is X good?`) — ابحث عن **قياس** (`X WER benchmark`).

---

## ٣) FANOUT — الإطلاق المتوازي

- **كل الاستعلامات المستقلة تُنفَّذ في كتلة أدوات واحدة.** (التسلسل يقتل السرعة والاتساع.)
- الحد الأدنى: **٣ استعلامات مختلفة لكل مجهول**.
- `depth`: `1` لمسح سريع، `2` للمقارنات، `3` للحقائق العميقة/الأرقام.
- الـ follow-ups تُبنى على ما ظهر: **الاستعلام التالي يُشتق من النتيجة السابقة** (multi-hop)،
  لا يُكتب مسبقاً.

---

## ٤) GRADE — تقييم الدليل

| الرمز | النوع | متى يُعتمد |
|---|---|---|
| **A** | مصدر أولي: ورقة بحثية، مستودع رسمي، توثيق، benchmark، model card، بيان صحفي للشركة المُنتِجة | أساس لأي رقم |
| **B** | ثانوي موثوق: تغطية تقنية رصينة، survey، منشور فيه أرقام منقولة بدقة | تعزيز |
| **C** | مجتمعي: Reddit/HN/مدونة شخصية/منتدى | **إشارة فقط** — يكشف gotchas، لا يُبنى عليه ادعاء وحده |
| **D** | تسويقي/ترويجي | **ادّعاء لا دليل** — يُسجَّل كـ "تقول الشركة" لا كحقيقة |

**مرشح الروابط:** الأدبيات تُظهر أن **٥–١٨%** من روابط الاستشهادات لا تُفتح،
و**٣–١٣%** مُختلقة كلياً، وأن **حتى ٥٧%** من الاستشهادات "مُبرَّرة لاحقاً"
(النموذج يُنتج من ذاكرته ثم يبحث عن مصدر يطابق شكله).
→ **أنا لا أستشهد برابط لم أفتحه فعلاً في هذه الجلسة. ولا أستشهد من الذاكرة أبداً.**

---

## ٥) TRIANGULATE — التثليث

- **ادّعاء حامل (load-bearing):** يحتاج مصدرين مستقلين، أحدهما A أو B.
- **رقم:** يحتاج مصدر أولي (ورقة/مستودع/قياس)، ويُذكر مع ظروف القياس دائماً
  (أي جهاز؟ أي دقة؟ أي عيّنة؟) — رقم بلا ظروف = رقم بلا معنى.
- **تناقض بين مصادر:** لا أختار الأفضل بل **أذكر التناقض والسبب المرجّح**
  (اختلاف الأجهزة/الإصدارات/العينات). التناقض معلومة، ليس مشكلة.

---

## ٦) ATTACK — الهجوم المضاد ⭐ (أهم طبقة)

بعد تكوين استنتاج، أهاجمه بنشاط:

```
استعلامات الهجوم الإلزامية:
  • "<الاستنتاج> limitations"
  • "<التقنية> failure modes / when it breaks"
  • "alternatives to <التقنية>"
  • "<التقنية> criticism / benchmark flawed"
  • "<الافتراض> is false / does not hold"
```
- لو **لم أجد** أي نقد: أُصرّح بذلك صراحةً وأُنزّل الثقة درجة (غياب النقد ≠ صحة؛
  غالباً يعني أنني بحثت في المكان الخطأ).
- أُسجّل "أقوى حجة ضد استنتاجي" في المخرجات. **هذه علامة الجودة الأولى.**

---

## ٧) FRESHNESS — فحص الزمن

- اليوم (ثابت): **2026-09-24**. التاريخ في أدوات البحث يتفوق على ذاكرتي.
- مجالات سريعة (نماذج/أدوات/تسعير): أي مصدر أقدم من **٦ أشهر** يُعلَّم ⚠️ ويُتحقق منه.
- مجالات بطيئة (نظرية/رياضيات/خوارزميات): سنتان مقبول.
- موديل/إصدار: أتحقق من تاريخ الإصدار ومن أنه ما زال الأحدث.

---

## ٨) CLOSE — قاعدة التوقف

أتوقف عندما يتحقق **أحد** الشرطين:
1. كل مجهول مصنّف U1..U6 حصل على مصدر A/B، **و** جولة ATTACK لم تُنتج مجاهيل جديدة؛ أو
2. نفدت ميزانية البحث — وحينها **أُعلن صراحةً** ما لم يُبحث.

> **قاعدة الصدق:** "لا أعرف، ولم أجد مصدراً" ≫ تخمين بصيغة واثقة.
> الجهل المُعلن قابل للمعالجة؛ التخمين المُقنَّع يبني قرارات على رمال.

---

## ٩) SYNTHESIZE — عقد الإخراج

كل مخرجات بحث تلتزم بهذا الشكل:

```
■ الاستنتاج (جملة واحدة)
■ الثقة: عالية / متوسطة / منخفضة — والسبب
■ الأدلة: [id](url) مع درجة A/B/C/D لكل دليل
■ أقوى حجة ضد هذا الاستنتاج:
■ ما سيغيّر رأيي: (دليل قابل للملاحظة)
■ ما لا أعرفه (فجوات صريحة):
■ الخطوة التالية / القرار المقترح:
```

لا أخلط **الاستدلال من مصدر** بـ **التقدير الشخصي**. الثاني يُوسم هكذا صراحة.

---

## ١٠) COMPOUND — التراكم (الخندق الحقيقي)

بعد كل جولة بحث، أُحدّث ملفيْن:

1. **`meta/SOURCE-MAP.md`** — خريطة المصادر حسب المجال:
   أي المواقع أعطت إجابة دقيقة؟ أي الاستعلامات كانت عالية العائد؟
   أي المصادر تكرّر كلاماً تسويقياً؟
2. **`meta/DECISIONS-LOG.md`** — كل قرار معماري + الدليل الذي بُني عليه + تاريخه،
   حتى يمكن مراجعته لاحقاً عند تغيّر المعطيات.

> الفرق بين وكيل بحث جيد وآخر عبقري: **الذاكرة التي تتراكم عبر الجلسات.**

---

## ⛔ الأنماط الممنوعة (Checklist قبل كل إجابة)

- [ ] هل بحثت فعلاً، أم أجبت من الذاكرة؟
- [ ] هل كل رابط استشهدت به **فُتح فعلاً** في هذه الجلسة؟
- [ ] هل كل استنتاج حامل عليه مصدران أم مصدر واحد؟ هل فيه مصدر A أو B؟
- [ ] هل نفّذت جولة **ATTACK** (بحثت عن الفشل والبدائل)؟
- [ ] هل بحثت عن **سبق/أولوية (prior art)** قبل ادعاء الابتكار؟
- [ ] هل وسمت الأرقام بظروف قياسها؟
- [ ] هل ميّزت بين "تقول الشركة" و"ثبت في قياس"؟
- [ ] هل أعلنت ما **لا** أعرفه؟
- [ ] هل حدّثت `SOURCE-MAP.md`؟

---

## 🗺️ خريطة مصادر ابتدائية (مجال الذكاء الاصطناعي/الصوت/الترجمة)

| الطبقة | المصادر عالية العائد | ملاحظات |
|---|---|---|
| أوراق | `arxiv.org`, `aclanthology.org`, `openreview.net` | الأعلى موثوقية للأرقام |
| موديلات | `huggingface.co` (model card + Discussions) | الـ Discussions تكشف عيوباً واقعية لا تذكرها البطاقة |
| تنفيذ | `github.com` | تحقّق من تاريخ آخر commit ونجومه قبل الاعتماد |
| قياسات | `paperswithcode`, HF leaderboards (Open ASR) | انتبه لظروف القياس |
| واقع ميداني | `reddit.com/r/LocalLLaMA`, HN | مصدر C: إشارة فقط |
| تغطية ثانوية | marktechpost, emergentmind, siliconflow | ⚠️ تسويقي جزئياً — تحقّق من الأرقام في المصدر الأولي |
| تحليل آلي | `pith.science` | مفيد لملخصات الأوراق والنقد المنهجي |

_آخر تحديث: 2026-09-24 — الإصدار 1.0_

---

# الملحق أ — خريطة المصادر (كانت ملفاً مستقلاً، دُمجت تطبيقاً للقاعدة S8)

## ١) تقييم المصادر (مجال: ASR / MT / TTS / عربي / زمن-حقيقي)

| المصدر | الدرجة | العائد | ملاحظات مستفادة |
|---|---|---|---|
| `arxiv.org` | **A** | ⭐⭐⭐⭐⭐ | أعلى عائد. الصيغة `html` أفضل من `abs` (تُظهر الجداول) |
| `aclanthology.org` | **A** | ⭐⭐⭐⭐⭐ | ممتاز للأوراق المقبولة (تفوق arXiv في الموثوقية) |
| `github.com` (مستودع رسمي) | **A** | ⭐⭐⭐⭐⭐ | الـ README + الـ commits يكشفان ما لا تقوله الورقة |
| `isca-archive.org` (Interspeech) | **A** | ⭐⭐⭐⭐ | مصدر ممتاز لأبحاث الكلام — غالباً أغفلته في الجولة الأولى |
| `huggingface.co/papers` | **A/B** | ⭐⭐⭐⭐ | ملخّصات نظيفة + روابط للكود والداتا في مكان واحد |
| `nature.com/articles` | **A** | ⭐⭐⭐⭐ | ممتاز **للأبحاث السلبية** (مخاطر الإفراط في التحيز) |
| `mdpi.com` | **B** | ⭐⭐⭐ | surveys جيدة؛ الأرقام تحتاج تحقّق من مصدرها الأولي |
| `pith.science` | **B** | ⭐⭐⭐⭐ | ⭐ مفاجأة الجولة: نقد منهجي آلي + "اعتراضات مُثارة علناً" = ATTACK pass مجاني |
| `lacuna.tiptreesystems.com` | **B/C** | ⭐⭐⭐⭐ | ⭐ مفاجأة ثانية: شروح ممتازة لـ **prior art** وسلاسل الأبحاث |
| `ieeexplore.ieee.org` | **A** | ⭐⭐⭐ | ممتاز للزمن-حقيقي/الجدولة؛ الوصول للنص الكامل متفاوت |
| `2019.rtss.org` | **A** | ⭐⭐⭐⭐ | ⭐ أعلى عائد في موضوع الجدولة — العروض التقديمية أوضح من الورقة |
| `studio-fugu.com` | **B** | ⭐⭐⭐⭐⭐ | ⭐ أفضل مصدر لمعايير الترجمة حسب اللغة (جدول CPS/CPL لـ RTL) |
| `subtle-subtitlers.org.uk` | **A** | ⭐⭐⭐⭐⭐ | ⭐ المعيار الذهبي لمعايير الترجمة (SUBTLE) |
| `reddit.com/r/LocalLLaMA` | **C** | ⭐⭐⭐ | إشارة فقط. ممتاز لاكتشاف النماذج **الجديدة قبل فهرستها** |
| `marktechpost` / `emergentmind` / `siliconflow` | **C/D** | ⭐⭐ | ⚠️ تسويقي جزئياً. **تحقّق دائماً من الرقم في المصدر الأولي** |
| `xda-developers.com` | **C** | ⭐⭐⭐ | ⭐ مفيد جداً لـ **الاستخبارات التنافسية** (من يبني ماذا) |
| `chromewebstore.google.com` | **C** | ⭐⭐⭐ | ⭐ مصدر مُهمَل لاكتشاف منافسين (إضافات المتصفح) |

---

## ٢) صيغ الاستعلامات التي **نجحت** (أعد استخدامها)

| المحور | الصيغة الناجحة | العائد |
|---|---|---|
| الانعكاس ⭐ | `<تقنية> limitations failure modes` | أعلى عائد — كشف ٣ مخاطر تصميمية |
| الأولوية ⭐ | `look-ahead future context simultaneous translation anticipation` | كشف TAF = prior art مباشر |
| المقارنة | `X vs Y benchmark` | جداول جاهزة |
| المعايير | `<لغة> subtitle reading speed characters per second guidelines` | ⭐ صحّح خطأً في التصميم |
| الاستخبارات | `video player subtitles translate on the fly <player>` | ⭐ كشف PotPlayer/mpv-llm-subtrans |
| الداتا | `<لغة> <مهمة> dataset huggingface <حجم>` | ⭐ كشف Alexandria |
| التنفيذ | `llama.cpp <تقنية> constrained decoding` | تقييم واقعي للجدوى |

## ٣) صيغ **فشلت** (لا تكرّرها)
- `how to make X better` → نتائج عامة بلا أرقام
- `is X good for Y` → آراء، لا قياسات
- `best AI tool 2026` (بدون قيد) → قوائم تسويقية مكرّرة
- البحث عن منتج تجاري بالاسم فقط → يعيد نسخة الموقع التسويقي

---

## ٤) حقائق مرجعية مثبتة (مُتحقَّق منها — أعد استخدامها بلا إعادة بحث)

| الحقيقة | المصدر | الدرجة |
|---|---|---|
| العربية RTL: ٣٢–٣٦ حرف/سطر، ١٥–١٨ CPS كحد أقصى | [studio-fugu](https://www.studio-fugu.com/blog-posts/your-ultimate-guide-to-multilingual-subtitling) | B |
| SUBTLE: متوسط ١٢–١٥ CPS، أقصى ١٦–١٧، مدة ١–٦ث، ٣٢–٤٢ حرف | [SUBTLE PDF](https://subtle-subtitlers.org.uk/wp-content/uploads/2023/01/SUBTLE-Recommended-Quality-Criteria-for-Subtitling.pdf) | A |
| NLLB-200 يدعم `arz_Arab` (مصري) و `arb_Arab` | [Phabricator T326578](https://phabricator.wikimedia.org/T326578) | A |
| Qwen3-ASR 0.6B/1.7B، ٥٢ لغة، ستريمنج+أوفلاين، Apache 2.0 | [QwenLM/Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR) | A |
| Voxtral Realtime 4B: ١٣ لغة، ٤٨٠ms = جودة Whisper، Apache 2.0 | [arXiv 2602.11298](https://arxiv.org/html/2602.11298v1) | A |
| Alexandria: ١٠٧K دورة، ١٣ دولة، جندر المتكلم-المخاطَب، `UBC-NLP/alexandria` | [arXiv 2601.13099](https://arxiv.org/abs/2601.13099) | A |
| ArzEn-MultiGenre: ٢٥,٥٥٧ زوج إنجليزي↔مصري (ترجمات + أغاني + روايات) | [arXiv 2508.01411](https://arxiv.org/pdf/2508.01411) | A |
| >٥٠٪ من جمل en→ar فيها اعتماد جندري؛ المخاطَب أكثر هيمنة | [Elaraby 2018](https://arxiv.org/abs/1802.09287) | A |
| TAF: توقع المستقبل بـ LLM + تصويت أغلبية، +٥ BLEU | [arXiv 2410.22499](https://arxiv.org/html/2410.22499v1) | A |
| QE-cascade: ترجمة صغير → CometKiwi → الأضعف للموديل الكبير | [arXiv 2502.12701](https://arxiv.org/pdf/2502.12701) | A |
| EDF أمثل لـ `1\|pmtn\|L_max` | [MDPI GPU Scheduling Survey](https://www.mdpi.com/1999-4893/18/7/385) | A |
| CometKiwi-23 سبيرمان: ٠.٨٦ (Et-En) ←→ ٠.٣٤ (En-Te) | [MDPI QE](https://www.mdpi.com/2078-2489/16/10/916) | A |
| الإفراط في التحيز يضر أكثر مما ينفع | [Nature SciRep 2025](https://www.nature.com/articles/s41598-025-12121-4) | A |
| IndexTTS2: تحكم دقيق بالمدة، خطأ <٠.٠٣٪، Apache 2.0، تغطية لغات "تتطور" | [IndexTTS2](https://index-tts.github.io/index-tts2.github.io/) | A |
| Oracle ablation على BrowseComp-Plus: ٩٣.٥٪ مع أدلة مضمونة | [arXiv 2508.06600](https://arxiv.org/html/2508.06600v1) | A |

---

## ٥) سجل القرارات المعمارية

| # | القرار | الدليل | الثقة | الحالة |
|---|---|---|---|---|
| D-01 | Qwen3-ASR أساسي + faster-whisper بديل | ٥٢ لغة + ستريمنج/أوفلاين + Apache 2.0 | 🟢 | مقبول |
| D-02 | llama.cpp (Vulkan) لتشغيل الـ LLM | يغطي AMD/NVIDIA/Intel بنفس binary | 🟢 | مقبول |
| D-03 | ترجمة هجينة NLLB (مسودة) + LLM (نهائي) | NLLB سريع على CPU ويدعم `arz`؛ LLM للسياق | 🟢 | مقبول |
| D-04 | قاعدة "السطر المعروض لا يتغير" | حل جذري للرفرفة | 🟢 | مقبول |
| D-05 | CPL ٣٢–٣٦ / CPS ١٣–١٥ للعربية | ⚠️ **صُحِّح بعد بحث** | 🟢 | مُحدَّث |
| D-06 | جدولة DQC بالمواعيد + `Δ*` المستنبطة | أدبيات الزمن الحقيقي + QE-cascade | 🟡 | مقترح |
| D-07 | قاموس عرّاف بمرشّح مضاد للإفراط | CMT-LLM + Nature (خطر الإفراط) | 🟢 | مقترح |
| D-08 | جندر المتكلم **والمخاطَب** حقناً في البرومبت | >٥٠٪ من السطور متأثرة | 🟡 | مقترح |
| D-09 | تأجيل الدبلجة (IndexTTS2 تغطية لغات غير مؤكدة) | مصدر أولي ينص على القيد | 🟢 | مقبول |
| D-10 | الاستباق: **قراءة** المستقبل لا توقعه | TAF تتوقعه لأنها لا تملكه | 🟢 | مقبول |

---

## ٦) فجوات بحثية لم تُغلق بعد (صراحة)

1. **لم أبحث في براءات الاختراع** — ادعاءات الابتكار مقيدة بالأدبيات المنشورة فقط.
2. لم أتحقق من **دعم العربية محلياً** في Qwen3-TTS (النسخة المستضافة تدعمها، المحلية غير مؤكدة).
3. لم أجد **قياساً منشوراً** لمنحنى الجودة مقابل الاستباق → هذه فرصتنا، لكنها تعني
   أيضاً أنه **لا يوجد خط أساس نقارن به**.
4. لم أتحقق من **ترخيص Voxtral TTS** (المصادر متضاربة: Apache-2.0 مقابل CC BY-NC).
5. لم أبحث في **استهلاك الطاقة/الحرارة** على اللابتوب (مهم للاستخدام الطويل).

---

_دُمجت 2026-09-24 بموجب القاعدة S8 (ميزانية الذاكرة): إضافة ملف إلى meta/ توجب دمجاً أو حذفاً._

---

# ١١) EMERGENCE REFRESH — البحث العابر للمجالات

عند طلب ابتكار يتجاوز orchestration المعتاد، لا أبحث في LLMs فقط. أفتح أربع نوافذ على الأقل: **complex adaptive systems**، الفيزياء/المواد، علوم الأعصاب/التحكم، وهندسة البرمجيات/التعلم. أبحث عن الآلية لا التشبيه:

```
primitive → bond/interface → local feedback → selection → memory →
resource/energy constraint → defect/residual → phase transition → held-out persistence
```

أي اقتراح جديد يجب أن يجيب: ما الذرة؟ ما الرابطة؟ ما الذي يتغير بسبب feedback؟ ما آلية الانتقاء؟ كيف يتحول الفشل إلى بنية؟ وما الدليل على انتقال القدرة إلى تركيب لم يره النظام؟

قاعدة المواد: العيب ليس فشلاً تلقائياً؛ قد يكون مصدراً للتكيف، لكنه لا يصبح قوة إلا داخل lattice وقواعد تثبّت حركته. أترجم ذلك إلى `residual → operator → capability graph`، لا إلى سجل أخطاء طويل.

قاعدة التعقيد: لا تعطي كثرة الوكلاء emergent intelligence وحدها؛ يلزم تفاعل غير خطي، ذاكرة، تغذية راجعة، وعتبة يمكن قياسها. وقاعدة الابتكار: أفحص prior art في blackboard systems، compositional generalization، test-time adaptation، self-evolving agents، وprogram repair قبل تسمية التركيب اختراعاً.

المخرج الإلزامي للجولة العابرة للمجالات: **mechanism map + prior-art matrix + formal hypothesis + falsification experiment**. التشبيه يُوسم تشبيهاً، والآلية تُصاغ كعقد/معادلة/اختبار.

# ١٢) META-AMPLIFICATION REFRESH — من تحسين score إلى ترقية abstraction

الجولة الجديدة تضيف قاعدة: `operator ≠ capability`. لا تُرقّى نتيجة إلى capability إلا إذا امتلكت interface، pre/postconditions، verifier، routing context، replay provenance، وrollback، ثم اجتازت held-out composition دون زيادة غير مسموحة في budget.

أفصل دائماً بين:

```text
M = base model (ثابت أثناء التجربة)
H = harness (قابل للتعديل والإصدار)
K = typed capability knowledge (operators/contracts/graphs)
```

وأبحث عن `abstraction promotion` عبر المستويات:

```text
L0 instance patch → L1 local operator → L2 closed capability
→ L3 compositional schema → L4 meta-controller
```

الهدف ليس أن أرفع evaluator score فقط، بل أن أختبر تغير مساحة الحلول: unseen transfer، composition، retention، diagnosis، recovery، cost، وscope. أستخدم مصادر RSI/meta-agent الحديثة لتحديد ما يثبت harness improvement وما لا يثبت model self-improvement، وأعامل reward hacking وignition claims كاختبارات مستقلة.

يجب تسجيل هذه الجولة في:

- `RESEARCH/TAEC-V2-DEEP-DESIGN-REFRESH.md`
- `meta/SOURCE-MAP.md`
- `meta/DECISIONS-LOG.md`

ولا يُشغّل full protocol قبل E1–E3: dual-control probe، fast/broad memory، وtyped residual compiler.

# ١٣) META-COGNITION / ATTRIBUTION UPDATE — من معرفة الحدود إلى التصرف وفقها

الجولة الجديدة تضيف أن self-report لا يكفي. يجب فصل:

```text
self-knowledge
عن
metacognitive control
```

ولا يسمح النظام للنموذج وحده بتقرير الثقة أو التصعيد. تُقاس إشارات خارجية: verifier disagreement، local-global state gap، memory staleness، task-family distance، irreversibility، residual recurrence، وstress/debt.

كما يجب فصل:

```text
Outcome Gain
عن
Mechanism Evidence
```

أي أن التحسن في المهمة لا يثبت أن memory أو operator أو probe هو سبب التحسن. نستخدم persistence-on/off، stale/distractor controls، وtrace evidence لـwrite→retrieve→apply→update.

وتُضاف إلى tomography مؤشرات trajectory-level:

```text
local action validity
world-state fidelity
local-global gap
stress accumulation
recovery after collapse
```

الهدف الجديد: **governed composition** — primitives + typed interfaces + composition + boundary detection + intervention + recovery + trajectory evidence.

المصدر/المخرج التفصيلي: `RESEARCH/TAEC-V2-META-COGNITION-UPDATE.md`.

# ١٤) NEUROCOGNITIVE REFRESH — ترجمة آليات الدماغ لا ادعاء امتلاك دماغ

لا يكفي بحث AI وحده عند تصميم cognition عميقة. أفتح مساراً مستقلاً لعلم الأعصاب: neural manifolds، recurrent/global workspace، PFC–basal-ganglia gating، hippocampal replay، oscillatory multiplexing، neuromodulatory uncertainty، network switching، dendritic/context integration، وpost-decision metacognition.

القاعدة:

```text
brain observation → computational principle → software mechanism → ablation
```

لا أخلط ذلك بادعاء أن النموذج يملك جمجمة أو سيالات عصبية أو شخصية ذاتية. الكلمات "خطي/حلزوني/تجاوزي" تُترجم إلى modes قابلة للقياس: linear، branching، recurrent، abstraction-promoting، representation-switching؛ وليست أسماء علمية مثبتة لديناميكيات بشرية منفصلة.

المخرج التفصيلي: `RESEARCH/TAEC-V2-NEUROCOGNITIVE-REFRESH.md`.

آليات NCL المرشحة:

```text
StateManifold
RecurrentWorkspace
WorkingMemoryGate
ReplayScheduler
NeuromodulatorySignals
NetworkModeController
ContextContentGate
PostDecisionMonitor
GlobalStateAuditor
```

كل آلية تُختبر مستقلة في N1–N8 قبل دمجها، ولا تُسجل نتيجة neurocognitive أو consciousness claim من التشابه المعماري.

# ١٥) FUTURE/EVENT REFRESH — الحدث قبل token والتوزيع قبل النبوءة

الحدث أصبح وحدة أساسية في TAEC v2. لا يكفي توقع next token أو next action؛ يجب بناء:

```text
event boundary → event graph → successor map → hazard/time window
→ multi-horizon futures → causal/counterfactual branches
→ action → forecast residual → schema update
```

كل forecast يخرج event type، time window، probability، conditions، leading indicators، disconfirming signals، causal path، وaction options. التوقعات تقاس بـcalibration وproper scoring وtime-to-event، لا بالـaccuracy فقط.

نفرق صراحة بين:

```text
likely future
possible future
counterfactual future
extreme/tail future
```

وتستخدم early-warning signals مثل recovery latency، autocorrelation، variance، وlocal-global gap كfeatures احتمالية، لا كحتمية لانهيار.

المخرج التفصيلي: `RESEARCH/TAEC-V2-FUTURE-EVENT-COMPILER.md`.

التجارب الجديدة F1–F9 تختبر event trace، successor representation، hazard، multi-horizon prediction، counterfactual futures، early warning، prospective memory، وforecast calibration قبل أي claim عن foresight.

