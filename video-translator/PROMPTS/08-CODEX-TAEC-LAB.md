# PROMPTS/08-CODEX-TAEC-LAB.md — بناء مختبر TAEC/AER-EGM

> **أمر مستقل قابل للصق في Codex.**
> يبني مختبراً خارج Fawri ويختبر فرضية النقل السلوكي من Terra إلى Astra.
> لا ينفّذ أي تغيير في Fawri، ولا يدّعي نجاحاً قبل وجود traces وheld-out evidence.

---

## BEGIN PASTE

أنت Codex، مهندس تجارب وتنفيذ مستقل. مهمتك الوحيدة في هذه الرسالة هي بناء مختبر معزول اسمه **TAEC Lab** لا تعديل مشروع Fawri.

### 0) التعريف والحدود غير القابلة للتفاوض

- `TAEC` = `Terra-to-Astra Execution Compiler`.
- `AER-EGM` = `Adaptive External Recurrence with Evidence-Gated Memory`، محرك الحالة والتصعيد داخل TAEC.
- هذه تجربة harness/behavior، وليست محاولة لتعديل weights أو استنساخ architecture أو الادعاء أن Terra صار Astra.
- جذر Fawri المحمي هو `/home/user/video-translator`.
- جذر المختبر الإلزامي هو `/home/user/terra-astra-lab`، أو مسار خارجي يحدده المستخدم صراحةً.
- قبل أي كتابة، احسب `realpath` للمسارين. إذا كان `LAB_ROOT` داخل Fawri أو يساويه: **توقف BLOCKED**.
- ممنوع تعديل أو حذف أو إعادة تسمية أي ملف تحت Fawri، وممنوع تعديل `.git` أو `README.md` أو `src/` أو `tests/` أو `tools/` أو `PROMPTS/` أو `meta/` داخله.
- ممنوع إنشاء symlink من المختبر إلى Fawri، وممنوع import مباشر من كود Fawri. إن احتجت fixture، انسخ أقل قدر من البيانات إلى المختبر مع سجل المصدر، ولا تستخدم مساراً حياً.
- ممنوع `rm -rf` أو `git clean` أو أوامر واسعة. لا تتصل بالشبكة، ولا تستخدم API key أو subscription أو cloud runner، ولا تثبّت حزمة من الإنترنت.
- لا تخترع نتائج model run أو tokens أو latency. القيمة المفقودة هي `UNKNOWN` وليست صفراً.
- لا تخزّن chain-of-thought. خزّن القرار المختصر، الأداة، الـartifact، evidence، والفشل فقط.

### 1) المصدر والبحث

اقرأ من Fawri قراءة فقط، إن وجد:

- `/home/user/video-translator/RESEARCH/TERRA-ASTRA-TRANSFER.md`
- `/home/user/video-translator/meta/COMMAND-OS.md`

هذه مصادر تصميم وليست إثباتاً للنتيجة. إن كان web access متاحاً، تحقّق من المصادر الرسمية والبحثية المذكورة في ملف البحث، وسجّل URL ووقت الاطلاع في `RESEARCH_SOURCES.md`. إن لم يكن متاحاً، لا تدّعِ أنك تحققت؛ سجّل `WEB_RESEARCH: BLOCKED`.

لا تستخدم الإنترنت وقت تشغيل المختبر. لا تخلط المصادر العامة في كل Run Packet؛ الاسترجاع يكون progressive disclosure.

### 2) الهدف الوحيد وتعريف الانتهاء

أنشئ مختبراً محلياً قابلاً للتشغيل يحقق الآتي:

1. يعرّف عقد TAEC، وذاكرة AER-EGM، وحالات الدورة، وسياسة `assume/ask`، وبوابة evidence.
2. يتيح تسجيل وتشغيل traces حقيقية أو مستوردة من runner خارجي، مع mock runner للاختبارات البرمجية فقط.
3. يعرّف conditions قابلة للمقارنة: `raw`, `contract`, `memory`, `verifier`, `specialists`, `full`.
4. يجهز benchmark تطويري صغيراً وواجهة held-out لا تكشف acceptance المخفي أثناء التطوير.
5. يحسب quality/cost/scope/retry/latency metrics من بيانات موجودة فعلاً.
6. يطبق ablations وkill conditions ولا يعلن تحسناً من mock data.
7. يثبت كل ذلك باختبارات deterministic تعمل بلا شبكة أو نموذج أو GPU.

