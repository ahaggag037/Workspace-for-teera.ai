# TAEC v2 — الجولة الثانية: الذاكرة المناعية، التشكل، والتعلم متعدد الأزمنة

**التاريخ:** 2026-09-24
**الحالة:** بحث إضافي؛ لا تنفيذ بعد.

## الاستنتاج المركزي

الجولة الأولى أعطت `Residual → Operator → Capability Graph`. الجولة الثانية أضافت أن هذا وحده لا يكفي. النظام الذي يريد اكتساب قدرات يحتاج ثلاث خصائص كانت ناقصة:

1. **تعدد أزمنة التعلم:** حل سريع، تعديل خلال الحلقة، consolidation بطيء.
2. **انتقاء يشبه المناعة:** ليس كل نجاح يتحول إلى ذاكرة؛ نحتاج تنوعاً، تخصيصاً، breadth، tolerance، وnegative selection.
3. **تنظيم يشبه التشكل:** local activation مع long-range inhibition، حتى لا يسيطر operator واحد ولا تتحول الذاكرة إلى كتلة متجانسة.

هذه ليست دعوة لنسخ البيولوجيا حرفياً؛ إنها آليات قابلة للترجمة والاختبار.

---

## 1) الذاكرة المناعية: بنك سريع وبنك واسع

