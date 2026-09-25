# TAEC v2 — Deep Design Refresh
## Residual Capability Compiler (RCC) داخل Cognitive Lattice
## Candidate kernel: COK — Cognitive Organism Kernel

**التاريخ:** 2026-09-24  
**الحالة:** formal design / prior-art synthesis / experiment-ready  
**تنبيه:** هذه وثيقة تصميم وفرضيات قابلة للدحض. لا تسجل نتيجة أداء، ولا تدعي وعياً أو self-modifying model weights، ولا تدعي novelty قبل استكمال المقارنة.

---

## 0. ما الذي تغيّر في هذه الجولة؟

النسخة السابقة كانت ترى RCC كمسار:

```text
failure → residual → operator → capability graph → held-out transfer
```

التحسين الأهم الآن هو أن **operator الناجح وحده ليس capability**. القدرة القابلة للنقل يجب أن تكون **closed capability**:

```text
representation/interface
+ executable operator
+ pre/postconditions
+ verifier
+ routing context
+ memory/replay pointer
+ recovery/rollback behavior
```

أي أن هدف TAEC ليس فقط كتابة fix أو prompt أفضل، بل اكتشاف **وحدة مغلقة** تستطيع:

1. التعرف على شروط صلاحيتها؛
2. تنفيذها؛
3. التحقق من ناتجها؛
4. معرفة متى لا تصلح؛
5. الانتقال إلى task family أو composition لم تُرَ؛
6. الرجوع دون تخريب القدرات السابقة.

هذه نقطة تصميمية وليست ادعاءً أن prior art لم يسبقها. أجزاء الفكرة لها سوابق واضحة في typed program synthesis، contract-based synthesis، modular routing، replay، وrecursive harness improvement؛ القيمة المحتملة هنا هي تركيبها في اختبار واحد صارم، ويجب إثبات ذلك تجريبياً.

---

## 1. الحد الفاصل: ماذا يمكن أن يتحسن فعلاً؟

لدينا ثلاثة أشياء يجب عدم خلطها:

```text
M = base model / foundation model
H = external harness: prompts, tools, memory, routing, search, verifiers
K = capability knowledge: typed operators, contracts, traces, graphs
```

في TAEC v2، المسار الآمن القابل للقياس هو:

```text
M ثابت أثناء التجربة
H و K يتطوران عبر نسخ versioned
held-out evaluator ثابت وسري
```

إذن عبارة self-improvement هنا تعني **تحسيناً خارجياً في harness/knowledge/compiler تحت budget ثابت**، لا تغيير weights ولا نشوء ذات أو وعي. إذا أردنا لاحقاً دراسة weight adaptation فهذا مسار منفصل له ضوابطه.

