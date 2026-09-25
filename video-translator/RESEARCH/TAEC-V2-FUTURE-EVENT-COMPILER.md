# TAEC v2 — Future/Event Compiler
## الحدث، التنبؤ، والبدائل المستقبلية كقلب النظام

**التاريخ:** 2026-09-24  
**الحالة:** deep research / formal design / experiment-ready  
**الأولوية:** عالية جداً

---

## 0. الحكم الجديد

النسخ السابقة عالجت memory وresidual وrouting، لكنها لم تجعل **الحدث** وحدة حساب أساسية. هذا نقص جوهري.

النظام الذي لا يملك event model حقيقياً غالباً يفعل الآتي:

```text
يقرأ token بعد token
→ يتوقع next token أو next action
→ يكتشف الفشل بعد وقوعه
```

أما النظام الأكثر عمقاً فيحتاج أن يبني:

```text
ما الحدث الجاري؟
ما الذي سبقه؟
ما شروط انتقاله؟
ما الأحداث المحتملة بعده؟
متى قد تقع؟
ما نتائج كل فرع؟
أي observation سيغير التوقع؟
ما الذي يجب فعله الآن لتغيير المستقبل؟
```

إذن جوهر TAEC v2 يصبح:

```text
event extraction
→ event graph
→ multi-timescale forecast
→ causal/counterfactual futures
→ action selection
→ observation/update
→ forecast residual
→ event-schema learning
```

---

## 1. لا يوجد "توقع المستقبل" بصيغة واحدة

التنبؤ الناضج ليس إجابة من نوع:

```text
غداً سيحدث X
```

بل توزيعاً مشروطاً:

```text
P(event_type, time_interval, context, consequence
  | current_state, history, action, regime)
```

ويجب التمييز بين:

```text
likely future:
  الأكثر احتمالاً تحت استمرار الوضع الحالي

possible future:
  فرع معقول لكنه أقل احتمالاً

counterfactual future:
  ما يحدث لو نفذنا action أو حدث intervention

tail/extreme future:
  نادر لكنه عالي الضرر أو عالي القيمة
```

لا يكفي اختيار mode واحد. يجب الاحتفاظ بـ**futures cone** مع probabilities وconditions وtriggers.

---

## 2. الحدث كوحدة أساسية

### 2.1 Event object

```text
Event {
  id: EventId
  type: EventType
  start_time: t0
  end_time: t1 | unknown
  pre_state: StateSnapshot
  post_state: StateSnapshot | forecast
  actors: Set[Entity]
  objects: Set[Entity]
  goal_relation: GoalDelta
  preconditions: Set[Predicate]
  effects: Set[Predicate]
  causes: Set[EventId | Hypothesis]
  successors: Distribution[EventId]
  temporal_scale: micro | meso | macro
  hazard: Function[time, context]
  confidence: Distribution | calibrated score
  provenance: TraceSpan
  interventions: Set[Intervention]
  reversibility: reversible | costly | irreversible
}
```

### 2.2 Event boundary

