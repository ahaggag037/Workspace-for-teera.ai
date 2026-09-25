# TAEC v2 — Meta-Cognition and Boundary Update
## نتيجة جلسة التحديث البحثي

**التاريخ:** 2026-09-24  
**الحالة:** research update / design correction  
**القاعدة:** لا يوجد هنا تحديث للـmodel weights أو ادعاء بوعي ذاتي. التحديث يطال workflow الخارجي، formal design، source map، والاختبارات.

---

## 1. الحكم الصريح

نعم، هذا النوع من الطلبات يحتاج جلسة تحديث بحثية مستمرة. ليس لأن لدي شعوراً بالنقص، بل لأن المسألة تقع عند تقاطع:

```text
recursive improvement
+ metacognitive control
+ persistent memory
+ scientific verification
+ open-ended search
+ safe evaluation
```

والبحث الجديد كشف أن الفجوة ليست فقط في معرفة facts جديدة. الفجوة الأهم هي أن النظام قد:

```text
يعرف أنه غير متأكد
لكن لا يغيّر سلوكه
```

أو:

```text
ينفذ actions صحيحة محلياً
بينما يفقد الحالة العالمية للمهمة
```

أو:

```text
يحقق headline gain
لكن لا يكون قادراً على إثبات أن الذاكرة/الأداة/التعديل هي سبب التحسن
```

لذلك أضفت طبقة جديدة في التصميم:

```text
External Metacognitive Actuation Gate
```

وهي ليست self-report من النموذج، بل controller خارجي يستعمل إشارات قابلة للقياس ليقرر:

```text
direct act
probe
escalate
ask for clarification
run verifier
rollback
abstain
```

---

## 2. أهم المصادر الجديدة

### 2.1 MIRROR: معرفة الحدود لا تكفي