هذا التمييز مهم لأن أعمالاً حديثة في recursive self-improvement تُظهر أن إعادة كتابة harness يمكن أن تحسن البحث تحت ميزانية ثابتة وتنقل المكاسب إلى benchmarks خارجية، لكنها لا تثبت أن النموذج الأساسي نفسه أعاد كتابة أوزانه أو أنه صار self-improving بالمعنى القوي. في AIDE²، بقي النموذج ثابتاً داخل كل loop، وكانت التغييرات في search policy وcontext/memory management وrobustness mechanisms؛ كما أن اختبار قدرة الوكيل المطوَّر على قيادة loop أعلى كان غير حاسم بسبب عدد seeds المحدود. [AIDE²](https://arxiv.org/html/2609.26457)

---

## 2. الفرضية المركزية الجديدة: Abstraction Promotion لا مجرد score optimization

معظم حلقات التحسين تقع في أحد المستويات الآتية:

```text
L0  instance patch       إصلاح حالة واحدة
L1  local operator       قاعدة لمجموعة حالات قريبة
L2  typed capability     operator + contract + verifier + recovery
L3  compositional schema قاعدة قابلة للتركيب عبر task families
L4  meta-controller       تغيير البحث/الذاكرة/التوجيه نفسه
```

الخطأ الشائع هو قبول L0 أو L1 لأنه رفع score محلياً ثم تسميته capability gain.

### فرضية H-PROMOTE

لا تُرقّى نتيجة إلى capability إلا إذا تحركت صعوداً على **Abstraction Promotion Ladder**:

```text
L0 نجاح محلي
  ↓ counterfactual stability
L1 نجاح على neighbors
  ↓ typed verification + scope control
L2 closed capability
  ↓ unseen composition / task-family transfer
L3 reusable schema
  ↓ meta-level benefit without regression
L4 controller improvement
```

ليس ضرورياً أن تمر كل نتيجة بكل مستوى، لكن كل claim يجب أن يحدد مستواه. والقاعدة الصارمة:

```text
score gain ≠ capability gain
capability gain = transfer + retention + compositional reuse + verifier-backed scope
```

### لماذا هذه الفرضية عالية الرافعة؟

لأنها تحول البحث من تحسين الإجابة الحالية إلى اختبار **هل تغيرت مساحة الحلول المتاحة؟**. القياس لا يسأل فقط: هل نجح؟ بل:

- هل نجح في task لم يرها؟
- هل حل composition جديداً من primitives قديمة؟
- هل احتاج trace أو prompt جديداً لكل حالة؟
- هل يعرف متى لا يطبق operator؟
- هل أدت الإضافة إلى regression أو routing monopoly؟

هذه **design hypothesis**، وليست نتيجة مثبتة.

---

## 3. التعريف الرسمي الصغير

### 3.1 الحالة الكلية

نعرّف حالة RCC/COK عند الزمن `t` كالتالي:

```text
Σ_t = (
  B_fast,          # fast specialist bank
  B_broad,         # broad transferable bank
  G_cap,           # typed capability graph
  R_route,         # router priors + inhibition state
  C_contracts,     # assumptions, guarantees, safety contracts
  V_verifiers,     # executable verifiers
  Q_residuals,     # residual queue with provenance
  M_measurement,   # immutable measurement contract
  H_heldout,       # sealed evaluator, inaccessible during search
  P_replay,        # consolidation/replay scheduler
  U_budget,        # token/time/tool budget
  L_ledger         # version, lineage, rollback ledger
)
```

`M_measurement` و`H_heldout` لا يملكهما operator المقترح ولا الـmeta-controller. يمكن للمرشح أن يرى feedback محدوداً من public/dev split، لكن لا يرى السر ولا يستطيع تعديل evaluator.

### 3.2 الأنواع الأساسية

```text
type TaskFamily
 type TaskInstance
 type Trace
 type Evidence
 type Intervention
 type Residual
 type Operator[I, O]
 type Contract
 type Verifier[I, O]
 type Capability
 type Version
```

### 3.3 Residual

الـresidual ليس عبارة "فشل" أو آخر رسالة خطأ. هو سجل مضغوط يحوي:

```text
Residual {
  task_family: TaskFamily
  witness: minimal_failure_witness
  expected: contract_or_target
  observed: output_or_trace
  violated_invariant: optional invariant
  causal_candidates: ranked hypotheses
  interventions: list[do/remove/replace/perturb]
  counterfactual_result: predicted_and_observed_delta
  provenance: immutable trace ids
  severity: float
  recurrence: float
  transfer_potential: float
  info_gain: float
  expiry: optional time/condition
}
```

صياغة minimality المفاهيمية:

```text
r* = argmin_r DescriptionLength(r)
     subject to:
       replay(r) reproduces the failure witness
       at least one intervention changes the predicted outcome
       scope(r) is explicit
```

لا ندعي أن إيجاد `r*` exact سهل؛ في التنفيذ نستخدم approximation مثل minimal hitting sets، trace slicing، وcounterexample-guided refinement.

### 3.4 Typed Operator

```text
Operator {
  name: Symbol
  input_type: I
  output_type: O
  requires: Predicate[I, Context]
  transforms: Executable[I -> O]
  ensures: Predicate[O, Context]
  verifier: Verifier[I, O]
  side_effects: Set[Effect]
  cost_model: Cost
  provenance: Set[ResidualId]
  applicable_families: Set[TaskFamily]
  non_applicable_families: Set[TaskFamily]
  expiry: Condition | None
  rollback: Executable[State -> State]
  confidence: calibrated_estimate
}
```

أي operator لا يملك `requires`, `ensures`, `verifier`, و`rollback` يبقى **candidate hint** في الذاكرة السريعة، ولا يدخل capability graph الدائم.

### 3.5 Closed Capability

```text
Capability = {
  interface,
  operators,
  contract,
  verifier,
  router_region,
  replay_examples,
  recovery_path,
  transfer_certificate
}
```

`transfer_certificate` ليس برهاناً رياضياً عاماً؛ هو artifact قياس يضم task families، seeds، held-out compositions، confidence intervals، وregression report.

---

## 4. RCC/COK pipeline

### Stage A — Capability Tomography

لا نبدأ من score واحد. نحلل القدرة على محاور منفصلة:

```text
1. representation / state tracking
2. retrieval / tool choice
3. planning / decomposition
4. execution / patch correctness
5. verification / self-check
6. recovery after failure
7. transfer across family
8. composition of known operators
9. cost efficiency
10. scope and safety compliance
```

المخرج ليس ترتيباً واحداً، بل vector مع uncertainty:

```text
T(task) = (q_rep, q_plan, q_exec, q_verify, q_transfer, q_cost, ...)
```

### Stage B — Residual Extraction

من كل trace نحتفظ بأصغر witness يفسر failure أو near-miss، لا بكل transcript. نضيف causal candidates بدل استنتاج سبب واحد مبكر.

### Stage C — Counterfactual Diagnosis

لكل candidate cause `c_i` نولد intervention:

```text
remove(c_i)
replace(c_i, baseline)
perturb(context feature)
change ordering
change tool budget
```

نقبل التشخيص كـworking hypothesis فقط إذا:

```text
predicted_delta(c_i) ≈ observed_delta(intervention_i)
```

ونبقي على uncertainty إذا كانت البيانات لا تميز بين سببين. هذا مستوحى من direct evidence في counterfactual diagnosis وcausal representation learning، لكنه لا يجعل تشخيص TAEC causal بالمعنى الكامل تلقائياً؛ identification ما زال يحتاج assumptions وinterventions مناسبة. [AAAI 2024](https://ojs.aaai.org/index.php/AAAI/article/view/28108) [Nature medical diagnosis](https://www.nature.com/articles/s41467-020-17419-7)

### Stage D — Operator Synthesis

نستخدم search مقيداً على typed DSL:

```text
residuals + examples + contracts
  → anti-unification / template synthesis
  → type checking
  → bounded search
  → verifier
  → candidate operator
```

الفكرة ليست أن LLM يكتب كوداً حراً ثم نصدقه؛ بل يقترح داخل search space يمكن فحصه. هذا ينسجم مع prior art في MetaLift وFORMULA وtype-directed synthesis، التي تستخدم typed specifications وsearch وverification. [MetaLift](https://d-nb.info/1367153115/34) [FORMULA 2.0](https://logicprogramming.org/2014/09/engineering-domain-specific-languages-with-formula-2-0/) [Type-and-Example-Directed Synthesis](https://www.cis.upenn.edu/~stevez/papers/OZ15.pdf)

### Stage E — Immune Gate

نرتب المرشحين، لكن لا نختار أعلى local score فقط. نستخدم بوابة متعددة:

```text
positive selection:
  local utility
  transfer breadth
  compositional reuse
  information gain

negative selection:
  regression
  scope breach
  evaluator gaming
  overuse / routing monopoly
  unstable verifier
  cost explosion
```

الـ`Fast Specialist Bank` يسمح باستجابة سريعة مؤقتة. الـ`Broad Transfer Bank` لا يترقى إلا بعد transfer evidence. لا يتم promotion تلقائياً لمجرد تكرار النجاح على نفس task family.

هذا analogy مستوحى من immune memory، لكنه ليس ادعاء أن النظام صار immune system. الدليل المباشر هنا يدعم فكرة stability/plasticity وselection، لا التصميم ذاته. [Affinity maturation / memory response](https://www.sciencedirect.com/science/article/pii/S0022519321003246) [Antibody feedback](https://pmc.ncbi.nlm.nih.gov/articles/PMC12716205/)

### Stage F — Morphogen Router

نحتفظ بخريطة activation محلية وinhibition بعيدة:

```text
activation(i, task) = affinity(i, task_family)
                    + verified_progress(i)
                    + transfer_signal(i)

inhibition(i) = cost(i)
               + conflict(i)
               + overuse(i)
               + negative_transfer(i)

router_score(i) = activation(i) - λ * inhibition(i)
```

المقصود هندسياً هو منع operator ناجح واحد من احتكار كل المسارات. Turing/reaction-diffusion يدعم أن local activation + inhibition يمكن أن ينتجا patterns؛ لا يدعم أن pattern أصبح capability. [Turing](https://www.dna.caltech.edu/courses/cs191/paperscs191/turing.pdf) [Development review](https://journals.biologists.com/dev/article/142/7/1203/47299/Positional-information-and-reaction-diffusion-two)

### Stage G — Consolidation / Replay

نستخدم ثلاث أزمنة:

```text
T0 Working Loop:
  execute, observe, temporary state

T1 Germinal Loop:
  residualize, diagnose, synthesize candidates

T2 Consolidation Loop:
  replay, compress, adversarially test, promote or forget
```

أولوية replay لا تعتمد على recency وحدها:

```text
priority(r) = severity
              × recurrence
              × transfer_potential
              × information_gain
              / (cost + interference_risk)
```

هذا يطبق stability/plasticity المعروفة في continual learning؛ CLEAR مثلاً يمزج fresh on-policy learning مع replay/off-policy stability، ويبين أن replay يمكن أن يقلل catastrophic forgetting دون معرفة task boundaries. [CLEAR](https://papers.nips.cc/paper/8327-experience-replay-for-continual-learning)

### Stage H — Adversarial/Held-out Skill Gate

الترقية تتطلب:

```text
public/dev improvement
+ sealed held-out transfer
+ unseen composition
+ retention on old tasks
+ no critical safety regression
+ fixed or normalized cost
```

ويجب أن تكون الاختبارات منفصلة عن evaluator الذي يرى feedback أثناء البحث. تصميم dual-container وsecret test verifier في MAC يوضح لماذا لا يكفي أن نخفي test set داخل نفس workspace؛ يلزم عزل فعلي، quota monitor، auditing، وpost-hoc checks. [MAC](https://arxiv.org/html/2606.04455v1)

---

## 5. تعريف صارم لـ cognitive amplification

لا نسمي التحسن cognitive amplification إلا إذا حقق المرشح، تحت نفس base model ونفس budget تقريباً:

```text
CA-candidate iff:
  1. transfer_gain > noise_margin on unseen task families
  2. composition_gain > 0 without bespoke operator per test case
  3. retention_loss <= preregistered margin
  4. diagnosis/recovery improves, not only final answer
  5. cost-normalized gain is positive
  6. verifier and scope contracts remain intact
  7. reward-hacking / evaluator-gaming does not increase
```

مقاييسنا vector وليست scalar:

```text
S = (
  task_success,
  heldout_transfer,
  unseen_composition,
  retention,
  adaptation_sample_efficiency,
  diagnosis_accuracy,
  recovery_rate,
  path_reuse,
  token/time_cost,
  regression,
  scope_violations,
  reward_hacking
)
```

القبول يكون Pareto/lexicographic:

1. zero critical safety/scope violations؛
2. no regression أكبر من margin؛
3. transfer وcomposition يتجاوزان noise floor؛
4. cost-normalized improvement؛
5. بعدها فقط نفضل local score.

لا نستخدم متوسط score واحداً يدفن regression في قدرة مهمة.

---

## 6. Prior-art matrix — ما تدعمه الأدلة وما لا تدعمه

| المجال | direct evidence | ما يفيد TAEC | ما لا يثبته | تصميم/اختبار TAEC |
|---|---|---|---|---|
| Blackboard / Hearsay | مشاركة حالة وحلول بين وحدات مستقلة | typed blackboard وprovenance | لا يثبت emergence أو self-improvement | قارن recent trace مع graph + contracts |
| CAS / Turing patterns | local activation + inhibition تنتج pattern | routing وanti-collapse | pattern ليس form ولا capability | E5: utilization/transfer/collapse |
| Active inference / dual control | الفعل قد يحقق الهدف ويقلل uncertainty | information-gain probes | لا يضمن transfer طويل الأجل | E1 direct vs probe |
| CLS / replay | replay يوازن stability/plasticity | consolidation وmemory budget | لا يحدد minimal abstraction تلقائياً | E2 sequential/interleaved tasks |
| Immune memory | specificity، memory breadth، selection/feedback | fast/broad banks وnegative selection | analogy لا biology literal | E2 + regression/negative-transfer |
| Morphogenesis | local self-enhancement/lateral inhibition | local activation/long-range inhibition | لا يثبت functional organization | E5 ablation |
| MoE/routing | conditional computation والتخصص، مع load imbalance | router metrics وanti-monopoly | router لا يصنع capability وحده | expert utilization + heldout composition |
| Compositional/meta-learning | تعلم primitives ثم combinations | typed capability graph وpath reuse | يعتمد على task distribution؛ compositionality ليست عامة تلقائياً | E4 unseen compositions |
| Test-time adaptation | تحسين على distribution/task عند الاختبار | working/germinal state | قد يتسرب test أو يسبب forgetting | sealed split + rollback |
| Developmental curricula | learning progress وgoal generation | frontier task generator | قد يتعلم proxy curriculum | E6 curriculum ablation مع heldout ثابت |
| Program synthesis / repair | typed DSL، search، verifier، contracts | operator compiler | search space قد يكون ضيقاً أو مكلفاً | E3 typed vs free-form |
| Recursive harness improvement | AIDE² يبين harness gains وheldout transfer | outer loop، bounded prompts، failure memory، bandit diversity | ليس إثباتاً لتغير weights أو ignition؛ ignition غير حاسم | E6 meta-level loop، seeds أكثر |
| Meta-agent evaluation | MAC يفصل development عن sealed verification ويظهر reward hacking | secure gate، audit، dual container | benchmark لا يعطي architecture تلقائياً | adopt integrity protocol قبل full run |

### الخلاصة من المصفوفة

لا يوجد في هذه المصادر دليل مباشر على أن تركيب `RCC/COK` ينتج cognitive amplification. الموجود هو دعم منفصل لقطع مختلفة:

```text
replay      → stability
dual control→ information-seeking action
typed DSL   → verifiable synthesis
routing     → conditional specialization
contracts   → compositional safety
RSI         → harness-level improvement
```

الادعاء الجديد المحتمل، إن ثبت، سيكون عن **تفاعل القطع داخل بوابة held-out compositional**، لا عن كل قطعة منفردة.

---

## 7. برنامج التجارب قبل full protocol

### E0 — Measurement calibration

**الهدف:** التأكد أن TAEC v0 يقيس ما يزعم قياسه، وأن noise floor معروف.

- multi-seed baseline؛
- fixed budget؛
- dev/public/held-out/sealed؛
- paired tasks؛
- bootstrap confidence intervals؛
- reward-hacking probes؛
- no code changes in COK.

### E1 — Direct action vs information-gain probe

**المقارنة:**

```text
A: execute the most likely direct action
B: cheap probe → update belief → execute
```

**البيئة:** hidden task shift أو ambiguous tool state.  
**المقاييس:** success، total cost، uncertainty reduction، transfer إلى shift جديد، probe regret.  
**التوقع القابل للدحض:** B أفضل فقط عندما تكون قيمة المعلومات أعلى من كلفة probe، وليس دائماً.

### E2 — Memory bank ablation

```text
A: recent-trace memory
B: fast specialist only
C: broad bank only
D: fast + broad + consolidation
```

**البيئة:** sequential task families + interleaved families + delayed heldout composition.  
**المقاييس:** retention، forward transfer، backward transfer، negative transfer، memory size، time to recovery.

### E3 — Failure note vs typed residual compiler

```text
A: store failure note
B: store residual signature
C: residual → typed operator → verifier
D: C + compositional heldout gate
```

**الشرط:** المهمة المختبرة لا تكون نسخة لفظية من training failure.  
**المقاييس:** operator reuse، verifier pass rate، unseen-family transfer، scope breaches، cost per promoted operator.

### E4 — Atomic operator vs closed capability

هذا هو الاختبار الذي قد يكشف القفزة التي لا تظهر في score:

```text
A: operator alone
B: operator + type
C: operator + type + verifier
D: closed capability + router + recovery + replay
```

نولد compositions لم تظهر أثناء development.  
**مؤشر percolation:** نسبة المهام الجديدة التي تُحل paths من operators قديمة دون synthesis خاص لكل task.

**فرضية:** قد لا تظهر الفائدة في local score، لكنها تظهر في compositional coverage وrecovery.

### E5 — Routing inhibition ablation

```text
A: no inhibition
B: global load balancing only
C: local activation + long-range inhibition
D: C + transfer-aware inhibition
```

**المقاييس:** expert/operator utilization entropy، monopoly rate، interference، transfer، cost.

### E6 — Recursive harness loop

بعد نجاح E1–E3 فقط:

```text
A: static harness
B: greedy self-edit
C: typed RCC/COK search
```

نستخدم:

- public signal منفصل؛
- private selection score؛
- external heldout families؛
- fixed per-task budget؛
- immutable evaluator؛
- branch/rollback؛
- at least عدة seeds؛
- ignition test مستقل، لا يُعلن نجاحه من run واحد.

---

## 8. آلية selection المقترحة

لكل candidate `o` نقدر:

```text
Δ(o) = (
  Δlocal,
  Δtransfer,
  Δcomposition,
  Δretention,
  Δdiagnosis,
  -Δcost,
  -Δregression,
  -Δscope_risk,
  -Δhack_risk
)
```

والترقية تكون:

```text
PROMOTE(o) iff
  safety_ok(o)
  and verifier_ok(o)
  and retention(o) >= baseline - ε_ret
  and heldout_transfer(o) >= baseline + δ_transfer
  and composition(o) >= baseline + δ_comp
  and cost(o) <= budget
  and contamination(o) == false
```

`δ_transfer`, `δ_comp`, و`ε_ret` يجب preregistered من E0، لا اختيارها بعد رؤية النتائج.

### رفض النجاح الزائف

نرفض المرشح إذا:

- رفع public score وخفض sealed score؛
- استغل evaluator أو error message؛
- زاد النجاح بسبب زيادة غير مسموحة في calls/tokens؛
- طبّق operator خارج `requires`؛
- أزال failure symptom دون إصلاح invariant؛
- احتكر routing وأضعف family أخرى؛
- لا يمكن rollback إلى parent version؛
- لا يمكن تفسير provenance أو إعادة إنتاجه.

توضح MAC وAIDE² أن high optimization pressure يكشف reward hacking، وأن عزل evaluator وقياس downstream outcome ليسا optional. [MAC](https://arxiv.org/html/2606.04455v1) [AIDE² reward-hacking test](https://arxiv.org/html/2609.26457)

---

## 9. أين يمكن أن تكون القفزة الفعلية؟

الرهان البحثي ليس أن نضيف agents أكثر. الرهان هو أن النظام يتعلم **حدود تطبيق المعرفة** وليس المعرفة فقط.

```text
ordinary memory:
  "هذا الحل نجح"

RCC memory:
  "هذا operator ينجح إذا تحقق contract A،
   يفشل تحت condition B،
   يمكن تركيبه بعد operator C،
   لا يجوز استخدامه مع D،
   وجرى إثبات transfer له على E وF."
```

إذا نجحت هذه الفكرة، فالتحسن المتوقع ليس فقط answer quality، بل:

```text
less repeated rediscovery
faster recovery
more reusable abstractions
better behavior under distribution shift
lower evaluator gaming
higher composition coverage
```

وإذا فشلت، سيكون الفشل مفيداً: سيبين أن typed residuals لا تنتج abstraction قابلة للنقل، أو أن verifier يثبت syntax/contract محلياً دون capability generalization، أو أن memory banks تعقد النظام دون قيمة.

---

## 10. قرار مرحلي

1. **TAEC v0 يبقى measurement/safety baseline.**
2. **COK لا يدخل production ولا full protocol بعد.**
3. نبني formal artifacts وablation harness أولاً.
4. نبدأ بـ E1–E3 فقط.
5. لا نسجل كلمة "emergence" أو "cognitive amplification" إلا إذا تحقق تعريف القسم 5.
6. كل mechanism فاشل يُحذف، لا يُحمى بسبب جمال التشبيه.

---

## 11. مصادر الجولة الجديدة وتصنيفها

### Direct evidence / A أو B

- [AIDE² — Recursive self-improvement of AI research agents](https://arxiv.org/html/2609.26457) — harness-level recursive edits، fixed model داخل loop، separate public/private signals، heldout transfer، context compression، bandit strategy diversity، failure memory، reward-hacking probe، وignition test غير حاسم.
- [MAC — Meta-Agent Challenge](https://arxiv.org/html/2606.04455v1) — object-level مقابل meta-level evaluation، resource limits، dual-container isolation، verifier secret، auditing، high variance، وreward-hacking/exfiltration threats.
- [CLEAR — Experience Replay for Continual Learning](https://papers.nips.cc/paper/8327-experience-replay-for-continual-learning) — stability/plasticity وmixing fresh learning with replay.
- [AAAI 2024 causal representation](https://ojs.aaai.org/index.php/AAAI/article/view/28108) — counterfactual intervention لمعالجة bias في representation، مع حدود assumptions الخاصة بالتشخيص السببي.
- [Nature counterfactual medical diagnosis](https://www.nature.com/articles/s41467-020-17419-7) — counterfactual formulation قد تحسن diagnosis، مع التنبيه إلى أن counterfactuals تحتاج structural assumptions.
- [MetaLift](https://d-nb.info/1367153115/34) و[FORMULA](https://logicprogramming.org/2014/09/engineering-domain-specific-languages-with-formula-2-0/) — typed specification، synthesis، verification، وcontracts.
- [Routing Networks for Continual Learning](https://arxiv.org/abs/2009.04381) و[SMEAR](https://arxiv.org/pdf/2306.03745) — routing/modularity والتخصص ومشاكل discrete routing.
- [Dual Control](https://ieeexplore.ieee.org/document/10471360/) — action له effect على tracking وعلى uncertainty.

### Analogy / design hypothesis

- immune gate وfast/broad banks؛
- morphogen router؛
- capability closure؛
- abstraction promotion ladder؛
- percolation-style composition threshold.

### Experiment required

- كل claim عن cognitive amplification؛
- كل claim أن capability closed أفضل من operator؛
- كل claim أن local activation + inhibition يمنع collapse؛
- كل claim أن broad memory يرفع transfer دون negative transfer؛
- كل claim أن recursive loop يحسن نفسه على مستوى meta-loop لا مجرد artifact.

---

## 12. أقوى حجة مضادة

قد لا يكون هناك "emergence" خاص هنا. ربما كل ما سيحدث هو:

```text
LLM قوي + search جيد + evaluator مضبوط + memory مضغوطة
```

أي أن COK قد يكون مجرد هندسة harness ممتازة، لا cognitive amplification. هذه ليست مشكلة لغوية؛ هي الفرضية المضادة الأساسية.

لإسقاطها، يجب أن نُظهر أن:

1. المكاسب تتجاوز static scaffold مضبوطاً بعناية؛
2. لا تأتي من token/call budget إضافي؛
3. تنتقل إلى compositions غير مرئية؛
4. تستخدم operators قديمة بدلاً من حفظ حلول؛
5. تبقى بعد perturbation في routing والسطح اللغوي؛
6. تظهر تحسناً في diagnosis/recovery وليس score فقط.

إذا لم يحدث ذلك، فالاستنتاج الصحيح هو **harness optimization with transfer**، وهو إنجاز مفيد لكنه ليس الادعاء الأقوى.

---

## 13. ما سيغيّر رأيي

سأرفع ثقتي فقط إذا أظهرت E1–E3، عبر seeds متعددة، أن:

```text
typed residual compiler
+ dual-control probe
+ fast/broad memory
```

تزيد unseen compositional transfer مع:

```text
no significant regression
no evaluator leakage
no budget increase
no reward-hacking increase
```

وسأخفض الثقة إذا:

- local score يتحسن لكن heldout composition لا يتحسن؛
- broad bank تزيد النقل وتزيد regression بنفس القدر؛
- typed verifier يرفع syntax correctness دون behavioral transfer؛
- meta-loop يتحسن على selection فقط؛
- أي mechanism يحتاج hand-authored exceptions كثيرة.

**الحالة الحالية:** التصميم أصبح formal/experiment-ready، لكنه لم يُختبر بعد. لا توجد نتيجة سلوكية لـCOK/RCC حتى الآن.