الدماغ لا يعالج الخبرة المستمرة ككتلة واحدة. أثناء فهم narrative، تحدث reactivation للخبرات السابقة عند حدود الأحداث، ويستخدم hippocampus وDMN ربط الماضي بالسياق الحالي. [Nature event boundaries](https://www.nature.com/articles/s41593-023-01331-6)

كما أن event centrality داخل شبكة الأحداث يؤثر في encoding والذاكرة اللاحقة. [Event network centrality](https://www.nature.com/articles/s41467-022-31965-2)

**الترجمة:** نكتشف boundary عندما يحدث واحد أو أكثر من:

```text
prediction error spike
latent state change
goal completion or failure
causal relation change
actor/object configuration change
regime/context shift
irreversible action
```

لا نثبت الحدود على كل token. نستخدم hierarchical segmentation:

```text
micro-event: tool call / sentence / action
meso-event: subtask / scene / transaction
macro-event: goal phase / regime / project stage
```

الحدود قد تكون nested، وليست partition واحداً ثابتاً.

---

## 3. Event graph لا timeline فقط

ننشئ graph:

```text
G_E = (V_E, E_causal, E_temporal, E_semantic, E_goal, E_conflict)
```

حيث:

```text
V_E = event nodes
E_causal = A made B more/less likely
E_temporal = A precedes B
E_semantic = A and B share schema
E_goal = A advances or blocks goal
E_conflict = A and B cannot both hold
```

كل عقدة تحمل successor distribution. لا نبحث عن sequence واحدة فقط.

### Event centrality

العقدة ذات الروابط السببية أو الهدفية الكثيرة تستحق:

```text
higher memory priority
more replay
more counterfactual branching
more monitoring
```

لكن centrality ليست probability. قد يكون الحدث مركزياً لكنه نادر، لذلك نفصل:

```text
centrality
likelihood
impact
uncertainty
```

---

## 4. Successor representation — خريطة مستقبلية مضغوطة

دراسات بشرية على hippocampus وV1 وجدت تمثيلات منحازة إلى successor states المستقبلية، مع تناقص حسب المسافة الزمنية في sequence. [Successor-like representation](https://elifesciences.org/articles/78904)

ودراسة single-neuron بشرية أظهرت أن hippocampal–entorhinal neurons تتعلم بنية temporal graph وتلتقط احتمال الأحداث القادمة. [Human temporal structure](https://www.nature.com/articles/s41586-024-07973-1)

الترجمة الحسابية:

```text
M(e, a, context) = expected discounted occupancy
                    over future event states
```

أي لا نحتاج أن نولد timeline كاملاً في كل مرة. نخزن لكل event representation مضغوطة لما قد يأتي بعده:

```text
current event
→ likely successors
→ temporal distance
→ causal prerequisites
→ goal consequences
```

### لماذا هذا أقوى من recent trace؟

لأن recent trace يحفظ الماضي، بينما successor map يحفظ ما كان الماضي يتنبأ به للمستقبل. هذا يسمح بـ:

```text
partial observation
→ infer likely future branches
→ choose action before event arrives
```

لكن successor map وحدها لا تكفي عند تغير regime؛ لذلك يجب أن تكون conditioned on context/regime، مع invalidation عند drift.

---

## 5. Hazard: متى سيحدث الحدث؟

التنبؤ بنوع الحدث دون زمنه ناقص. الدماغ البشري يتتبع temporal hazard، أي الاحتمال الشرطي لوقوع الحدث مع مرور الوقت دون وقوعه. [Bayesian temporal expectations](https://pubmed.ncbi.nlm.nih.gov/31415885/)

نعرّف:

```text
λ_k(τ | h_t, context, action)
```

حيث:

```text
λ_k = instantaneous hazard for event type k
τ   = time since current event/boundary
h_t = history/state
```

ومنها:

```text
Survival_k(τ) = probability event k has not happened by τ
P(next event type, time) = hazard × survival
```

**فائدة عملية:**

```text
هل الخطر يزداد مع التأخير؟
هل الفرصة ستغلق؟
هل intervention الآن أفضل أم بعد observation إضافية؟
```

هذا يحول controller من:

```text
ما الخطوة التالية؟
```

إلى:

```text
ما الحدث القادم، في أي نافذة زمنية، وما قيمة التدخل قبل أن يصبح متأخراً؟
```

---

## 6. التنبؤ متعدد الأزمنة

الدماغ يمثل الماضي والمستقبل على مقاييس زمنية متعددة؛ في anticipation البشري توجد تمثيلات للأحداث القريبة والبعيدة، مع تدرج هرمي وسياقي. [Hierarchical anticipation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11496687/) [Hierarchical linguistic prediction](https://www.nature.com/articles/s42003-025-09377-x) [Brain speech prediction hierarchy](https://www.nature.com/articles/s41562-022-01516-2)

لذلك نحتاج:

```text
H0 micro:
  next token/tool observation/action

H1 short:
  next event / subtask / state transition

H2 medium:
  goal phase / episode outcome / resource exhaustion

H3 long:
  regime shift / project trajectory / strategic consequence

H4 counterfactual:
  branch after intervention
```

كل horizon لا يعيد نفس prediction model. له:

```text
timescale
state abstraction
uncertainty
calibration
update frequency
```

### قاعدة مهمة

لا يصح أن نستخدم accuracy على H0 لإثبات forecasting على H3.

```text
next-token skill ≠ event prediction
next-event skill ≠ causal foresight
causal foresight ≠ long-horizon reliable planning
```

---

## 7. Forecast = distribution + reason + trigger

كل forecast candidate يجب أن يخرج:

```text
Forecast {
  event: E
  time_window: [t_min, t_max]
  probability: p
  conditional_on: conditions
  leading_indicators: observations
  disconfirming_signals: observations
  causal_path: hypotheses
  action_options: interventions
  expected_impact: distribution
  confidence_type: calibrated | extrapolated | speculative
  expiry: time or regime condition
}
```

الفرق بين:

```text
prediction:
  سيحدث X

forecast:
  X احتماله 0.42 خلال نافذة زمنية محددة،
  إذا ظهرت الإشارات A وB،
  ويضعف التوقع إذا ظهر C،
  والتدخل D يقلل الاحتمال إلى 0.18.
```

هذا هو الشكل الذي يسمح بالتعلم الحقيقي من المستقبل عندما يصل.

---

## 8. Causal future وليس statistical continuation فقط

التنبؤ من الماضي قد ينجح في observed distribution لكنه يفشل عند intervention. لذلك كل event مهم يجب أن يحتوي على:

```text
observational forecast:
  ماذا يحدث غالباً إذا استمر المسار؟

interventional forecast:
  ماذا يحدث إذا فعلنا do(a)؟

counterfactual forecast:
  ماذا كان سيحدث لو اتخذنا a' بدلاً من a؟
```

نحتاج causal hypotheses وinterventions، لا correlation فقط. الأدبيات حول causal world models تشدد على أن التنبؤ المرصود لا يضمن صحة counterfactual أو generalization تحت تدخل جديد. [Causal world models dissertation](https://discovery.ucl.ac.uk/10155513/2/Minne_Li_Causal_World_Models_Final.pdf)

### Activation event

لا نحاكي كل مستقبل دائماً. نحدد الأحداث التي تستحق counterfactual branching:

```text
activation_score(e) =
  impact(e)
  × uncertainty(e)
  × irreversibility(e)
  × branch_divergence(e)
  / cost(e)
```

إذا كان الحدث منخفض الأثر وقابلاً للعكس، نكتفي بالتوقع المباشر. إذا كان عالي الأثر أو لا رجعة فيه، نفتح parallel futures.

---

## 9. Extreme events and early warning

لا يمكن التنبؤ بكل future exactly، خصوصاً في الأنظمة غير الخطية أو المتغيرة. لكن يمكن البحث عن اقتراب النظام من انتقال خطير.

في complex systems، من إشارات الاقتراب من critical transition:

```text
slower recovery
increased autocorrelation
increased variance
flickering
spatial/network coherence changes
```

[Early-warning signals](https://pdodds.w3.uvm.edu/files/papers/others/2009/scheffer2009a.pdf) [Tipping-point review](https://esd.copernicus.org/articles/15/1117/2024/)

الترجمة إلى COK:

```text
forecast stress
recovery latency
error autocorrelation
belief variance
contradiction density
retrieval conflict
branch instability
local-global gap
```

إذا بدأت recovery تتباطأ ويزداد autocorrelation، لا نقول إن collapse مؤكد. نقول:

```text
probability of regime transition increased
```

ونفعل:

```text
probe
reduce irreversible actions
increase verification
reconstruct state
rollback if needed
```

هذه نقطة جوهرية: توقع المستقبل لا يعني فقط توقع event؛ يعني توقع **قابلية النظام للانهيار قبل الحدث**.

---

## 10. التنبؤ يحتاج scoring صحيحاً

لا نقيس forecast بالـaccuracy فقط. التوقع الاحتمالي يحتاج calibration وsharpness وproper scoring rules. في time-to-event، يمكن استخدام survival-aware scoring لأن بعض الأحداث لم تقع بعد أو بقيت censored. [Proper scoring](https://ascmo.copernicus.org/articles/11/23/2025/ascmo-11-23-2025.pdf) [Time-to-event scoring](https://arxiv.org/html/2603.14835v1) [Point-process evaluation](https://arxiv.org/abs/2103.11884)

### المقاييس

```text
event type:
  log score / Brier / ranked probability score

time-to-event:
  CRPS / survival score / absolute time error

calibration:
  probability bins vs observed frequencies

sharpness:
  narrow distributions only when justified

branch quality:
  coverage of realized future branch

causal forecast:
  interventional validity

utility:
  decision quality under forecast uncertainty
```

القاعدة:

```text
forecast حاد لكنه غير calibrated = خطر
forecast calibrated لكنه واسع دائماً = عديم القرار
```

نحتاج الاثنين معاً.

---

## 11. Event Compiler

### 11.1 المدخل

```text
stream of observations/actions/tool calls
+ current state
+ event graph
+ successor map
+ causal hypotheses
+ regime estimate
```

### 11.2 مراحل compiler

```text
1. detect boundary
2. parse event object
3. update event graph
4. estimate current regime
5. generate multi-horizon successor forecasts
6. compute hazards/time windows
7. branch counterfactuals for high-impact events
8. score uncertainty/calibration
9. select information-gain or control action
10. observe outcome
11. compute forecast residual
12. update event schema and successor map
```

### 11.3 Forecast residual

```text
ε_event = {
  type_error,
  timing_error,
  omitted_event,
  false_event,
  causal_error,
  regime_error,
  consequence_error,
  calibration_error
}
```

هذا أهم من سجل فشل عادي؛ لأنه يعلم النظام **أي طبقة من التنبؤ فشلت**.

---

## 12. Prospect memory: التذكر من أجل المستقبل

Prospective memory ليست مجرد استرجاع الماضي؛ هي الاحتفاظ بنية حتى يظهر cue مستقبلي. دراسات encoding تشير إلى مساهمة نظام ذاكرة عام مع network تنفيذي مخصص للنية المستقبلية. [Prospective memory encoding](https://www.sciencedirect.com/science/article/abs/pii/S1053811909009586)

في البيئة الطبيعية، يتأثر تنفيذ النية بالأهمية، المساعدات الخارجية، التأخير، وإعادة تنشيط النية، مع بقاء جزء كبير من variance غير مفسر. [Prospective memory in the wild](https://pmc.ncbi.nlm.nih.gov/articles/PMC9765353/)

الترجمة:

```text
future intention {
  trigger_event
  intended_action
  expiry
  priority
  required_context
  verification
  fallback
}
```

لا ننتظر أن يتذكر النظام intention عند كل turn. نستخدم event trigger:

```text
when event pattern matches:
  retrieve intention
  check current context
  execute or revise
```

---

## 13. الذاكرة المستقبلية كـpredictive map

الـmemory الأفضل ليست archive للماضي. هي map تربط:

```text
current state
→ likely successors
→ actions that alter successors
→ risk and opportunity
```

نخزن لكل event:

```text
successor distribution
hazard profile
causal preconditions
counterfactual branches
failure signatures
```

وهكذا يتحول replay من:

```text
ماذا حدث؟
```

إلى:

```text
ما الذي كان الحدث يتوقعه؟
ما الذي تحقق؟
أين انكسر النموذج؟
ما البديل الذي كان يمكن أن يحدث؟
```

---

## 14. التجارب الجديدة

### F1 — Token trace vs event trace

```text
A: next-token / raw transcript
B: event segmentation
C: nested event graph
```

**القياس:** long-horizon state tracking، event recall، next-event forecast، recovery.

### F2 — Next event vs next action

```text
A: predict next action directly
B: predict next event then choose action
C: event + hazard + action
```

### F3 — Recent history vs successor map

```text
A: recent trace retrieval
B: event graph retrieval
C: successor representation
D: successor representation + context conditioning
```

اختبار composition وregime shift.

### F4 — Point forecast vs calibrated future cone

```text
A: single best future
B: top-k futures
C: probability/time-window distribution
D: distribution + disconfirming signals
```

### F5 — Observational vs counterfactual future

```text
A: continue current trajectory
B: simulate do(action)
C: simulate multiple interventions
D: intervention + causal verifier
```

### F6 — Early warning

نخلق بيئات تقترب من regime shift ونقيس:

```text
هل تتغير recovery latency قبل collapse؟
هل تزيد autocorrelation؟
هل يزداد forecast uncertainty بطريقة مفيدة؟
هل يتخذ النظام action وقائياً؟
```

### F7 — Multi-timescale anticipation

```text
A: one horizon
B: micro + meso
C: micro + meso + macro
D: multi-horizon + shared event graph
```

### F8 — Prospective memory

نقدم intention قديمة ثم cue مستقبلية بعد context changes، ونختبر:

```text
trigger detection
stale intention rejection
correct update
execution reliability
```

### F9 — Forecasting calibration

نقارن:

```text
verbal confidence
calibrated probabilistic forecast
external forecast controller
```

مع Brier/log/CRPS/survival scores، لا pass/fail فقط.

---

## 15. ما الذي يعنيه "توقع المستقبل إلى أقصى حد"؟

ليس أن يدّعي النظام معرفة المستقبل الغيبي. الحد الأقصى العلمي هو:

```text
1. compress past into event structure
2. learn temporal/causal transitions
3. represent multiple horizons
4. maintain a branching future distribution
5. identify high-impact activation events
6. simulate counterfactuals before irreversible actions
7. monitor leading indicators and regime shifts
8. update beliefs continuously
9. calibrate confidence after outcomes
10. remember future intentions and triggers
```

والحدود غير القابلة للإلغاء:

```text
unknown interventions
nonstationary regimes
chaotic sensitivity
partial observability
unmodeled agents
measurement delay
irreversible surprises
```

لذلك لا نعد بـ"أقصى prediction" كيقين، بل بـ**أقصى forecastable structure under explicit uncertainty**.

---

## 16. الفكرة الجوهرية الجديدة

الذكاء الأعلى قد لا يكون في معرفة إجابة صعبة، بل في بناء تمثيل يسبق الحدث:

```text
ordinary system:
  reacts after event

strong system:
  predicts next event

stronger system:
  predicts event + timing + consequences

much stronger system:
  predicts how its own action changes the event distribution

frontier system:
  detects which future branch is dangerous,
  what observation would disconfirm it,
  and what intervention changes the trajectory
```

هذه ليست شخصية أو وعياً بحد ذاتها، لكنها أقرب بكثير إلى جوهر cognition الموجه نحو المستقبل من مجرد token prediction.

---

## 17. المصادر وتصنيف الدليل

### Direct evidence

- event boundaries + hippocampal/DMN reactivation: [Nature 2023](https://www.nature.com/articles/s41593-023-01331-6)
- event-network centrality and memory: [Nature Communications](https://www.nature.com/articles/s41467-022-31965-2)
- human successor-like future representations: [eLife](https://elifesciences.org/articles/78904)
- human hippocampal–entorhinal temporal graph prediction: [Nature 2024](https://www.nature.com/articles/s41586-024-07973-1)
- hierarchical past/future anticipation: [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11496687/)
- dynamic predictive coding model: [PLOS Computational Biology](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1011801)
- temporal hazard and expectation updating: [PubMed](https://pubmed.ncbi.nlm.nih.gov/31415885/)
- prospective memory encoding and real-world intention: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1053811909009586), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9765353/)
- early-warning signals for regime shifts: [Scheffer et al.](https://pdodds.w3.uvm.edu/files/papers/others/2009/scheffer2009a.pdf), [ESD review](https://esd.copernicus.org/articles/15/1117/2024/)

### Design hypothesis

- event graph as primary memory unit؛
- successor representation for future-oriented memory؛
- hazard-conditioned event controller؛
- multi-horizon futures cone؛
- activation-event counterfactual branching؛
- forecast residual compiler؛
- early-warning layer for cognitive/state collapse.

### Experiment required

كل claim عن أن event compiler يتفوق على raw trace، أو أن successor map تزيد long-horizon transfer، أو أن counterfactual branch تمنع catastrophic failure، يجب اختباره في F1–F9 قبل تسجيل أي capability gain.

**الحالة:** هذه الجولة رفعت event/future prediction إلى القلب المعماري لـTAEC v2، لكنها لم تنتج نتيجة أداء بعد.