إذا تعذر إنشاء المختبر خارج Fawri، لا تبحث عن workaround داخل Fawri؛ اترك `BLOCKED` مع الدليل.

### 3) شكل المختبر المسموح

استخدم Python stdlib أولاً وبأقل dependencies. يمكنك تغيير أسماء الوحدات، لكن يجب أن توفر هذه القدرات ومسارات مفهومة:

```text
/home/user/terra-astra-lab/
  README.md
  AGENTS.md                         # قصير، لا يتجاوز 150 سطراً
  ROADMAP.md
  PROGRESS.md
  RESEARCH_SOURCES.md
  TRADEOFFS.md
  pyproject.toml أو requirements موثق بلا تثبيت تلقائي
  taec_lab/
    contracts.py                    # task/run/evidence schemas
    memory.py                       # STATE/DECISIONS/EVIDENCE/FAILURES/NEXT
    router.py                       # D0/D1/D2 والتصعيد bounded
    trace.py                        # JSONL events وartifact references
    scoring.py                      # metrics وUNKNOWN handling
    report.py                       # reports قابلة لإعادة التشغيل
    cli.py
  benchmark/
    dev/                             # tasks ذات acceptance معلن
    heldout/README.md                # قوالب فقط؛ لا تنشئ gold labels هنا
    schemas/
  runs/
  reports/
  tests/
```

لا تنشئ الملفات لمجرد مطابقة الشجرة. الكود والاختبارات هما المواصفة. اجعل كل path تحت `LAB_ROOT`، وافحص path traversal.

### 4) عقد TAEC/AER-EGM

طبّق state machine صريحة، لا prompt طويل:

```text
OBSERVE_CONTRACT → SCOUT → PLAN → BUILD → VERIFY
→ ADVERSARIAL_REVIEW → REPAIR → COMMIT_REPORT
```

كل Run Packet يحتوي فقط على:

- `task_id`, الهدف، الـartifact المطلوب.
- `definition_of_done` وallowed paths.
- القيود والمخاطر ودرجة reversibility.
- evidence ذات الصلة فقط.
- الحالة المختصرة والخطوة التالية.

ذاكرة كل run منظمة في:

```text
STATE.json       # الحالة الحالية، condition، round، next action
DECISIONS.jsonl  # قرار، بدائل، سبب مختصر، قابلية الرجوع
EVIDENCE.jsonl   # claim، source/artifact، checker، status
FAILURES.jsonl   # failure class، reproduction، repair، result
NEXT.md          # خطوة واحدة تالية، لا backlog مفتوح
```

قواعد `assume/ask`:

- افترض وسجّل إذا كان القرار منخفض المخاطر، قابلاً للرجوع، ولا يغير Definition of Done.
- اطلب clarification أو سجّل `BLOCKED` إذا كان القرار غير قابل للرجوع، يمس scope أو data أو acceptance، أو يوجد تعارض لا يمكن حسمه بالدليل.
- لا تجعل السؤال بديلاً عن فحص الملفات أو الاختبار.

Adaptive budget:

- `D0`: دورة واحدة + أدوات/تحقق حتمي.
- `D1`: planner مختصر + builder + verifier.
- `D2`: بديلان أو adversarial review ثم verifier وrepair.
- ابدأ بـ D0، وصعّد فقط عند ambiguity، risk، failed verifier، contradiction، أو regression.
- الحد الأقصى 3 rounds و2 bounded workers في الجولة. لا debate مفتوح ولا non-termination.
- لا تمنح كل worker reasoning مرتفعاً تلقائياً. المنسق يقرر، والworkers ينفذون مهاماً محدودة.

### 5) طبقات المقارنة والـablations

ثبّت task pack ونسخة الأدوات وترتيب المهام لكل condition. لا تغيّر أكثر من متغير في ablation.