في المناعة التكيفية، affinity maturation تنشئ نسخاً متغيرة وتنتقيها، لكن plasma cells وmemory cells لا يملكان الهدف نفسه. الدراسات تصف مفاضلة بين استجابة عالية التخصيص للمستضد الحالي وذاكرة أوسع قادرة على التعامل مع مستضدات متغيرة، مع feedback من الأجسام المضادة يعيد تشكيل بيئة الانتقاء نفسها. [1](https://www.sciencedirect.com/science/article/pii/S0022519321003246) [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC12716205/)

الترجمة إلى TAEC:

### Fast Response Bank

يحتوي على operators عالية التخصيص لمهمة حالية:

```text
problem signature → fast operator → immediate repair
```

عمرها قصير، وكلفتها منخفضة، ولا تدخل الذاكرة طويلة الأجل بمجرد نجاح واحد.

### Broad Memory Bank

يحتوي على operators أقل تخصيصاً وأكثر قابلية للانتقال:

```text
failure class → general operator → task-family transfer
```

قد يكون operator أقل أداءً على task واحد لكنه أفضل عبر تغييرات unseen. لذلك لا نختار دائماً أعلى score محلي؛ نحتفظ أحياناً بالمرشح الأوسع.

### Negative Selection / Tolerance

كما تحتاج المناعة إلى التمييز بين foreign وself، يحتاج TAEC إلى رفض operator ينجح taskياً لكنه يسبب:

- scope drift.
- regression.
- unsupported claims.
- overfitting للـevaluator.
- ضرراً في task family مجاورة.

إذن operator له حالتان مستقلتان:

```text
local_affinity
transfer_breadth
```

ولا يُقبل في long-term bank إلا إذا كانت `transfer_breadth` موجبة أو كان هناك سبب صريح للاحتفاظ به كـfast specialist.

---

## 2) morphogenesis: التفعيل المحلي والتثبيط البعيد

نظرية Turing reaction-diffusion تشرح كيف يمكن لتفاعلات محلية أن تنتج pattern غير متجانس من حالة أولية متجانسة؛ activator قصير المدى يعزز النمو محلياً، وinhibitor أطول مدى يمنع الانتشار غير المحدود. [1](https://www.dna.caltech.edu/courses/cs191/paperscs191/turing.pdf) [2](https://journals.biologists.com/dev/article/142/7/1203/47299/Positional-information-and-reaction-diffusion-two)

في TAEC لا نستخدم chemical diffusion حرفياً، لكن نترجم الآلية:

```text
operator utility on nearby tasks = activator
operator conflict/cost/interference = inhibitor
transfer across related tasks = diffusion
```

إذا نجح `ScopeLedger` في عدة مهام متجاورة، تزيد قابلية تفعيله في family مشابهة. لكن إذا سبب cost أو over-constraint في families أخرى، تنتشر إشارة inhibition وتمنع routing من اختياره عالمياً.

هذا يعالج مشكلة لم يعالجها TAEC v0: **routing collapse**، أي أن النظام يستخدم verifier أو skill واحداً لكل شيء لأنه نجح مبكراً.

في MoE، routing السيئ يترك بعض experts under-used ويدفع أخرى إلى over-specialization؛ Expert Choice يعكس اتجاه الاختيار لفرض capacity أكثر توازناً. [1](https://papers.neurips.cc/paper_files/paper/2022/file/2f00ecd787b432c1d36f3de9800728eb-Paper-Conference.pdf) [5](https://research.google/blog/mixture-of-experts-with-expert-choice-routing/)

الترجمة العملية: لا نكتفي بأن task يختار operator؛ نسجل أيضاً **capacity وload وtransfer** لكل operator، ونمنع operator من احتكار كل السياقات.

---

## 3) الذاكرة ليست ملفاً: ثلاثة أزمنة

أبحاث memory consolidation تصف replay متكرراً يحول traces الحلقية إلى تمثيلات أكثر تجريداً واستقراراً، مع إعادة توزيع بين ذاكرة سريعة وذاكرة طويلة الأجل. [1](https://www.nature.com/articles/s41593-019-0467-3) [2](https://www.nature.com/articles/s41467-023-43939-z)

هذا يقترح ثلاث حلقات:

### T0 — Working Loop

```text
task → action → observation → next action
```

حالة غنية ومؤقتة. لا نخزنها كلها لاحقاً.

### T1 — Episode Loop

```text
trace → residual → candidate operator
```

يعمل بعد task أو بعد failure cluster. ينتج مرشحين، لا يغير النظام الحي تلقائياً.

### T2 — Consolidation Loop

```text
replay selected episodes
→ compress to minimal sufficient operator
→ adversarial test
→ accept / retain / forget
```

الاختيار لا يعتمد على recency فقط؛ الأولوية لـ:

```text
novelty
+ severity
+ transfer potential
+ repeated failure
+ information gain
− redundancy
− interference
```

مبدأ information bottleneck يقول إن التمثيل الجيد minimal لكنه sufficient للمهمة، وأن ضغط المعلومات قد يزيد robustness ضد nuisance variables. [1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10369960/)

لكن الضغط المحلي قد يحذف شيئاً تحتاجه مهمة أخرى؛ لذلك نحتاج **task-family-conditioned memory**، لا ملخصاً واحداً عالمياً.

---

## 4) dual control: الفعل الذي يحل ويعلّم في نفس الوقت

في dual control، الفعل له أثران: يحسن الهدف الحالي، ويجمع معلومات عن النظام المجهول. controller جيد لا يفصل exploration عن exploitation تماماً؛ يختار أحياناً probing action لأن قيمة المعلومة المستقبلية تبرر كلفته. [1](https://arxiv.org/html/2608.20073) [9](https://jmlr2020.csail.mit.edu/papers/volume17/15-162/15-162.pdf)

في TAEC:

```text
ask clarification
read one extra file
run a cheap targeted test
create a minimal counterexample
```

قد تكون هذه actions منخفضة الأداء اللحظي لكنها عالية information gain. يجب أن يقررها meta-controller عندما:

```text
uncertainty × future consequence > probe_cost
```

هذا أعمق من قاعدة assume/ask الحالية التي تعتمد على risk labels ثابتة.

---

## 5) developmental curriculum: النظام يختار ما يتعلمه

أبحاث Intrinsically Motivated Goal Exploration Processes تبين أن agent يستطيع توليد أهدافاً، يختارها حسب learning progress، ويبني curriculum من مهارات بسيطة إلى tool use وتركيبات أصعب؛ لا يحتاج أن يبرمج المصمم كل ترتيب مسبقاً. [1](https://www.jmlr.org/papers/volume23/21-0808/21-0808.pdf) [4](https://arxiv.org/pdf/2202.10222)

لا نطبق open-ended learning بلا حدود على Codex؛ هذا مكلف وغير آمن. لكن نستخدم نسخة مضبوطة:

```text
capability frontier
→ generate near-boundary task
→ estimate learning progress
→ choose task with high transfer value
→ test on locked holdout
```

أي أن benchmark لا يكون ثابتاً فقط. بعد اكتشاف residual متكرر، يولد النظام task قريباً من الحد الذي يفشل فيه Terra، وليس random task. هذا يصنع curriculum موجهة لنقاط الضعف الحقيقية.

الشرط: tasks المولدة للتعلم لا تكون هي نفسها held-out evaluator؛ held-out يبقى خارج حلقة التوليد.

---

## 6) typed DSL: operator ليس نصاً

أبحاث program synthesis وS3 تستخدم DSL مقيدة، أمثلة input-output، search، ranking، وtype checking لبناء إصلاحات تعمم أفضل من patch حر غير مقيد. [1](https://www.cs.cmu.edu/~clegoues/docs/legoues-esecfse17.pdf) [9](https://dl.acm.org/doi/10.1145/3106237.3106309)

هذا يغيّر RCC جوهرياً. operator لا يُخزن هكذا:

```text
تذكر أن تتحقق من scope.
```

بل كـtyped transform:

```text
Operator<ScopeLedger>:
  requires: Task has write_scope
  reads: TaskContract, Diff
  writes: ScopeState
  ensures: changed_paths ⊆ allowed_paths
  verifier: PathOracle
  cost: CostModel
  invalidates: on_scope_schema_change
```

الـLLM يمكن أن يقترح operator، لكن compiler/validator يمنع malformed operators، وtest synthesis يخلق أمثلة مضادة قبل التثبيت.

---

## 7) التصميم الجديد: Cognitive Organism Kernel

الاسم المؤقت للطبقة النظرية: **COK — Cognitive Organism Kernel**. ليس منتجاً جديداً ولا ادعاءً نهائياً؛ هو دمج للآليات التالية داخل RCC:

```text
Working Loop       = T0 execution
Germinal Loop      = T1 candidate variation/selection
Consolidation Loop = T2 replay/compression
Immune Gate        = tolerance + negative selection
Morphogen Router   = local activation + global inhibition
Dual Controller    = task action + information gain
Capability Lattice  = typed operators and compositions
```

الصورة الكاملة:

```text
Task field
  ↓
probe / act / observe
  ↓
working state
  ↓
residual extraction
  ↓
variation of typed operators
  ↓
local evaluator + adversarial inhibition
  ↓
capability lattice update
  ↓
replay/consolidation
  ↓
held-out transfer / retention
  ↓
crystallize, keep broad memory, or kill
```

لا يوجد هنا ادعاء بوعي أو selfhood. كلمة organism استعارة هندسية لنظام له metabolism للمعلومات، homeostasis للمخاطر، memory متعددة الأزمنة، وتخصص قابل للتكيف.

---

## 8) ما الذي لم نثبتْه؟

- ليس ثابتاً أن immune-style selection أفضل من Pareto prompt evolution.
- ليس ثابتاً أن reaction-diffusion analogy تنتج router أفضل.
- ليس ثابتاً أن replay/consolidation يقلل forgetting في coding agents.
- ليس ثابتاً أن curriculum ذاتي التوليد لا يoverfit للـevaluator.
- ليس ثابتاً أن operators typed ستنتقل بين task families.
- لا يوجد بعد benchmark لـCOK.

لذلك كل آلية تدخل كـhypothesis منفصل، مع ablation مستقل.

## 9) التجربة الصغيرة المناسبة

لا نبني الكائن كله دفعة واحدة. نختبر ثلاثة mechanisms فقط على TAEC v0:

### E1 — Dual Probe

يقارن:

```text
act immediately
vs
cheap information-gain probe ثم act
```

### E2 — Two-Bank Memory

يقارن:

```text
recent trace memory
vs
fast specialist bank + broad transferable bank
```

### E3 — Residual Operator

يقارن:

```text
failure note فقط
vs
failure → typed operator → compositional held-out
```

وكل تجربة تقيس:

```text
heldout transfer
retention after distractors
negative transfer
accepted outcome/token/minute
```

إذا لم يظهر أثر mechanism منفرداً، لا نضيفه إلى COK لمجرد جمال التشبيه.

## القرار الحالي

الجولة الثانية نقلت الفكرة من «تراص وحدات» إلى **تنظيم متعدد الأزمنة والوظائف**:

```text
variation without selection = noise
selection without diversity = brittleness
memory without forgetting = overload
activation without inhibition = routing collapse
exploration without task utility = waste
compression without sufficiency = catastrophic forgetting
```

الخطوة التالية الفكرية هي formal spec لـCOK/RCC وتجربة واحدة صغيرة على residual-to-operator، لا تشغيل stack كبير ولا إضافة agents عشوائياً.
