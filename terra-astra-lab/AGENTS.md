# AGENTS.md — TAEC Lab

## Scope

هذا المختبر مستقل عن `/home/user/video-translator`. ممنوع تعديل Fawri من هنا.

## Rules

1. لا تُسمّى نتيجة synthetic أو mock capability gain.
2. UNKNOWN ليست صفراً وليست نجاحاً.
3. كل forecast يسجل النوع والزمن والاحتمال ومصدره.
4. لا تُضاف آلية جديدة قبل وجود ablation وkill condition.
5. لا توجد شبكة أو API أو model download.
6. الاختبارات deterministic وتعمل بـPython stdlib.
7. لا تُخزن chain-of-thought؛ فقط القرارات، الآثار، والفشل.
8. أي integration مع model خارجي يحتاج runner مستقل وheld-out evaluator.

## Current exit criterion

النسخة الحالية تنجح فقط إذا:

- schemas قابلة للتسلسل؛
- Event Compiler يكتشف حدود الأحداث في fixture؛
- scoring يتعامل مع الاحتمالات؛
- F1–F3 protocol ينتج trace/report قابلين لإعادة التشغيل؛
- لا يوجد ادعاء خارج حدود synthetic protocol.