- `raw`: لا contract خاص، لا memory، لا verifier خارجي؛ نفس الأدوات المتاحة.
- `contract`: raw + intent/Definition of Done/scope contract.
- `memory`: contract + progressive disclosure والذاكرة المنظمة.
- `verifier`: memory + deterministic verifier وrepair loop.
- `specialists`: verifier + Scout/Builder/Adversary bounded مع orchestrator واحد.
- `full`: كل ما سبق + adaptive budget وrisk-based assume/ask.

وفّر `ablate --remove contract|memory|verifier|specialists|adaptive_budget` أو ما يعادله. لا تعتبر full أفضل لمجرد أنه الأخير.

أي mock runner يجب أن يحمل `runner_type: MOCK_ONLY`، ويستخدم لاختبار schemas وscoring فقط، ويُستبعد من أي claim عن Terra.

### 6) benchmark دون تلوث

أنشئ في `benchmark/dev/` ثماني مهام self-contained متنوعة، لا تعتمد على Fawri:

- مهمتان coding/fixture repair مع tests.
- مهمة scope discipline متعددة الملفات.
- مهمة ambiguity وclarification.
- مهمة بحث محلي بمصادر fixture مع claims قابلة للفحص.
- مهمة artifact/document quality.
- مهمة tool failure/recovery.
- مهمة regression بعد تغيير صغير.

كل task يحدد: `task_id`, category, prompt، allowed paths، risk، clarification policy، artifact، acceptance checks، وseed إن وجد.

لا تضع gold acceptance أو hidden evaluator لمهام held-out في الكود الذي يطوره Codex. أنشئ فقط:

```text
benchmark/heldout/README.md
benchmark/heldout/manifest.schema.json
```

ويجب أن تبقى حالة held-out في التقارير `NOT_RUN` إلى أن يضيف operator مستقل task pack وevaluator بعد تجميد الكود. إذا اضطررت إلى اختبار protocol، استخدم fixture موسوماً `PROTOCOL_TEST_ONLY` ولا تسميه held-out evidence.

### 7) traces والتقييم

وفّر schema لتسجيل run فعلي أو trace مستورد:

```json
{
  "run_id": "...",
  "task_id": "...",
  "condition": "raw|contract|memory|verifier|specialists|full",
  "runner_type": "terra|manual|mock",
  "status": "PASS|FAIL|BLOCKED|UNKNOWN",
  "rounds": 0,
  "input_tokens": null,
  "output_tokens": null,
  "latency_seconds": null,
  "human_minutes": null,
  "retries": 0,
  "scope_violations": 0,
  "unsupported_claims": 0,
  "hallucinated_tools": 0,
  "regressions": 0,
  "artifacts": [],
  "evidence": [],
  "notes": ""
}
```

عرّف `accepted_outcome = 1` فقط إذا نجح evaluator الحقيقي، وظهر artifact المطلوب، ولم توجد scope violation أو hallucinated tool أو unsupported claim قاتل للمهمة. غير ذلك `0` أو `UNKNOWN` حسب نقص الدليل؛ لا تحوّل missing data إلى failure صامت أو نجاح.

التقرير يجب أن يعرض على الأقل:

- accepted outcome وfirst-pass acceptance.
- correctness/acceptance per task.
- scope violations، unsupported claims، hallucinated tools.
- retries، rounds، repair success، regressions.
- median وP90 latency.
- tokens وhuman minutes عندما تكون موجودة.
- `accepted_outcome_per_1k_tokens` و`accepted_outcome_per_minute` فقط عندما تكون المقامات حقيقية.
- مقارنة كل condition بالمهمة نفسها، ثم aggregate مع `N`, missingness، وعدم ادعاء دلالة إحصائية من pilot صغير.

لا تستخدم Terra نفسه منفذاً وحكماً وحيداً في scoring. استخدم tests/rules/fixtures أولاً، ومراجعة بشرية مزدوجة أو evaluator مستقل للـartifact quality عند الحاجة.

### 8) kill conditions وtrade-offs

اكتبها قبل تشغيل benchmark في `TRADEOFFS.md`، وسجّل كل قرار مع البدائل والكلفة ودليل القبول وشرط الرجوع.

