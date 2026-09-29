"""Run an investigation from the terminal and print the reasoning trace + report.

    cd backend && python -m scripts.run_demo [--scope "Dept of Transport"]
"""

import argparse

from app.agents.workflow import run_investigation
from app.models import InvestigationRequest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scope", default="all")
    p.add_argument("--question", default=None)
    p.add_argument("--max-iterations", type=int, default=3)
    args = p.parse_args()

    r = run_investigation(InvestigationRequest(scope=args.scope, question=args.question,
                                               max_iterations=args.max_iterations))

    print("=" * 80, "\nAGENT TRACE\n" + "=" * 80)
    for t in r.trace:
        print(f"[{t.step:02d}] it{t.iteration} {t.agent:<12} {t.action:<22} {t.detail}")

    print("\n" + "=" * 80, "\nREPORT\n" + "=" * 80)
    print(r.report["summary"])
    for n in r.report["networks"]:
        print(f"\n>> RISK {n['risk_score']:.2f} — {', '.join(n['company_names'])}")
        print(n["narrative"])
    print("\nExplained away by the Skeptic:")
    for d in r.report["dismissed"]:
        print(f"  - {d['id']} {d['kind']} [{d['status']}]: {d['why']}")


if __name__ == "__main__":
    main()
