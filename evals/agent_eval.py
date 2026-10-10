#!/usr/bin/env python3
"""Run behavior cases against an agent prompt at a git revision (baseline) or the working tree (treatment).

Status: Evaluator. Boundary: grades only deterministic field checks from the case file;
it does not run the agent inside OMP's task tool, so tool use and delegation are not exercised.
Run: python3 evals/agent_eval.py CASES AGENT_FILE --revision REV|--working-tree --model M --profile P --attempts N --output DIR
Output: DIR/results.jsonl (one row per attempt) and DIR/summary.json. Exit 1 on capture failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from grade import apply_check, parse_response_fields  # noqa: E402


def agent_body(path: str, revision: str | None) -> str:
    text = subprocess.run(["git", "show", f"{revision}:{path}"], capture_output=True, text=True, check=True).stdout if revision else Path(path).read_text()
    return text.split("---", 2)[2].strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    parser.add_argument("agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--revision")
    group.add_argument("--working-tree", action="store_true")
    parser.add_argument("--model", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    prompt = agent_body(args.agent, args.revision)
    cases = [json.loads(line) for line in args.cases.read_text().splitlines()]
    rows, failed_capture = [], 0
    for case in cases:
        for attempt in range(1, args.attempts + 1):
            proc = subprocess.run(
                ["omp", "-p", "--no-session", "--no-extensions", "--no-skills", "--no-rules", "--no-tools", "--thinking=off",
                 f"--profile={args.profile}", f"--model={args.model}", f"--system-prompt={prompt}", case["prompt"]],
                capture_output=True, text=True, timeout=630,
            )
            response = proc.stdout.strip()
            fields = parse_response_fields(response, case["response_fields"])
            checks = [{"name": c["name"], "critical": c["critical"], "passed": fields is not None and apply_check(c, {"fields": fields})[0]} for c in case["checks"]]
            failed_capture += proc.returncode != 0
            rows.append({"case_id": case["id"], "attempt": attempt, "exit_code": proc.returncode, "response": response,
                         "contract_ok": fields is not None, "checks": checks,
                         "critical_passed": fields is not None and all(c["passed"] for c in checks if c["critical"])})
    (args.output / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    summary = {"agent": args.agent, "revision": args.revision or "working-tree",
               "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "model": args.model, "profile": args.profile,
               "cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(), "case_attempts": len(rows),
               "critical_failures": sum(not r["critical_passed"] for r in rows),
               "per_case": {c["id"]: sum(not r["critical_passed"] for r in rows if r["case_id"] == c["id"]) for c in cases},
               "capture_failures": failed_capture}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 1 if failed_capture else 0


if __name__ == "__main__":
    raise SystemExit(main())
