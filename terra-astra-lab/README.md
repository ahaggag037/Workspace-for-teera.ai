# TAEC Lab — Minimal Event/Future Compiler

هذا مختبر معزول لتحويل تصميم TAEC v2 إلى تجربة قابلة للتشغيل. لا يعدّل مشروع Fawri ولا يثبت أن COK/RCC أفضل من baseline.

## الحالة

- `PROTOCOL_TEST_ONLY`: أول vertical slice لـ F1–F3 على عالم أحداث اصطناعي مضبوط، وقد تم تشغيله فعلياً.
- لا توجد تجربة نموذج خارجي أو claim عن capability.
- `held-out` الحقيقي لم يُفتح بعد؛ بيانات هذا الإصدار protocol/dev وليست دليلاً تأكيدياً.

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