أوقف فوراً إذا:

1. كتب المختبر خارج `LAB_ROOT` أو لمس Fawri.
2. احتاج شبكة/API key أو أخفى فشل dependency.
3. اختُرعت tokens/latency/results أو خُلِط mock بتجربة Terra.
4. تلوث held-out أو ظهر evaluator في prompt أثناء التشغيل.
5. تجاوزت الدورة حدود rounds/workers أو دخلت loop.

اقتُل أي component في pilot/confirmatory run إذا:

- زاد median cost أو latency بأكثر من 25% بلا تحسن واضح في accepted outcomes.
- سبب scope violation أو hallucinated tool في أي حالة acceptance حرجة.
- خفّض held-out accepted outcome ≥10 نقاط مئوية مقارنةً بأبسط condition، عند توفر 8 held-out tasks على الأقل.
- لم يحقق full stack تحسناً مقابل أفضل ablation مع زيادة تكلفة ملحوظة؛ لا تدمجه ولا تدافع عنه.

هذه thresholds قواعد قرار مسبقة وليست برهاناً إحصائياً. عند `N` صغير اكتب `INSUFFICIENT_POWER` بدلاً من إعلان فائز.

### 9) ترتيب التنفيذ الإلزامي

1. افحص المسارات والحماية، ثم شغّل baseline للمختبر إن كان موجوداً.
2. أنشئ `ROADMAP.md` و`PROGRESS.md` بحالات `failing`، وسجّل القيود.
3. اكتب schemas واختبارات path guard وstate transitions وUNKNOWN handling قبل التنفيذ.
4. نفّذ contract/memory/router/trace/scoring بأبسط كود.
5. أضف dev fixtures وprotocol test فقط.
6. شغّل tests، lint إن كان مضبوطاً، وself-check بلا شبكة.
7. راجع diff وتأكد أن Fawri لم يتغير، وأن held-out ما زال `NOT_RUN`.
8. لا تبدأ تجربة Terra فعلية أو تكامل Fawri في هذه الرسالة؛ ذلك هدف لاحق بإذن صريح.

حد الإصلاح: ثلاث دورات اختبار/إصلاح. بعد ذلك اترك `FAILING` أو `BLOCKED` مع الدليل، ولا توسع النطاق.

### 10) التقرير الإلزامي

أعد التقرير التالي فقط، مع القيم الفعلية:

```text
BEGIN REPORT
OBJECTIVE: build isolated TAEC/AER-EGM lab
LAB_ROOT: <real absolute path>
Fawri touched: NO | YES
STATUS: PASSING | FAILING | BLOCKED
WEB_RESEARCH: VERIFIED | BLOCKED | NOT_REQUIRED
CHANGED_FILES: <paths under LAB_ROOT only>

BASELINE_COMMAND: <actual command or NONE>
BASELINE_EXIT_CODE: <actual code or NONE>
BASELINE_LAST_30_LINES:
<raw output>

TEST_COMMAND: <actual command>
TEST_EXIT_CODE: <actual code>
TEST_LAST_30_LINES:
<raw output>

DEV_BENCHMARK: PROTOCOL_ONLY | RUN | BLOCKED
HELDOUT_STATUS: NOT_RUN | RUN
MOCK_RESULTS_USED_AS_CLAIM: NO | YES
NETWORK_USED: NO | YES

KILL_CONDITIONS_REGISTERED: yes | no
TRADEOFFS_REGISTERED: yes | no
ROADMAP_UPDATED: yes | no
PROGRESS_UPDATED: yes | no
UNVERIFIED_OR_BLOCKED:
- <items with evidence, or NONE>
NEXT_SINGLE_OBJECTIVE:
<one objective only>
END REPORT
```

`PASSING` لا تعني أن Terra اقترب من Astra؛ تعني فقط أن lab protocol والكود والاختبارات نجحت. لا تستخدم كلمة `equivalent`, `Astra-level`, أو `improved` إلا مع held-out evidence حقيقي.

## END PASTE

*الإصدار 1.0 · 2026-09-24 · مستقل عن Fawri · لا تكامل قبل تفويض صريح*
