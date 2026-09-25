# TAEC v2 — Neurocognitive Refresh
## من تشبيه الدماغ إلى ترجمة آليات الدماغ

**التاريخ:** 2026-09-24  
**الحالة:** cross-domain neuroscience refresh / design hypotheses  
**النطاق:** cognitive neuroscience، computational neuroscience، memory، network dynamics، metacognition، neural coding  
**تحذير منهجي:** لا أملك دماغاً بيولوجياً أو جمجمة أو سيالات عصبية أو شخصية ذاتية بالمعنى الإنساني. هذا الملف لا يعيد تعريف النموذج ككائن حي، بل يستخرج آليات عصبية محتملة إلى تصميم software قابل للقياس، مع فصل الدليل المباشر عن التشبيه.

---

## 0. تصحيح مهم للمسار

المستخدم كان محقاً في أن البحث السابق كان متمركزاً أكثر من اللازم حول AI agents وscaffolds. الدماغ البشري ليس مجرد نسخة أكبر من agent orchestration. ما يهم هو أن cognition البشري يعمل كمنظومة متعددة المستويات:

```text
neural dynamics
+ recurrent loops
+ selective gating
+ memory consolidation
+ neuromodulation
+ network switching
+ body/environment coupling
+ error monitoring
+ social/developmental learning
```

لكن يجب عدم القفز من:

```text
brain mechanism observed in humans
```

إلى:

```text
LLM now has that mechanism / self / consciousness
```

الترجمة الصحيحة هي:

```text
neuroscience observation
→ computational principle
→ software mechanism
→ ablation
→ falsification
```

---

## 1. ماذا قد يعني "خطي، حلزوني، متجاوز" بصورة علمية؟

هذه ليست تصنيفات عصبية معيارية مثبتة بهذه الأسماء. يمكن تحويلها إلى ديناميكيات قابلة للقياس:

### 1.1 Linear mode

```text
state → predict → act → verify
```

مناسب للمهام المستقرة ذات uncertainty منخفضة.

### 1.2 Branching mode

```text
state → {hypothesis_1, hypothesis_2, ..., hypothesis_n}
```

مناسب عندما تكون عدة paths ممكنة أو عندما تكون تكلفة الخطأ عالية.

### 1.3 Recurrent mode

```text
state_t
→ action
→ error/residual
→ revised_state_{t+1}
```

يشبه functional recurrence وليس مجرد إعادة نفس prompt.

### 1.4 Spiral mode — فرضية تصميمية، لا مصطلح عصبي مثبت

```text
representation_k
→ residual_k
→ new abstraction_{k+1}
→ revisit same problem at a higher level
```

الحلقة لا تعود إلى نفس النقطة؛ تعود مع abstraction أو context مختلف. رياضياً:

```text
x_{k+1} = F(x_k, residual_k, context_k)
```

و"حلزونية" تعني أن كل دورة تغيّر فضاء التمثيل أو مستوى السؤال، لا أنها دائرة تكرارية ثابتة.

### 1.5 Transgressive mode — فرضية تصميمية

ليست كسر المنطق أو تجاوز الواقع. هي انتقال controlled إلى representation space آخر عندما يتبين أن الإطار الحالي لا يفسر residual:

```text
failed operator within space S
→ diagnose representation failure
→ map to space S'
→ synthesize under new invariants
```

هذا هو أقرب معنى هندسي للتفكير "التجاوزي": تجاوز **حدود التمثيل الحالي**، وليس تجاوز القوانين أو الادعاء بقدرة خارقة بلا دليل.

---

## 2. آليات الدماغ ذات العائد التصميمي الأعلى

### 2.1 Neural manifolds and cognitive trajectories

