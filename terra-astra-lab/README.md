# TAEC Lab — Minimal Event/Future Compiler

هذا مختبر معزول لتحويل تصميم TAEC v2 إلى تجربة قابلة للتشغيل. لا يعدّل مشروع Fawri ولا يثبت أن COK/RCC أفضل من baseline.

## الحالة

- `WARM / HELDOUT_PASS (pack-hard-v2, sealed)`: خمس بوابات مكتملة — آخرها
  phase 4: مشغّل `TAECMind.v2-fusedseg` (حدود بالدليل المدمج + typing
  بالأحدثية) عدّى البوابات المسجّلة مسبقاً على eval split، وعادى كاشف
  الإنتاج على حزمة مختومة جديدة (dAcc +0.0321، dLL −0.0538، bF1 0.9903).
  ذراع الـ n-best mixture اتقتلت في الـ dev واتسجّلت للمرجعية.
- لا توجد تجربة نموذج خارجي أو claim عن capability.
- `held-out` التالي: compositional (tokens/regimes جديدة كلياً) — بيانات
  هذا الإصدار protocol/dev وليست دليلاً تأكيدياً على العالم المفتوح.

## التشغيل

```bash
python -m unittest discover -s tests -v
python -m taec_lab.cli protocol --seed 20260924 --train 40 --test 20

# External mind lifecycle
python -m taec_lab.cli learn --train 40 --difficulty easy   # persist banks
python -m taec_lab.cli status                                # COLD_START or WARM
python -m taec_lab.cli recall "stable create forecast"       # retrieve lessons
python -m taec_lab.cli credit --traces 12 --apply            # grade lessons

# Gates
python -m taec_lab.cli multiseed --difficulty hard           # 3-seed confirmation
python -m taec_lab.cli heldout-build --difficulty hard       # sealed pack
python -m taec_lab.cli heldout-solve --brain-dir brain --predictions heldout/w.json
python -m taec_lab.cli heldout-eval --predictions heldout/w.json --report heldout/v.json

# Phase 4: soft-segmentation operator
python -m taec_lab.cli softseg-eval                          # hard vs softmix vs v2 ablation
python -m taec_lab.cli heldout-solve --brain-dir brain --segmentation v2 \
    --pack-dir heldout/pack-hard-v2 --predictions heldout/w-v2.json

# Phase 5-6: real work-event tap + operational mind
python -m taec_lab.cli worklog-record --verb edit --area code --phase implement --detail "..."
python -m taec_lab.cli worklog-eval                                 # pre-registered gates
python -m taec_lab.cli ops-learn                                    # absorb ledger into brain-ops/
python -m taec_lab.cli ops-forecast                                 # next real work event (advisory)
MIND_API_PORT=8000 python3 -m taec_lab.mind_api                     # read-only live Mind dashboard/API
```

التقرير الفعلي يكتب إلى:

```text
reports/protocol-f1-f3.json
reports/protocol-f1-f3.md
```

## المقارنات

```text
raw_token
event_transition
successor_representation
hazard_time_to_event
```

## الحدود

- الكود stdlib فقط.
- العالم الاصطناعي يسمح بـground truth حتمي، لذلك النتائج لا تعمم على cognition أو العالم المفتوح.
- أي mock أو synthetic result يظل `PROTOCOL_TEST_ONLY`.
- لا تُعدّل ملفات `/home/user/video-translator` من هذا المختبر.
