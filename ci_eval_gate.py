"""
CI/CD evaluation quality gate (Bonus).

Runs the golden-dataset benchmark and BLOCKS (exit 1) if any aggregate metric is
below threshold — the "agent fails eval = no deploy" pattern from the lecture.

Used by the CI workflow (ci/eval-workflow.yml). Run locally with:
    python ci_eval_gate.py
"""

import sys

from benchmark import (
    BenchmarkRunner,
    RAGASEvaluator,
    build_qa_pairs,
    make_agent,
)

# Minimum bars to allow a deploy. Conservative for this teaching pipeline;
# in production tighten faithfulness/relevance toward 0.70 (see exercises.md 1.3).
THRESHOLDS = {
    "avg_faithfulness": 0.50,
    "avg_relevance": 0.50,
    "avg_completeness": 0.50,
    "pass_rate": 0.50,
}


def main() -> None:
    pairs, answers = build_qa_pairs()
    runner = BenchmarkRunner()
    results = runner.run(pairs, make_agent(answers), RAGASEvaluator())
    report = runner.generate_report(results)

    print("== RAG Evaluation Quality Gate ==")
    failed = []
    for key, bar in THRESHOLDS.items():
        value = report[key]
        ok = value >= bar
        print(f"  {key:18s} = {value:.3f}  (>= {bar:.2f})  {'PASS' if ok else 'FAIL'}")
        if not ok:
            failed.append(key)

    if failed:
        print(f"\nQUALITY GATE FAILED: {failed} below threshold — blocking deploy.")
        sys.exit(1)
    print("\nQUALITY GATE PASSED — safe to deploy.")


if __name__ == "__main__":
    main()