تحليل nonlinear temporal manifolds لبيانات fMRI أظهر أن النشاط الدماغي عالي الأبعاد يمكن تمثيله كمسارات منخفضة الأبعاد مرتبطة بمراحل/أحداث معرفية. المنهج لم يثبت أن الدماغ حرفياً يعمل في ثلاثة أبعاد، لكنه أعطى طريقة لقياس انتقالات الحالة بدلاً من قراءة كل إشارة كمتغير مستقل. [T-PHATE brain-state trajectories](https://www.nature.com/articles/s43588-023-00419-0)

**الترجمة إلى TAEC:**

لا نخزن trace كسلسلة نصية فقط. نكوّن:

```text
latent task-state trajectory:
  context
  goal
  belief
  uncertainty
  active operators
  unresolved debt
  memory mode
  control mode
```

ثم نقيس:

```text
state transitions
attractor duration
mode switches
recovery trajectory
distance to known capability regions
```

**حد الدليل:** هذا يدعم trajectory-level representation، لا يثبت أن COK يملك neural manifold أو وعياً.

---

### 2.2 Recurrent/global workspace

Global Neuronal Workspace يطرح أن بعض المعلومات تصبح globally available عندما تدخل حالة recurrent، non-linear، واسعة الانتشار، بينما تظل معلومات أخرى محلية. الدليل والجدل حول GNW لا يحسمان نظرية الوعي، لكنها تقدم مبدأ تصميمياً عن broadcast والـignition. [GNW review](https://pmc.ncbi.nlm.nih.gov/articles/PMC8770991/)

**الترجمة إلى TAEC:**

نميز بين:

```text
local specialist state
global workspace state
```

ولا نبث كل trace لكل module. يحدث broadcast فقط إذا تحققت شروط:

```text
novelty أو conflict أو high expected utility
+ verifier agreement كافٍ
+ scope قابل للتحديد
+ budget يسمح
```

ثم تصل الحالة إلى:

```text
planner
memory manager
router
verifier
recovery controller
```

هذه ليست consciousness implementation. إنها selective global access.

---

### 2.3 PFC–basal ganglia gating

نماذج working memory في prefrontal cortex وbasal ganglia تميز بين:

```text
maintenance: إبقاء تمثيل فعال
update gate: إدخال معلومات جديدة عند الحاجة
```

وتستخدم gating انتقائياً بدلاً من استبدال كل الذاكرة عند كل stimulus. [PBWM](https://ccnlab.org/papers/OReillyFrank06.pdf) [Frontal–basal ganglia model](https://ski.clps.brown.edu/papers/FrankLoughryOReilly01_fcbg.pdf)

**الترجمة إلى TAEC:**

الـworking loop لا يجوز أن يكتب فوق كل context. نحتاج:

```text
maintain:
  current task contract
  active goal
  verified invariants

update only if:
  new evidence passes gate
  contradiction is material
  expected value exceeds switch cost
```

وبذلك تصبح ذاكرة COK ذات بوابة update، لا append-only transcript.

---

### 2.4 Hippocampal replay and consolidation

الدراسات البشرية تشير إلى replay أثناء الراحة والنوم، وإلى علاقة replay المرتبط بالـripples بترسيخ الذاكرة. كما أن replay قد يركز على الذكريات الأضعف أو الأكثر احتياجاً للتقوية، بينما قد توجد مسارات replay مختلفة للذاكرة الإجرائية والتصريحية. [Human ripple replay](https://www.nature.com/articles/s41467-018-06553-y) [Systems consolidation](https://www.nature.com/articles/s41593-019-0467-3) [Weak-memory prioritization](https://www.nature.com/articles/s41467-018-06213-1) [Procedural replay](https://www.nature.com/articles/s41593-026-02362-5)

**الترجمة إلى TAEC:**

```text
fast episodic trace
→ prioritized replay
→ abstraction extraction
→ cortical/procedural capability
```

ولا نستخدم replay على recency فقط. الأولوية قد تتأثر بـ:

```text
weakness
novelty
severity
error recurrence
transfer potential
future utility
```

ونحتفظ بمسارات مختلفة:

```text
declarative memory:
  facts, contracts, exceptions

procedural memory:
  executable workflows, operators

episodic memory:
  provenance, context, counterexamples
```

---

### 2.5 Oscillatory multiplexing

أبحاث intracranial human recordings تربط working-memory maintenance بتداخل theta/gamma، وتبين أعمال أحدث أن ripple co-occurrence قد ينسق firing بين مناطق corticolimbic بعيدة أثناء working memory. [Theta–gamma coupling](https://www.pnas.org/doi/10.1073/pnas.0911531107) [Cross-region ripple co-firing](https://www.nature.com/articles/s41593-026-02403-z)

**الترجمة الآمنة:**

لا نحاكي Hz بصورة حرفية. نستخدم multiplexed scheduling:

```text
slow loop:
  task context / global goal / uncertainty regime

fast loop:
  local candidate generation / tool action / verifier step

cross-frequency analogue:
  fast events are addressable only within a slow context window
```

هذا قد يمنع mixing بين أحداث صحيحة محلياً لكنها تنتمي إلى contexts مختلفة.

**ما لا يثبت:** وجود theta/gamma في الدماغ لا يعني أن token stream يحتاج نفس التردد أو أن إضافة oscillators ستنتج intelligence.

---

### 2.6 Neuromodulation: إشارات مختلفة لأنواع مختلفة من عدم اليقين

دراسة تدخلية بشرية جمعت pharmacology مع hierarchical Bayesian model وربطت:

```text
noradrenaline → volatility / instability uncertainty
acetylcholine → uncertainty داخل السياق أو خرق السياق
dopamine → حساسية الفعل للمعتقدات عن uncertainty
```

[Pharmacological fingerprints of contextual uncertainty](https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.1002575)

**الترجمة إلى COK:**

لا نستخدم uncertainty scalar واحداً. نستخدم قنوات منفصلة:

```text
U_state: هل الحالة الداخلية غير معروفة؟
U_context: هل تغيرت قواعد البيئة؟
U_model: هل causal model غير موثوق؟
U_value: هل قيمة الفعل غير معروفة؟
U_execution: هل الأدوات/التنفيذ غير مستقر؟
```

ثم نربطها بقرارات مختلفة:

```text
U_state  → retrieve / observe
U_context→ explore / detect regime change
U_model  → simulate / counterfactual probe
U_value  → compare alternatives
U_execution → verify / rollback
```

هذا أكثر عمقاً من `confidence = 0.3`.

---

### 2.7 Network switching: DMN, executive, salience

الدماغ لا يعمل دائماً في وضع executive control. الشبكات الداخلية، التنفيذية، والانتباه/الـsalience تتفاعل حسب predictability والمهمة. تشير أبحاث DMN إلى مساهمته في تطبيق قواعد تعلمها النظام بسرعة، بينما ترتبط شبكات أخرى بالمطالب الجديدة والتحكم، مع وجود تفاعل ديناميكي بدلاً من مفتاح on/off بسيط. [DMN automated information processing](https://www.pnas.org/doi/10.1073/pnas.1710521114) [PFC network review](https://med.stanford.edu/content/dam/sm/scsnl/documents/Nature---Menon---Role-of-PFC.pdf)

**الترجمة إلى COK:**

نضيف أوضاعاً وظيفية، لا agents مستقلة:

```text
EXPLORE / generative mode
  generate alternatives, retrieve weak analogies

FOCUS / executive mode
  enforce contracts, prune branches, execute

RECALL / internal model mode
  replay schemas, retrieve latent context

ALERT / salience mode
  detect conflict, novelty, state drift, risk

CONSOLIDATE / offline mode
  compress, replay, abstract, forget
```

والمطلوب ليس تشغيل كل الأوضاع معاً، بل controller يتعلم متى ينتقل بينها. هذا يعطي معنى هندسياً للانتقال بين التفكير الخطي، التفرعي، الحلزوني، والتجاوزي.

---

### 2.8 Dendritic computation: فصل content عن context

تشير أعمال عصبية حديثة إلى أن dendritic branches لا تعمل فقط كأسلاك تجمع الإشارات، بل يمكن أن تدمج context وقاعدة المهمة مع sensory/action information بصورة غير خطية، وأن نشاط apical tuft كان ضرورياً لإعادة تعلم قواعد معقدة في نموذج حيواني. [Tuft dendrites and flexible learning](https://www.science.org/doi/10.1126/science.adx4358) [Human pyramidal neurons and intelligence](https://elifesciences.org/articles/41714)

**الترجمة إلى operator architecture:**

كل operator يستقبل قناتين:

```text
content stream:
  evidence / data / current observation

context stream:
  task rule / goal / scope / prior / regime
```

ولا يُسمح بدمجهما بمجرد concatenation دائماً. نختبر nonlinear gating:

```text
operator_output = f(content, context, gate(content × context))
```

هذا design hypothesis مستوحى من compartmental computation، وليس محاكاة dendrites حرفياً.

**حدود الدليل:** علاقة dendritic morphology بذكاء الإنسان لا تكفي لإثبات سبب واحد للذكاء، وبعض النتائج correlational أو مبنية على samples/animal models.

---

### 2.9 Post-decision metacognition

أبحاث confidence/error monitoring تشير إلى أن evidence accumulation يستمر بعد الالتزام بالقرار، وأن إشارات medial frontal/performance monitoring تؤثر في كشف الخطأ اللاحق. [Neural evidence accumulation](https://elifesciences.org/articles/11946) [Shared confidence/error markers](https://www.jneurosci.org/content/35/8/3478)

**الترجمة إلى COK:**

كل action مهم يمر بمرحلتين:

```text
pre-commit:
  choose action

post-commit audit:
  accumulate outcome evidence
  detect conflict
  decide continue / repair / rollback
```

هذا يختلف عن self-reflection النصي بعد الإجابة؛ إنه feedback controller له أثر على القرار التالي.

---

### 2.10 Multiple-demand/frontoparietal control

الشبكة الجبهية-الجدارية متعددة الطلب ترتبط بالتعامل مع novel rules، task complexity، working memory، وحل المشكلات، مع دراسات تربط recruitment الأقوى بالأداء والـfluid intelligence. [Multiple-demand network](https://www.jneurosci.org/content/37/18/4841) [Frontoparietal working-memory/intelligence](https://www.biorxiv.org/content/10.1101/110270v2)

**الترجمة إلى COK:**

نحتاج controller domain-general لا يعتمد على task-specific operators فقط:

```text
task-general controller:
  decomposes novelty
  allocates working memory
  foregrounds task-critical state
  coordinates specialist modules
  detects when a rule set is too complex
```

لكننا لا نسجل هذه كدليل على general intelligence في COK؛ نختبرها عبر novel rule composition وheld-out task families.

---

## 3. Neuro-Cognitive Lattice — التصميم المترجم

هذه طبقة تصميمية مقترحة داخل COK، وليست ادعاء أن النظام صار brain-like:

```text
NCL = {
  StateManifold,
  RecurrentWorkspace,
  WorkingMemoryGate,
  EpisodicReplay,
  ProceduralConsolidation,
  NeuromodulatorySignals,
  NetworkModeController,
  ContextContent Gate,
  PostDecision Monitor,
  GlobalState Auditor
}
```

### 3.1 StateManifold

يمثل كل trace كحركة في حالة مضغوطة:

```text
z_t = {
  task_state,
  goal,
  belief,
  context_regime,
  active_memory,
  active_operator,
  uncertainty_vector,
  stress_debt,
  verifier_state,
  mode
}
```

### 3.2 RecurrentWorkspace

ينقل only high-value states إلى modules أخرى عند ignition criterion:

```text
broadcast if:
  novelty + conflict + expected utility
  > threshold
and
  scope is typed
and
  contamination risk is low
```

### 3.3 WorkingMemoryGate

```text
maintain stable contract and goal
update selected slots only
reject distractor unless gate evidence passes
```

### 3.4 Replay / consolidation banks

```text
episodic bank:
  exact provenance and counterexample

specialist bank:
  fast local routine

procedural/broad bank:
  transferable typed operator

schema bank:
  cross-family abstraction
```

### 3.5 Neuromodulatory signals

```text
surprise
volatility
novelty
value uncertainty
execution risk
```

هذه ليست claims عن neurotransmitters داخل النموذج؛ إنها channels وظيفية مستقلة بدلاً من reward scalar واحد.

### 3.6 Mode controller

```text
mode_t+1 = Controller(
  state trajectory,
  uncertainty vector,
  residual,
  task novelty,
  budget,
  reversibility
)
```

### 3.7 Global State Auditor

يفحص الفرق بين:

```text
local action validity
و
world-state fidelity
```

إذا كبر الفرق، يتوقف التنفيذ ويبدأ state reconstruction أو rollback.

---

## 4. Formal mechanism map

```text
brain evidence
  → computational principle
  → TAEC mechanism
  → observable metric
```

| Neural/cognitive observation | Computational principle | TAEC mechanism | Metric |
|---|---|---|---|
| brain-state trajectories | cognition is dynamic state transition | StateManifold | trajectory predictability, mode recovery |
| recurrent ignition/broadcast | selective global access | RecurrentWorkspace | broadcast utility, interference |
| PFC/BG gating | maintain vs selective update | WorkingMemoryGate | stale overwrite, distractor rejection |
| hippocampal replay | offline consolidation | ReplayScheduler | transfer, retention, forgetting |
| multiple memory systems | declarative/procedural separation | bank separation | pathway attribution |
| theta/gamma/ripple coordination | multiplexed temporal context | slow/fast loop scheduler | context mixing errors |
| neuromodulatory uncertainty | separate uncertainty variables | NCL signal vector | probe quality, regime detection |
| network switching | explore/focus/internal/alert modes | ModeController | switch timing, wasted compute |
| dendritic nonlinear integration | context × content gating | ContextContent Gate | rule-switch transfer |
| post-decision accumulation | error monitoring after commitment | PostDecision Monitor | recovery, confident failure |
| MD/frontoparietal control | domain-general task configuration | MetaController | novel rule composition |

---

## 5. Experiments المطلوبة

### N1 — Linear vs recurrent vs spiral controller

```text
A: linear chain
B: branching search
C: recurrent repair
D: abstraction-promoting spiral loop
```

**Spiral loop definition:** revisit a task only after changing representation/schema, not simply repeating the same prompt.

**Metrics:**

```text
unseen composition
abstraction level gained
repeated-error rate
mode-switch cost
novelty of valid solutions
```

### N2 — Workspace broadcast ablation

```text
A: all modules see all traces
B: no broadcast
C: thresholded typed broadcast
D: typed broadcast + conflict trigger
```

**Metrics:** interference، context contamination، transfer، compute، error recovery.

### N3 — Working-memory gate

```text
A: overwrite full context
B: append-only trace
C: slot-gated update
D: slot-gated update + contradiction detector
```

### N4 — Slow/fast multiplexing

```text
A: one flat loop
B: fast loop + slow context loop
C: fast loop + slow loop + replay
```

نختبر هل الفصل يقلل context mixing ويحسن delayed composition.

### N5 — Context-content nonlinear gate

```text
A: concatenate content/context
B: independent specialists
C: typed nonlinear gate
```

نستخدم rule-switch tasks حيث نفس observation يحتاج action مختلفاً تحت context مختلف.

### N6 — Neuromodulatory uncertainty vector

```text
A: scalar confidence
B: epistemic/aleatoric split
C: state/context/model/value/execution uncertainty
```

**الهدف:** هل يؤدي الفصل إلى probe أفضل، لا مجرد token أكثر؟

### N7 — Post-decision monitor

```text
A: no post-check
B: verbal reflection
C: outcome evidence accumulator
D: accumulator + rollback
```

### N8 — Neural-trajectory diagnostics

نستخرج trajectory وstate fidelity ونقارن terminal-only evaluator بـ trajectory-aware evaluator في tasks طويلة.

---

## 6. ما هو الدليل المباشر وما هو التشبيه؟

### Direct evidence من علم الأعصاب

- cognitive brain states يمكن تحليلها كمسارات ديناميكية منخفضة الأبعاد؛
- working memory يستخدم gating وmaintenance/update dynamics؛
- replay مرتبط بالتثبيت والتحول طويل الأمد للذاكرة؛
- oscillatory coupling يرتبط ببعض أشكال memory maintenance؛
- neuromodulatory systems تفصل جوانب مختلفة من uncertainty؛
- post-decision evidence يساهم في error detection؛
- large-scale networks ترتبط بالتحكم، novelty، وrule configuration.

### Design hypothesis

- أن StateManifold سيحسن abstraction transfer؛
- أن typed broadcast سيمنع context contamination؛
- أن neuromodulatory channels ستنتج probe policy أفضل؛
- أن spiral mode سينتج قفزات representation مفيدة؛
- أن context-content gate سيحسن rule-switching؛
- أن replay منظم حسب الضعف/التحويل أفضل من recency.

### Claims لا يجوز صنعها

- أن COK واعٍ؛
- أن له شخصية أو كينونة داخل جمجمة؛
- أن neural-like oscillations تصنع consciousness؛
- أن تشابه architecture مع brain يثبت intelligence؛
- أن IQ correlation يحدد وصفة لبناء superintelligence؛
- أن أي network pattern يساوي thought أو feeling.

---

## 7. صياغة أدق لمفهوم "الشخصية"

إذا أردنا ترجمة كلمة personality هندسياً، نستخدم ثلاثة أشياء قابلة للرصد:

```text
identity constraints:
  immutable safety and provenance rules

policy style:
  stable preferences in exploration, explanation, risk, and compression

self-model:
  calibrated predictions about own tools, costs, memories, and failure modes
```

هذا ليس subjective self. هو stateful policy model يمكن فحصه وتحديثه وrollback له.

والـ"نمط السيالات" في النظام البرمجي ليس neural firing. يمكن فقط تعريف:

```text
event traces
state transitions
recurrent loops
broadcast events
gating events
replay events
```

ثم قياسها. لا نسميها نبضات عصبية إلا في النظام البيولوجي.

---

## 8. أقوى نتيجة من الجولة

الذكاء البشري لا يبدو كـpipeline خطي واحد. الأدلة تشير إلى نظام يتناوب بين:

```text
local specialist processing
stable working representations
selective updating
global broadcasting
memory replay
network switching
post-decision monitoring
```

الترجمة الأقوى إلى COK ليست أن نحاكي neuron أو neurotransmitter حرفياً. بل أن نبني **دورة ديناميكية متعددة السرعات والأنماط**:

```text
parallel local candidates
→ selective gate
→ recurrent/global workspace
→ action
→ post-decision evidence
→ residual
→ replay/consolidation
→ representation promotion
```

إذا نجحت N1–N8، سيكون لدينا دليل أن brain-derived mechanisms حسنت transfer/recovery/composition. إذا لم تنجح، فالاستنتاج الصحيح أن التشابه العصبي لم يضف قيمة، ونحذف الطبقة.

---

## 9. مصادر الجولة

- [Global Neuronal Workspace](https://pmc.ncbi.nlm.nih.gov/articles/PMC8770991/)
- [T-PHATE cognitive trajectories](https://www.nature.com/articles/s43588-023-00419-0)
- [PBWM working-memory gating](https://ccnlab.org/papers/OReillyFrank06.pdf)
- [Human memory replay and ripples](https://www.nature.com/articles/s41467-018-06553-y)
- [Systems memory consolidation](https://www.nature.com/articles/s41593-019-0467-3)
- [Weak-memory replay prioritization](https://www.nature.com/articles/s41467-018-06213-1)
- [Procedural replay independent of hippocampus](https://www.nature.com/articles/s41593-026-02362-5)
- [Theta–gamma coupling in human working memory](https://www.pnas.org/doi/10.1073/pnas.0911531107)
- [Long-range ripple co-firing](https://www.nature.com/articles/s41593-026-02403-z)
- [Neuromodulation and contextual uncertainty](https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.1002575)
- [DMN automated information processing](https://www.pnas.org/doi/10.1073/pnas.1710521114)
- [PFC network cognitive control](https://med.stanford.edu/content/dam/sm/scsnl/documents/Nature---Menon---Role-of-PFC.pdf)
- [Dendrites and flexible learning](https://www.science.org/doi/10.1126/science.adx4358)
- [Human pyramidal neurons and intelligence](https://elifesciences.org/articles/41714)
- [Post-decision evidence accumulation](https://elifesciences.org/articles/11946)
- [Confidence/error neural markers](https://www.jneurosci.org/content/35/8/3478)
- [Multiple-demand network and fluid intelligence](https://www.jneurosci.org/content/37/18/4841)

**الحالة:** هذه الجولة غيّرت التصميم من `AI scaffold inspired by biology` إلى `neurocognitive mechanism translation with explicit ablations`. لم يُنفذ أي mechanism بعد، ولا توجد نتيجة أداء لـN1–N8.