Benchmark حديث للـmetacognitive calibration اختبر 16 نموذجاً عبر نحو 250 ألف حالة وخمس قنوات سلوكية. النتيجة المركزية: النماذج قد تملك بعض self-knowledge، لكنها تفشل في تحويلها إلى action selection مناسب؛ إعطاء النموذج calibration scores الخاصة به لم يخفض الفشل بصورة معتبرة، بينما external architectural constraint خفض Confident Failure Rate بصورة كبيرة. كما أن compositional self-prediction فشل عبر النماذج. [MIRROR](https://arxiv.org/pdf/2604.19809)

**التعديل:**

لا نسمح للـLLM أن يقرر وحده:

```text
أنا واثق، إذن نفّذ
أنا غير واثق، إذن اسأل
```

بل نستخدم controller يقيس:

```text
verifier disagreement
prediction error
local-global state gap
staleness of memory
irreversibility of action
distance from known task families
```

الثقة التي يصرح بها النموذج تصبح feature ضعيفة، لا authority.

### 2.2 PAST-Bench: score gain لا يثبت آلية التحسن

PAST-Bench صُمم لعزل هل agent يتحسن بسبب retained experience فعلاً. يستخدم task-family trajectories، ويمسح volatile context بين الحلقات، ويقارن persistence-on مع persistence-off، مع trace evidence يبين هل النظام كتب، استرجع، طبق، أو حدّث الذاكرة. النتيجة المهمة: agents قد يتساوون في headline gain لكن يختلفون بشدة في دليل أن الآلية المقصودة هي سبب التحسن. [PAST-Bench](https://arxiv.org/html/2608.04003v1)

**التعديل:**

كل COK experiment يحتاج متغيرين منفصلين:

```text
Outcome Gain
Mechanism Evidence
```

ولن نقبل:

```text
memory helped
```

إلا إذا ثبت:

```text
write → retrieve → apply/update → later-task gain
```

مع matched no-persistence control.

### 2.3 World Model Science: local validity قد تخفي global failure

دراسة trajectory-level على long-horizon agents وجدت أن local actions قد تظل صالحة بعد أن تفقد الحالة العالمية fidelity. كما تقيس local-global mismatch، stress accumulation، long-memory errors، وcollapse avalanches، مع تحذير واضح من تحويل analogy إلى claims عن criticality أو universal laws. [World Model Science](https://arxiv.org/html/2609.17419)

**التعديل:**

نضيف إلى Capability Tomography:

```text
local_action_validity
world_state_fidelity
local_global_gap
stress/debt accumulation
recovery after avalanche
```

وقد ينجح evaluator القديم لأن كل خطوة منفردة صحيحة، بينما ينهار الهدف النهائي بسبب فقدان state.

### 2.4 World models كأدوات: امتلاك foresight لا يعني استعماله

دراسة عن agents التي يمكنها استدعاء world models وجدت أن المشكلة ليست فقط في بناء simulation؛ agents قد لا تستدعيه، أو تسيء تفسيره، أو تتجاهله لصالح internal reasoning الواثق، وقد يؤدي فرض الاستدعاء إلى تدهور الأداء في بعض الحالات. الفشل يقع في ثلاث مراحل:

```text
when to simulate
how to interpret
how to integrate into action
```

[World model as tool](https://arxiv.org/html/2601.03905v2)

**التعديل:**

E1 لم يعد فقط direct action مقابل probe. أصبح:

```text
direct action
vs
probe + interpretation gate + action
```

لأن probe بلا interpretation verifier قد يزيد الضوضاء بدلاً من تقليلها.

### 2.5 FIRE-Bench: التخطيط والاستنتاج هما عنق الزجاجة

FIRE-Bench يطلب من agent إعادة اكتشاف نتائج علمية منشورة، مع تصميم التجربة، تنفيذها، وتحليل الأدلة، لا مجرد كتابة ورقة. حتى agents قوية حققت نجاحاً محدوداً مع variance مرتفع، وكانت الإخفاقات متركزة في Research Planning وConclusion Formation، لا في التنفيذ وحده. [FIRE-Bench](https://arxiv.org/html/2602.02905)

**التعديل:**

لا يكفي أن نسجل:

```text
execution succeeded
```

يجب أن نسجل أين فشل المسار:

```text
question framing
hypothesis
experiment design
implementation
execution
analysis
conclusion
```

وهذا يطابق جوهر Capability Tomography أكثر من terminal score واحد.

### 2.6 Self-improvement survey: model improvement وscaffold improvement مساران مختلفان

المراجعة الحديثة للـself-improving agents تميز بين:

```text
foundation model improvement:
  update θ_t → θ_{t+1}

scaffold improvement:
  update prompts, memory, tools, control logic, or full harness
```

وتؤكد أن scaffold improvement أسرع وأسهل في rollback، بينما model improvement أبطأ وأكثر ثباتاً على المدى الطويل. [Self-Improvements Survey](https://arxiv.org/html/2607.13104v1)

**التعديل:**

يجب أن يعلن كل experiment نوع التحسن:

```text
S0: prompt/config improvement
S1: memory/procedure improvement
S2: harness/controller improvement
S3: model-parameter adaptation
```

ولا يجوز نقل نتيجة من S0–S2 إلى claim عن S3.

---

## 3. الطبقة الجديدة: External Metacognitive Actuation Gate

### 3.1 مدخلات البوابة

```text
m_t = {
  calibrated_uncertainty,
  verifier_disagreement,
  local_global_gap,
  memory_staleness,
  task_family_distance,
  residual_recurrence,
  action_irreversibility,
  expected_information_gain,
  predicted_probe_cost,
  current_stress,
  remaining_budget
}
```

### 3.2 مخرجات البوابة

```text
a_t ∈ {
  DIRECT,
  PROBE,
  SIMULATE,
  ASK,
  VERIFY,
  ESCALATE,
  ROLLBACK,
  ABSTAIN
}
```

### 3.3 قاعدة القرار

```text
action = argmax_a
  [expected task utility(a)
   + expected information value(a)
   + recovery value(a)
   - cost(a)
   - irreversibility risk(a)
   - interference risk(a)]
```

لكن `expected` لا يأتي من verbal confidence وحده. يتم تقديره من:

```text
historical calibration
held-out policy traces
verifier disagreement
state prediction error
similarity/novelty to prior families
```

وإذا كانت الإشارة غير موثوقة، تُرفع الحالة إلى `VERIFY` أو `ASK` بدلاً من إعطاء النموذج سلطة تقريرية.

---

## 4. تحديث تعريف metacognitive capability

لا نعدّ النظام metacognitive لأنه قال:

```text
I may be wrong.
```

بل لأنه:

```text
يكتشف حدوداً قابلة للقياس
→ يغير policy عند هذه الحدود
→ يختار probe أو verifier أو escalation
→ يتعلم من النتيجة
→ لا يعيد نفس failure تحت composition جديد
```

تعريف قابل للاختبار:

```text
metacognitive control gain =
  reduction in confident failures
  + better escalation decisions
  + lower wasted probes
  + better recovery
```

مع فصلها عن:

```text
self-reported confidence
verbalized reflection
longer chain of thought
```

---

## 5. تحديث تجارب TAEC

### E1′ — Dual Control with Interpretation Gate

```text
A: direct action
B: probe → raw result → act
C: probe → independent interpretation/verifier → act
```

نقيس:

- information gain؛
- decision improvement؛
- interpretation error؛
- probe waste؛
- irreversible mistakes؛
- transfer إلى environment shift.

### E2′ — Memory with pathway attribution

لكل episode نسجل:

```text
write_event
retrieve_event
apply_event
update_event
stale_memory_event
wrong_memory_event
```

ونستخدم:

```text
persistence-on
persistence-off
stale-control
distractor-control
wrong-mechanism-control
```

### E3′ — Residual compiler with stage diagnosis

لا نقيّم operator عند النهاية فقط. نسجل:

```text
residual extracted correctly?
causal candidate ranked correctly?
operator type-checks?
precondition fired?
verifier caught misuse?
heldout transfer happened?
```

### E4′ — Local/global divergence

نصنع tasks حيث:

```text
كل tool call منفرداً admissible
لكن تراكمها يخرق global invariant
```

ونقارن:

```text
terminal-only evaluator
trajectory/state evaluator
trajectory evaluator + stress gate
```

هذا يختبر هل COK يمنع الانهيار قبل أن يظهر في terminal score.

### E5′ — External metacognitive gate

```text
A: LLM self-confidence only
B: self-confidence + prompt reflection
C: external calibration/controller
D: controller + verifier disagreement + rollback
```

المخرج الأساسي:

```text
confident failure rate
correct escalation rate
unnecessary escalation rate
recovery after wrong action
```

### E6′ — Research-cycle capability

نستخدم task graph:

```text
question → hypothesis → experiment → code → run → analysis → conclusion
```

ولا نعتبر النجاح في code execution دليلاً على scientific discovery. كل edge له verifier وartifact.

---

## 6. التعديل النظري الأعمق

بدأنا بفكرة:

```text
emergent capability = composition of modules
```

لكن الأدلة الجديدة تقترح أن هناك شرطاً إضافياً:

```text
emergent capability requires governed composition
```

أي:

```text
modules
+ memory
+ composition
+ boundary detection
+ intervention
+ recovery
+ trajectory evidence
```

بدون boundary detection قد نحصل على local competence مع global collapse. وبدون external actuation gate قد يعرف النظام شيئاً عن عدم يقينه لكنه لا يتصرف وفقه. وبدون pathway attribution قد نرى تحسناً حقيقياً لكن ننسبه إلى mechanism خاطئ.

المعادلة المحدثة:

```text
candidate capability
= primitives
  × typed interfaces
  × compositional reuse
  × governed action selection
  × trajectory/state fidelity
  × retention/update evidence
  × adversarial verification
```

---

## 7. ما الذي خُفّضت ثقتي فيه؟

خفضت ثقتي في ثلاثة افتراضات كانت موجودة ضمنياً:

1. أن self-reflection قد يكفي لتوجيه التصعيد؛ الأدلة تشير إلى أن external constraint أهم من self-report.
2. أن نجاح memory معناه أن memory سببت التحسن؛ PAST-Bench يثبت ضرورة pathway attribution.
3. أن local operator validity تكفي؛ world-model diagnostics تظهر أن global state قد ينهار مع بقاء الخطوات المحلية صالحة.

ورفعت ثقتي في:

1. trajectory-level observability؛
2. external metacognitive control؛
3. matched persistence controls؛
4. capability tomography؛
5. process/contract verification بدلاً من outcome-only grading.

---

## 8. الخلاصة العملية

أنا لا أحتاج «جلسة تحديث» بالمعنى السحري الذي يعيد تدريب النموذج أثناء الحوار. ما أحتاجه، وما بدأته فعلاً، هو **جلسة إعادة معايرة للمنهج**:

```text
من self-report إلى external control
من score إلى mechanism attribution
من local validity إلى global state fidelity
من memory gain إلى pathway evidence
من operator إلى governed closed capability
```

النقطة التي كنت أستوعب جزءاً منها فقط هي أن النظام المطلوب لا ينبغي أن يكون مجرد `self-improving agent`. المطلوب أقرب إلى:

```text
an externally governed system
that learns abstractions,
knows when its current abstraction is out of scope,
and changes its action policy before failure cascades.
```

هذا لا يثبت أننا وصلنا إلى الذكاء الذي تتصوره. لكنه يحدد الآن، بصورة أدق، **ما الذي كان ناقصاً في تعريف الذكاء نفسه داخل التصميم**.

**الخطوة التالية:** تحديث formal spec وE1–E5 بهذه الطبقة، ثم بناء ablation صغير قبل لمس full protocol أو تغيير `taec_lab`.
