# Terra → Astra: جلسة البحث الأولى ونظرية النقل السلوكي

**التاريخ:** 2026-09-24
**الحالة:** بحث أولي مكتمل؛ لم يُكتب prompt التنفيذ بعد.

## الحكم المختصر

لا توجد طريقة prompt-only تحول GPT-5.6 Terra إلى GPT-6 Astra حرفياً. الفرق يشمل checkpoint وتدريباً مسبقاً وRL وalignment وقدرات computer-use وحكماً أفضل، وأجزاء داخلية غير منشورة. لكن يمكن بناء **نظام تنفيذ Astra-like** حول Terra: ذاكرة خارجية، استرجاع انتقائي، test-time compute متكيف، أدوات، orchestration، تحقق مستقل، وتصحيح موجّه بالأدلة.

الهدف الصحيح ليس: «Terra = Astra».
الهدف القابل للقياس هو: **Terra + harness ذكي يقترب من Astra في مهام المستخدم، مع تكلفة وفشل معروفين.**

---

## 1) ماذا نعرف عن النموذجين؟

### Terra — معلوم من الوثائق الرسمية

`GPT-5.6 Terra` نموذج يوازن الذكاء والتكلفة، ويدعم `reasoning.effort` من `none` إلى `max`، وسياقاً حتى 1,050,000 token، وخرجاً حتى 128,000 token، وأدوات مثل code interpreter وweb search وcomputer use وMCP. صفحة النموذج تقول صراحةً إنه يقابل تقريباً طبقة mini في العائلات السابقة، وأن fine-tuning غير مدعوم. المصدر: [OpenAI Terra model page](https://developers.openai.com/api/docs/models/gpt-5.6-terra).

### Astra — معلوم من الوثائق الرسمية

`GPT-6 Astra` مخصص لأصعب الأعمال end-to-end، ويدعم reasoning من `low` إلى `max`، والسياق والخرج نفسيهما تقريباً، وأدوات البحث والملفات والكود والكمبيوتر. لكن القيمة الإضافية ليست حجم السياق فقط: OpenAI تصفه بأنه دُرّب عبر pre-training وRL وalignment ليحسن الحكم، فهم النية، computer use، البرمجة، العلم، والمهام المهنية. المصدر: [Astra API model page](https://developers.openai.com/api/docs/models/gpt-6-astra) و[إعلان Astra الرسمي](https://openai.com/index/gpt-6-astra/).

الوثيقة الرسمية تصف سلوكاً مهماً: Astra يملأ الفراغات الروتينية من السياق، يسأل فقط عندما يغير الجواب النتيجة، يستمر في العمل المستقل، يحافظ على اتجاه المهمة عند وصول متطلبات جديدة، ويستخرج السياق المهم بدلاً من تكرار كل شيء. هذا سلوك policy/harness قابل للتقليد جزئياً، لكنه ليس دليلاً أن Terra يملك نفس القدرة الخام.

### الفجوة الخارجية

المقارنات العامة ليست اختباراً محايداً لمهامنا. Artificial Analysis يعرض في مقارنة Terra High مقابل Astra Medium فجوة كبيرة في مؤشر الذكاء وTerminal-Bench، بينما Arena يقيس سلوكاً agentic مختلفاً ويعرض Astra Max أعلى من Terra xHigh في إشارات النجاح/الرضا. هذه أرقام مرجعية لا يجوز تحويلها إلى تنبؤ دقيق لمشروعنا: [Artificial Analysis](https://artificialanalysis.ai/models/comparisons/gpt-6-astra-medium-vs-gpt-5-6-terra-high) و[Arena Agent leaderboard](https://arena.ai/leaderboard/agent?rankBy=labs).

### ما لا نعرفه

لا نملك weights أو training recipe أو system prompt الكامل أو architecture موثقاً لـ Astra. توجد تقارير عن recurrent depth، لكن المصدر نفسه يصنفها كخبر غير مؤكد، وOpenAI لم تثبت أن Astra يستخدمه؛ بل تقول وثائق النظام إن سبب تغير monitorability غير منسوب تفاضلياً إلى architecture. لذلك لا نبني الحل على شائعة. المصدر: [تحليل recurrent depth مع فصل المؤكد عن المبلغ عنه](https://kingy.ai/blog/recurrent-depth-openai-astra/) و[نموذج Huginn البحثي عن latent recurrent depth](https://arxiv.org/html/2502.05171v1).

---

## 2) الاكتشاف الحاسم: النموذج ليس النظام

أقوى دليل عملي جاء من OpenAI نفسها: عند تشغيل GPT-5.6 Sol على ARC-AGI-3، رفع harness يحتفظ reasoning ويستخدم compaction النتيجة من 13.3% إلى 38.3%، مع خفض tokens بنحو 6 مرات. التغيير لم يكن في weights؛ كان في إدارة الحالة. المصدر: [ARC-AGI-3 harness investigation](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/).

وفي دليل بناء الأنظمة، تحدد OpenAI ثلاث رافعات: الاحتفاظ بالعمل السابق والـ reasoning، orchestration متعدد الوكلاء عند ملاءمته، ونقل العمل الحتمي إلى code بدلاً من استهلاك model tokens. المصدر: [Builder's guide to GPT-5.6](https://openai.com/index/builders-guide-to-gpt-5-6/).

إذن نشتري جزءاً من «إحساس Astra» خارج النموذج:

- الذاكرة والاتجاه عبر ملفات state.
- التخطيط والتحقق بدلاً من إجابة واحدة.
- أدوات حقيقية بدلاً من تخمين.
- توقف مبني على evidence بدلاً من ثقة لغوية.
- context retrieval انتقائي بدلاً من لصق كل التاريخ.

ولا نشتري:

- المعرفة الكامنة والتعميم الموجودين في weights.
- التحسن الأصلي في RL وalignment.
- latent reasoning أو architecture غير المنشورة.
- قدرة Astra في مسألة جديدة تماماً لم يستطع Terra تمثيلها.

---

## 3) ما الذي تعلمناه من البحث الخارجي؟

1. **الاستدلال وقت التشغيل قابل للتوسيع، لكن ليس بلا حدود.** Tree of Thoughts يضيف بحثاً وتفرعاً وbacktracking، وSETS يجمع sampling وself-verification وself-correction. النتيجة تعتمد على وجود verifier؛ تكرار الكلام وحده قد يضاعف التكلفة بلا فائدة. المصادر: [Tree of Thoughts](https://arxiv.org/pdf/2305.10601) و[SETS](https://arxiv.org/html/2501.19306v1).

2. **الأدوار المتعددة تنجح إذا كان orchestrator جيداً.** دراسة multi-agent على مهام tool-intensive وجدت أن reasoning عند المنسق يعطي أكبر مكسب، بينما reasoning في كل sub-agent قد يكون محدوداً أو سلبياً. ودراسة ثلاثة أدوار على نموذج واحد أظهرت أن scaffolding وقت التشغيل قد يضاعف الأداء في بيئة محددة، لا في كل شيء. المصادر: [Can Small Agents Collaborate?](https://arxiv.org/html/2601.11327v2) و[Three Roles, One Model](https://arxiv.org/html/2604.11465v1).

3. **تطور prompt ممكن بدون تغيير weights، لكن يحتاج held-out evaluation.** GEPA يقرأ traces وأخطاء الأدوات، يشخص السبب، يطوّر prompts، ويحافظ على Pareto frontier بدلاً من اختيار أفضل تجربة واحدة. هذا أقرب نموذج علمي لفكرة «التعلم الخارجي». المصدر: [GEPA, ICLR 2026 Oral](https://iclr.cc/virtual/2026/oral/10009494).

4. **لا تجعل Terra حكماً وحيداً على نفسه.** أبحاث LLM-as-a-Judge ترصد self-preference وverbosity وposition biases؛ لذلك يلزم verifier حتمي، أو حكم بشري، أو حكم من عائلة مختلفة، أو على الأقل blind pairwise evaluation. المصدر: [Quantifying bias in LLM-as-a-Judge](https://arxiv.org/html/2410.02736v1).

5. **التدريب/التقطير هو الطريق الوحيد للنقل الأعمق، لكنه غير متاح هنا.** توجد أبحاث على agent distillation تنقل behavior والأدوات من teacher إلى student، لكنها تحتاج dataset وteacher وcompute وتقييماً، وليست promptاً سحرياً داخل Codex. المصدر: [Distilling LLM Agent into Small Models](https://arxiv.org/html/2505.17612).

6. **كلما زادت المكونات ليس بالضرورة أن يتحسن النظام.** بحث scaffolding نفسه يبين أن tool access قد يفيد أكثر من «تفكير» إضافي، وأن التفكير غير المنضبط قد يسبب tool drift وnon-termination. لذلك الحل يجب أن يكون adaptive لا stack ثابتاً من خمسين قاعدة.

---

## 4) الاختراع المقترح: TAEC / AER-EGM

الاسم العملي المقترح: **TAEC — Terra→Astra Execution Compiler**، ومحركه التكيفي **AER-EGM — Adaptive External Recurrence with Evidence-Gated Memory**. TAEC هو الغلاف التنفيذي، وAER-EGM هو حلقة الحالة/التصعيد داخله.

ليست الفكرة promptاً واحداً؛ بل compiler يحول كل طلب إلى **Run Packet صغير ومناسب للمهمة**، ثم يدير Terra خلال حلقة evidence-gated.

### طبقات TAEC

1. **Intent Compiler**
   يستخرج: الهدف، artifact المطلوب، Definition of Done، القيود، المخاطر، unknowns، والقرارات القابلة للرجوع. يمنع Terra من التعامل مع الطلب كموضوع مفتوح.

2. **Adaptive Compute Router**
   يبدأ بأقل دورة تكفي. يصعّد فقط عند uncertainty أو فشل اختبار أو تضارب evidence:
   - D0: Terra مرة واحدة + تحقق حتمي.
   - D1: planner مختصر ثم executor ثم verifier.
   - D2: بديلان/نقد adversarial ثم تنفيذ ثم اختبار.
   لا نستخدم `max` أو عدة وكلاء لمجرد الإبهار.

3. **External Recurrence**
   كل دورة تقرأ state صغيراً وتكتب artifact جديداً: `STATE.json`, `DECISIONS.md`, `EVIDENCE.jsonl`, `FAILURES.md`. هذا يحاكي الاستمرارية/التكرار خارج latent space، بدون الادعاء أنه recurrent Astra.

4. **Orchestrator + bounded workers**
   Terra واحد يحتفظ بالحكم النهائي. workers محددون: `Scout` للقراءة، `Builder` للتنفيذ، `Verifier` للاختبار، `Adversary` لكسر النتيجة. لا نعطي كل worker حرية تغيير الملفات، ولا نجعل كل واحد «يفكر بعمق» بلا سبب.

5. **Evidence Gate**
   لا تنتقل الحالة من `planned` إلى `done` إلا بملف/اختبار/خرج قابل لإعادة التشغيل. اكتشاف مشكلة خارج النطاق لا يمنح الإذن بإصلاحها.

6. **Context Compiler**
   الـ OS الكامل يبقى على القرص، لكن الرسالة المرسلة لـ Terra تكون قصيرة وتحتوي فقط على القيود المرتبطة بالمهمة. هذا مهم لأن إرشادات Astra الرسمية نفسها تحذر من skills وAGENTS ضخمة أو متعارضة، وتوصي بـ progressive disclosure وتعريف completion بوضوح. المصدر: [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).

7. **Independent acceptance**
   verifier حتمي أولاً؛ بعده نقد model منفصل أو human review عند الحاجة. لا نقبل حكم Terra على مخرجه باعتباره ground truth.

8. **Prompt evolution**
   لا نعدل النظام الحي بعد كل فشل. نحفظ trace، نصنع candidate prompt، نختبره على build set ثم held-out set، ونقبله فقط إذا تحسن مع عدم تدهور المهام الأخرى. القواعد لها expiry وkill condition.

---

## 5) كيف نثبت أنه نجح؟

لا نقارن شعورنا بـ «Astra». نبني A/B على 12–24 مهمة ممثلة:

- coding/debugging، بحث موثق، تخطيط متعدد القيود، ملفات/وثائق، ambiguity، واستعادة من فشل.
- A: Terra High الحالي.
- B: Terra High + TAEC.
- نفس الملفات والأدوات وreasoning effort، وترتيب عشوائي، وacceptance مخفي قدر الإمكان.

المقاييس: `accepted_first_pass`, `tests_passed`, `scope_violations`, `unsupported_claim_rate`, `tool_hallucinations`, `correction_turns`, `recovery_steps`, الوقت/الاستهلاك، وتقييم المستخدم. لا نقبل «تحسن» بلا held-out evidence.

**النتيجة المتوقعة:** يمكن أن نغلق جزءاً كبيراً من فجوة workflow والانضباط والذاكرة والتحقق، خصوصاً في مهام Codex ذات الملفات والاختبارات. لا نتوقع أن نحول Terra إلى Astra في المعرفة الخام أو المسائل الحدية أو القدرات الكامنة.

## القرار

التحدي ممكن كـ **نقل سلوكي/نظامي مقيس**، ومستحيل كـ **استنساخ weights** عبر prompt. الخطوة التالية بعد هذه الجلسة هي كتابة prompt صغير يطلب من Codex بناء TAEC/AER-EGM نفسه، لا كتابة برومت ضخم يلقنه كل شيء. أول اختبار حقيقي لـ TAEC هو A/B على مهام Terra نفسها؛ إذا لم يتحسن فلا ندافع عنه، بل نقتله أو نعدله.
