# TAEC v2 — Cross-Domain Research Refresh

**التاريخ:** 2026-09-24
**الحالة:** بحث وتصميم أولي؛ لم يُرسل بعد إلى Codex.

## 1) تصحيح الاتجاه

ما بنيناه في TAEC v0 هو **measurement and safety kernel**: عقد، ذاكرة، evaluator، run-state، وحماية من النتائج الكاذبة. هذا ضروري، لكنه لا يخلق قدرة جديدة في Terra.

الطموح الأعلى يحتاج سؤالاً مختلفاً:

> كيف يتحول فشل Terra المتكرر إلى بنية تنفيذية جديدة قابلة لإعادة التركيب، ثم إلى قدرة تثبت انتقالها على مهام لم يرها؟

المقترح الجديد ليس زيادة عدد الوكلاء، بل **external capability acquisition**: اكتساب قدرات خارج الأوزان عن طريق تحويل residuals إلى operators، ثم operators إلى capability graph، مع feedback وانتقاء وذاكرة واختبارات مضادة.

---

## 2) درس الذرات والمواد: القوة في العلاقات والعيوب المضبوطة

التشبيه الذي طرحه المستخدم صحيح في جوهره مع تصحيح مهم: المادة لا تصبح قوية لأن الذرات كثيرة فقط، بل لأن ترتيبها وروابطها وحدودها وحركتها تحت الضغط تنتج خاصية كلية. والأهم أن البلورة المثالية ليست دائماً الأفضل هندسياً؛ العيوب مثل dislocations وحدود الحبيبات تغيّر القوة واللدونة. مراجع علم المواد تشرح أن حركة dislocations هي آلية التشوه البلاستيكي، وأن منع حركتها بحدود الحبيبات أو الشوائب أو الرواسب يقوي المادة، بينما إزالة العيوب تماماً قد تجعلها هشة. [1](https://www.engr.colostate.edu/laboratories/ceramics/wp-content/uploads/sites/29/2017/10/Callister_ch07_ZC.pdf) [2](https://dspace.mit.edu/bitstream/handle/1721.1/75283/3-091-fall-2004/contents/readings/notes_6.pdf)

الترجمة المعمارية:

| المادة | TAEC v2 |
|---|---|
| atom | primitive cognitive operator |
| bond | typed interface: precondition/postcondition |
| lattice | capability graph |
| defect/dislocation | residual: expected − observed |
| stress | adversarial task / distribution shift |
| strengthening | operator survives counterexamples |
| fracture | scope breach / regression / false acceptance |
| phase transition | stable held-out capability composition |

العيب ليس skill. العيب **إشارة** تحتاج تفسيراً. لا نضيف كل failure إلى الذاكرة؛ نستخرج أصغر residual سببي، ثم نختبر هل يمكن تحويله إلى operator قابل لإعادة الاستخدام.

---

## 3) درس التعقيد: لا emergent intelligence بلا feedback وتغيرات غير خطية

Complex Adaptive Systems لا تحصل على سلوك كلي جديد من جمع الأجزاء فقط. الأدبيات تلخص عناصر مثل العلاقات many-to-many، self-organization، feedback، التكيف، الذاكرة، واستكشاف/استغلال الموارد. السلوك الكلي يعتمد على التفاعلات وليس على خصائص جزء منفرد. [1](https://pmc.ncbi.nlm.nih.gov/articles/PMC7187952/) [2](https://www.mdpi.com/2079-8954/12/2/45)

النتيجة ضد التصميم القديم:

```text
5 agents + shared notes ≠ emergent intelligence
```

الحد الأدنى لادعاء emergence هندسي هو:

```text
primitive operators
+ compatible bonds
+ reciprocal feedback
+ selection pressure
+ persistent memory
+ resource limits
+ non-linear composition
+ measurable phase transition
```

هذا يعيد تعريف TAEC: لا يكون pipeline ثابتاً من Scout ثم Builder ثم Verifier، بل **lattice ديناميكية**؛ كل operator يتفعل عندما تتحقق preconditions، وينتج observation يغير قابلية operators أخرى للتفعيل.

يوجد prior art واضح لهذا المبدأ في Hearsay-II: knowledge sources مستقلة تعمل بأسلوب hypothesize-and-test، وتتواصل عبر blackboard عالمي، ويُختار التركيز بناءً على hypotheses ودرجات صلاحيتها. [1](https://apps.dtic.mil/sti/pdfs/ADA025171.pdf) لذلك blackboard وحده ليس ابتكاراً؛ الجديد المرشح يجب أن يكون في **تعلم operators من residuals مع بوابة انتقال capability**، لا في مجرد مشاركة state.

---

## 4) درس active inference: الفعل يجب أن يقلل الخطر والغموض معاً

أبحاث active inference تصف agent يحتفظ بنموذج توليدي للعالم، ويختار أفعالاً تقلل expected free energy؛ أي يوازن بين الوصول إلى حالة مرغوبة وبين تقليل uncertainty/ambiguity. [1](https://arxiv.org/pdf/2207.06415) [2](https://arxiv.org/html/2401.12917)

لن ندّعي تطبيق free-energy principle حرفياً على Terra، لكن نأخذ منه آلية عملية:

كل قرار routing لا يسأل فقط «ما أعلى احتمال للنجاح؟»، بل:

```text
expected task utility
− execution risk
− ambiguity
+ information gain
− token/time cost
```

وبالتالي قد يختار النظام سؤال clarification أو probe صغيراً بدلاً من تنفيذ خطة كبيرة. هذه ليست قاعدة `ask if unclear` ثابتة؛ إنها سياسة لاكتساب المعلومات عندما تكون قيمة المعلومة أعلى من كلفة السؤال.

---

## 5) درس compositionality: التقدم الحقيقي هو إعادة تركيب primitives

الأبحاث على systematic/compositional generalization تبين أن القدرة المهمة ليست حفظ primitive، بل إعادة تركيب primitives في combinations لم تُرَ. عمل Nature على Meta-Learning for Compositionality وجد أن تدريباً موجهاً للتركيب يمكن أن يحسن systematic generalization دون إضافة symbolic machinery إلى النموذج. [1](https://www.nature.com/articles/s41586-023-06668-3)

إذن capability graph في TAEC v2 يجب ألا يثبت أن operator نجح على نفس task فقط. يجب أن يثبت:

1. `in-distribution reuse`.
2. `primitive substitution`.
3. `new composition`.
4. `context transfer`.
5. `negative transfer`.

مثلاً لا يكفي أن ينجح `ScopeLedger` في مهمة ملفات Python؛ يجب اختباره على:

```text
Python files → docs files → config files → mixed repository
```

مع تغيير أسماء الملفات وترتيب الرسائل والـdecoy paths.

---

## 6) درس self-evolution: الذاكرة المرئية ليست دليلاً على التعلم

تقييمات self-developing agents الحديثة تؤكد أن المكسب المرئي لا يكفي: يجب اختبار held-out، وتجميد artifact، وقياس retention وtransfer. benchmark منشور عن self-developing agents أظهر أن اتجاه المكسب المرئي وافق held-out في 34 من 64 انتقالاً فقط، وأن نسخاً قليلة من التطور كانت الأفضل على held-out. [1](https://self-developing-agents.github.io/)

EvoPathBench يضيف أبعاداً مهمة: generalization، retention بعد distractor learning، rule adaptation، وقياس ما إذا كان artifact المختار أفضل فعلاً من المرشحين المرفوضين. [1](https://arxiv.org/html/2609.24663)

إذن TAEC v2 لا يقبل operator لأنه حسن dev task. كل operator له lifecycle:

```text
CANDIDATE
→ DEV_VALIDATED
→ ADVERSARIAL_TESTED
→ HELDOUT_VALIDATED
→ CRYSTALLIZED
→ MONITORED
→ RETIRED / ROLLED_BACK
```

ويجب الاحتفاظ بالمرشحين المرفوضين، لأن قرار الانتقاء نفسه يحتاج audit.

---

## 7) درس test-time adaptation: هناك مسار أعمق من prompt فقط

توجد أبحاث test-time learning تغيّر subset من الأوزان أو تستخدم self-supervised signals أثناء inference، مثل TLM الذي يستفيد من input perplexity وLoRA، وأبحاث أحدث عن fast weights. [1](https://arxiv.org/pdf/2505.20633) [2](https://arxiv.org/html/2604.06169)

هذا المسار غير متاح في Codex الحالي ولا ينسجم مع قرارنا بعدم تحميل نماذج محلية أو تعديل weights Terra. لكنه يثبت أن السؤال العلمي الصحيح ليس فقط «ما prompt الأفضل؟» بل:

```text
ما الذي يمكن أن يتكيف في وقت التشغيل؟
```

في حالتنا، المتغيرات القابلة للتكيف هي:

- operator selection.
- task decomposition.
- evidence retrieval.
- verifier composition.
- clarification policy.
- budget allocation.
- skill graph edges.

هذا **policy-level test-time learning**، لا weight-level learning.

---

## 8) الاختراع المرشح: Residual-to-Capability Compiler

الاسم المؤقت: **RCC — Residual-to-Capability Compiler**، ويعمل كمحرك جديد داخل TAEC v2.

### 8.1 Residual

```json
{
  "task_family": "multi_file_repair",
  "expected_invariant": "changed paths ⊆ allowed paths",
  "observed_failure": "edited forbidden file",
  "minimal_residual": "scope ledger absent after round 1",
  "evidence": ["diff", "trace", "evaluator"],
  "causal_hypotheses": ["memory_loss", "router_skip"],
  "counterfactuals": ["contract_only", "memory_only"]
}
```

### 8.2 Operator

```json
{
  "operator_id": "scope_ledger_v1",
  "preconditions": ["multi_file_task", "write_access"],
  "action": "materialize allowed_paths before every write round",
  "postconditions": ["diff_subset_of_allowed_paths"],
  "verifier": "path_allowlist_v2",
  "cost_estimate": {"tokens": 180, "seconds": 1.2},
  "provenance": ["residual_id"],
  "status": "CANDIDATE"
}
```

### 8.3 Capability

لا تتحول مجموعة operators إلى capability إلا إذا نجحت على:

```text
same task family
new composition
primitive substitution
adversarial perturbation
retention after unrelated tasks
```

### 8.4 Meta-controller

يختار operator أو composition بناءً على posterior empirical utility:

```text
score(operator, task) =
  expected_acceptance_gain
  + information_gain
  − token_cost
  − latency_cost
  − scope_risk
  − regression_risk
```

لا نحتاج في النسخة الأولى إلى Bayesian sophistication كاملة؛ يكفي سجل تجريبي calibrated مع confidence وsample count وexpiry. المهم أن الاختيار يتعلم من outcomes، لا من أسماء جذابة.

---

## 9) كيف يختلف هذا عن TAEC v0؟

| TAEC v0 | TAEC v2/RCC |
|---|---|
| يطبق contract ثابتاً | يتعلم أي contract/operator يفيد |
| يسجل failures | يستخرج residual سببي |
| memory للقرارات | memory للقدرات والعلاقات وشروط التفعيل |
| verifier للحل الحالي | verifier لاختبار انتقال capability |
| full stack ثابت | composition ديناميكي |
| dev/held-out للمقارنة | process checkpoints وretention وtransfer |
| repair loop | repair operator قابل لإعادة الاستخدام |
| no claim before evidence | skill لا تتبلور إلا بعد adversarial gate |

TAEC v0 يبقى مهماً كـmeasurement kernel. لكن RCC هو محاولة جعل النظام يتعلم **كيف يبني أدوات التفكير والتنفيذ الخاصة بنقاط ضعفه**.

---

## 10) الاختبار الذي سيقرر إن كان هذا اختراعاً مفيداً

نحتاج benchmark جديداً لا يسأل فقط: هل أنجز task؟ بل:

1. **Residual quality:** هل اكتشف سبب الفشل الحقيقي؟
2. **Operator reuse:** هل operator الناتج ينفع في task جديد؟
3. **Compositional transfer:** هل ينفع مع primitive جديد وتركيب جديد؟
4. **Retention:** هل يبقى بعد distractor tasks؟
5. **Negative transfer:** هل أفسد مهاماً أخرى؟
6. **Selection accuracy:** هل operator الذي اختاره النظام كان أفضل من المرشحين؟
7. **Cost-adjusted gain:** هل المكسب يستحق tokens/minutes؟
8. **Artifact-off/on:** هل الفائدة من skill خارجية فقط أم من policy مستقرة؟

لا نعلن capability acquisition إلا إذا تحقق:

```text
heldout_gain > noise_floor
and transfer_gain > 0
and retention_loss ≈ 0
and negative_transfer below threshold
and cost-adjusted utility positive
```

---

## 11) prior-art والحكم الحالي

المكونات منفردة لها سوابق واضحة: blackboard systems، active inference، compositional meta-learning، program repair، test-time adaptation، self-evolving skill memories، وLLM orchestration. لذلك لا يوجد الآن أساس لادعاء «لم يعرفه أحد».

التركيب المرشح للابتكار هو:

> **نظام خارجي يحول residuals الخاصة بنموذج واحد إلى typed executable operators، يركبها في capability lattice، ويقبلها فقط إذا أثبتت انتقالاً compositional وretention على held-out مع تكلفة مضبوطة.**

هذا proposition بحثي، لا حقيقة مثبتة. يحتاج prior-art attack مخصصاً وتجربة مقارنة مع TAEC v0.

## القرار

لا نرسل Codex لإكمال dev protocol حالياً باعتباره نهاية الطريق. نحتفظ بالمختبر الحالي كـmeasurement kernel، ونصمم TAEC v2/RCC قبل أي دمج في Fawri.

الخطوة التالية الصحيحة ليست إضافة agent سادس، بل كتابة formal spec صغيرة لـRCC ثم تنفيذ prototype واحد: `scope_ledger` أو `failure_to_operator` على مهام Codex، مع held-out compositional transfer.
