"""Command line entry point for the isolated TAEC lab."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .credit import run_credit
from .eval_memory import run_memory_eval
from .experiment import run_protocol
from .heldout import build_pack, evaluate_predictions, solve_pack
from .learning import train_mind
from .mind import TAECMind, default_brain_dir
from .multiseed import run_multiseed
from .synthetic import build_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic TAEC Lab protocols")
    subparsers = parser.add_subparsers(dest="command", required=True)

    protocol = subparsers.add_parser("protocol", help="run synthetic F1-F3 protocol")
    protocol.add_argument("--seed", type=int, default=20260924)
    protocol.add_argument("--train", type=int, default=40)
    protocol.add_argument("--test", type=int, default=20)
    protocol.add_argument("--difficulty", default="easy", choices=("easy", "hard"))
    protocol.add_argument("--report-dir", default="reports")

    mem = subparsers.add_parser("memory-eval", help="cold-start vs warm-memory transfer test")
    mem.add_argument("--seed", type=int, default=20260924)
    mem.add_argument("--train", type=int, default=40)
    mem.add_argument("--test", type=int, default=20)
    mem.add_argument("--difficulty", default="easy", choices=("easy", "hard"))
    mem.add_argument("--report-dir", default="reports")

    ms = subparsers.add_parser("multiseed", help="memory transfer over disjoint seeds")
    ms.add_argument("--seeds", type=int, nargs="+", default=[20260924, 424242, 777777])
    ms.add_argument("--train", type=int, default=40)
    ms.add_argument("--test", type=int, default=20)
    ms.add_argument("--difficulty", default="easy", choices=("easy", "hard"))
    ms.add_argument("--report-dir", default="reports")

    hb = subparsers.add_parser("heldout-build", help="build sealed held-out task pack")
    hb.add_argument("--out-dir", default="heldout/pack-v1")
    hb.add_argument("--traces", type=int, default=12)
    hb.add_argument("--seed-start", type=int, default=999001,
                    help="pack seed start; keep disjoint from all dev ranges")
    hb.add_argument("--difficulty", default="hard", choices=("easy", "hard"))

    hs = subparsers.add_parser("heldout-solve", help="solve pack with a Mind (or cold baseline)")
    hs.add_argument("--pack-dir", default="heldout/pack-v1")
    hs.add_argument("--predictions", default="heldout/predictions.json")
    hs.add_argument("--brain-dir", default=None,
                    help="brain to solve with; omit for cold-uniform baseline")
    hs.add_argument("--segmentation", default="hard", choices=("hard", "soft", "v2"),
                    help="hard detector (default), fusedseg-v2 candidate, or killed soft arm")

    he = subparsers.add_parser("heldout-eval", help="verify seal and score predictions")
    he.add_argument("--pack-dir", default="heldout/pack-v1")
    he.add_argument("--predictions", default="heldout/predictions.json")
    he.add_argument("--report", default="heldout/verdict.json")

    learn = subparsers.add_parser("learn", help="train persistent brain banks in workspace")
    learn.add_argument("--seed", type=int, default=20260924)
    learn.add_argument("--train", type=int, default=40)
    learn.add_argument("--difficulty", default="easy", choices=("easy", "hard"))
    learn.add_argument("--reset", action="store_true",
                       help="wipe banks before training (fresh cold start)")
    learn.add_argument("--brain-dir", default=str(default_brain_dir()))

    credit = subparsers.add_parser("credit", help="grade lessons by dev outcomes")
    credit.add_argument("--seed", type=int, default=20280924)
    credit.add_argument("--traces", type=int, default=12)
    credit.add_argument("--apply", action="store_true",
                        help="write use/success counts back into the bank")
    credit.add_argument("--brain-dir", default=str(default_brain_dir()))

    status = subparsers.add_parser("status", help="show brain bank status")
    status.add_argument("--brain-dir", default=str(default_brain_dir()))

    sseg = subparsers.add_parser(
        "softseg-eval",
        help="ablation: hard vs soft segmentation on frozen banks (pre-registered gates)",
    )
    sseg.add_argument("--dev-seed-start", type=int, default=20500924)
    sseg.add_argument("--eval-seed-start", type=int, default=20510924)
    sseg.add_argument("--n-dev", type=int, default=24)
    sseg.add_argument("--n-eval", type=int, default=24)
    sseg.add_argument("--difficulty", default="hard", choices=("easy", "hard"))
    sseg.add_argument("--brain-dir", default=str(default_brain_dir()))
    sseg.add_argument("--report-dir", default="reports")

    wl = subparsers.add_parser("worklog-status", help="real work-event ledger status")
    wl.add_argument("--ledger", default=None)

    wr = subparsers.add_parser("worklog-record", help="append a REAL work event to the ledger")
    wr.add_argument("--verb", required=True,
                    help="work verb (read/edit/write/test_pass/test_fail/fix/eval/commit/push/...)")
    wr.add_argument("--area", required=True, help="workspace area (code/tests/brain/docs/git/...)")
    wr.add_argument("--phase", required=True,
                    help="work phase (boot/study/implement/verify/tune/seal/document/persist)")
    wr.add_argument("--detail", default="", help="one-line factual description")
    wr.add_argument("--outcome", default="ok", choices=("ok", "fail", "na"))
    wr.add_argument("--corroborated-by", default="", help="artifact/ref that proves this happened")
    wr.add_argument("--source", default="live-turn")
    wr.add_argument("--ledger", default=None)

    we = subparsers.add_parser("worklog-eval", help="real-trace pilot eval (pre-registered gates R1-R8)")
    we.add_argument("--ledger", default=None)
    we.add_argument("--report-dir", default="reports")

    ol = subparsers.add_parser("ops-learn", help="absorb the live ledger into the persistent ops brain")
    ol.add_argument("--ledger", default=None)
    ol.add_argument("--brain", default=None)

    of = subparsers.add_parser("ops-forecast", help="forecast the NEXT real work event")
    of.add_argument("--ledger", default=None)
    of.add_argument("--brain", default=None)

    recall = subparsers.add_parser("recall", help="retrieve knowledge items")
    recall.add_argument("query")
    recall.add_argument("--top-k", type=int, default=3)
    recall.add_argument("--brain-dir", default=str(default_brain_dir()))
    recall2 = subparsers.add_parser("recall2", help="FTS5 recall vault (lessons + lived events)")
    recall2.add_argument("query")
    recall2.add_argument("--top-k", type=int, default=5, dest="top_k")
    recall2.add_argument("--brain-dir", default=str(default_brain_dir()))

    args = parser.parse_args()

    if args.command == "protocol":
        report = run_protocol(
            seed=args.seed, train_count=args.train, test_count=args.test,
            difficulty=args.difficulty, report_dir=Path(args.report_dir),
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.command == "memory-eval":
        report = run_memory_eval(
            seed=args.seed, train_count=args.train, test_count=args.test,
            difficulty=args.difficulty, report_dir=Path(args.report_dir),
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.command == "multiseed":
        report = run_multiseed(
            seeds=args.seeds, train_count=args.train, test_count=args.test,
            difficulty=args.difficulty, report_dir=Path(args.report_dir),
        )
        print(json.dumps({k: v for k, v in report.items() if k != "per_seed"},
                         indent=2, sort_keys=True))
        return 0
    if args.command == "heldout-build":
        manifest = build_pack(out_dir=args.out_dir, n_traces=args.traces,
                              seed_start=args.seed_start, difficulty=args.difficulty)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    if args.command == "heldout-solve":
        result = solve_pack(pack_dir=args.pack_dir, predictions_path=args.predictions,
                            brain_dir=args.brain_dir, segmentation=args.segmentation)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "heldout-eval":
        verdict = evaluate_predictions(pack_dir=args.pack_dir,
                                       predictions_path=args.predictions,
                                       report_path=args.report)
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 0
    if args.command == "learn":
        brain = Path(args.brain_dir)
        if args.reset:
            for name in ("WEIGHTS.json", "KNOWLEDGE.jsonl"):
                (brain / name).unlink(missing_ok=True)
        mind = TAECMind(brain_dir=brain)
        traces = build_dataset(args.train, seed_start=args.seed,
                               regimes=("stable", "stressed"), difficulty=args.difficulty)
        result = train_mind(mind, traces, args.seed)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "credit":
        report = run_credit(seed=args.seed, n_traces=args.traces,
                            brain_dir=args.brain_dir, apply=args.apply)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.command == "status":
        mind = TAECMind(brain_dir=args.brain_dir)
        payload = {
            "status": mind.status,
            "brain_dir": str(mind.brain_dir),
            "weights_updates": mind.weights.meta.get("updates", 0),
            "train_traces": mind.weights.meta.get("train_traces", 0),
            "knowledge_items": len(mind.bank),
            "weights_empty": mind.weights.is_empty(),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.command == "softseg-eval":
        from .softseg import run_softseg_eval

        report = run_softseg_eval(
            dev_seed_start=args.dev_seed_start,
            eval_seed_start=args.eval_seed_start,
            n_dev=args.n_dev,
            n_eval=args.n_eval,
            difficulty=args.difficulty,
            brain_dir=args.brain_dir,
            report_dir=Path(args.report_dir),
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.command == "worklog-status":
        from collections import Counter

        from .realtrace import DEFAULT_LEDGER, load_ledger, op_type

        ledger = Path(args.ledger) if args.ledger else DEFAULT_LEDGER
        rows = load_ledger(ledger)
        payload = {
            "ledger": str(ledger),
            "n_events": len(rows),
            "first_seq": rows[0]["seq"] if rows else None,
            "last_seq": rows[-1]["seq"] if rows else None,
            "op_histogram": dict(Counter(op_type(r) for r in rows)),
            "sources": dict(Counter(r.get("source", "?") for r in rows)),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.command == "worklog-record":
        from .realtrace import DEFAULT_LEDGER, append_event

        ledger = Path(args.ledger) if args.ledger else DEFAULT_LEDGER
        seq = append_event(
            {
                "verb": args.verb,
                "area": args.area,
                "phase": args.phase,
                "detail": args.detail,
                "outcome": args.outcome,
                "source": args.source,
                "corroborated_by": args.corroborated_by,
            },
            path=ledger,
        )
        print(json.dumps({"recorded_seq": seq, "ledger": str(ledger)}, indent=2))
        return 0
    if args.command == "worklog-eval":
        from .realtrace import DEFAULT_LEDGER, run_realtrace_eval

        ledger = Path(args.ledger) if args.ledger else DEFAULT_LEDGER
        report = run_realtrace_eval(ledger_path=ledger, report_dir=Path(args.report_dir))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.command == "ops-learn":
        from .realtrace import DEFAULT_LEDGER, OPS_BRAIN_PATH, learn_ops_brain

        ledger = Path(args.ledger) if args.ledger else DEFAULT_LEDGER
        brain = Path(args.brain) if args.brain else OPS_BRAIN_PATH
        print(json.dumps(learn_ops_brain(ledger_path=ledger, brain_path=brain), indent=2, sort_keys=True))
        return 0
    if args.command == "ops-forecast":
        from .realtrace import DEFAULT_LEDGER, OPS_BRAIN_PATH, forecast_next_ops

        ledger = Path(args.ledger) if args.ledger else DEFAULT_LEDGER
        brain = Path(args.brain) if args.brain else OPS_BRAIN_PATH
        print(json.dumps(forecast_next_ops(ledger_path=ledger, brain_path=brain), indent=2, sort_keys=True))
        return 0
        mind = TAECMind(brain_dir=args.brain_dir)
        hits = mind.bank.search(args.query, top_k=args.top_k)
        payload = [
            {"item_id": h.item_id, "title": h.title, "score": h.score(args.query),
             "use_count": h.use_count, "success_count": h.success_count}
            for h in hits
        ]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.command == "recall2":
        from .recall_vault import search_ledger, search_lessons

        payload = {
            "lessons": search_lessons(args.query, k=args.top_k),
            "lived_events": search_ledger(args.query, k=args.top_k),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
