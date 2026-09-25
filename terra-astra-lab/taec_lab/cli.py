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
    hb.add_argument("--difficulty", default="hard", choices=("easy", "hard"))

    hs = subparsers.add_parser("heldout-solve", help="solve pack with a Mind (or cold baseline)")
    hs.add_argument("--pack-dir", default="heldout/pack-v1")
    hs.add_argument("--predictions", default="heldout/predictions.json")
    hs.add_argument("--brain-dir", default=None,
                    help="brain to solve with; omit for cold-uniform baseline")

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

    recall = subparsers.add_parser("recall", help="retrieve knowledge items")
    recall.add_argument("query")
    recall.add_argument("--top-k", type=int, default=3)
    recall.add_argument("--brain-dir", default=str(default_brain_dir()))

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
                              difficulty=args.difficulty)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    if args.command == "heldout-solve":
        result = solve_pack(pack_dir=args.pack_dir, predictions_path=args.predictions,
                            brain_dir=args.brain_dir)
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
    if args.command == "recall":
        mind = TAECMind(brain_dir=args.brain_dir)
        hits = mind.bank.search(args.query, top_k=args.top_k)
        payload = [
            {"item_id": h.item_id, "title": h.title, "score": h.score(args.query),
             "use_count": h.use_count, "success_count": h.success_count}
            for h in hits
        ]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
