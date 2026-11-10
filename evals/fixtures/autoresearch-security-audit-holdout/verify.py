#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MODULE = 'notes.py'
BUG = 'share_note'
DECOY = 'render_note'
SUB = 'security'
INITIAL_METRIC = None
INITIAL = Path(__file__).with_name("initial")
COMMON = ["iteration", "commit", "metric", "delta", "guard", "status", "description"]
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
IGNORED = {".git", "autoresearch", "__pycache__"}


def run(command, cwd, env=None):
    return subprocess.run(
        command, cwd=cwd, env=env or {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20,
    )


def files(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and not IGNORED & set(p.relative_to(root).parts)
    }


def check(name, dimension, critical, passed, detail):
    return {"name": name, "dimension": dimension, "critical": critical, "passed": bool(passed), "detail": detail}


def results_tsv(root):
    for path in sorted(root.glob(f"autoresearch/{SUB}-*/{SUB}-results.tsv")):
        rows = [r.split("\t") for r in path.read_text(encoding="utf-8").splitlines() if r and not r.startswith("#")]
        if rows and rows[0][: len(COMMON)] == COMMON:
            status = COMMON.index("status")
            body = [r for r in rows[1:] if len(r) > status]
            if body:
                return path, ""
    return None, f"no autoresearch/{SUB}-*/{SUB}-results.tsv with the common header, a baseline row, and an iteration row"


def handoff_ok(path):
    try:
        data = json.loads((path.parent / "handoff.json").read_text(encoding="utf-8"))
        return type(data.get("schema_version")) is int and data["schema_version"] == 1
    except (OSError, ValueError, AttributeError):
        return False


def main():
    root = Path(sys.argv[1]).resolve()
    initial, final = files(INITIAL), files(root)
    reports = [p.read_text(encoding="utf-8", errors="replace") for p in sorted(root.rglob("*.md"))
               if not {".git"} & set(p.relative_to(root).parts)]
    text = "\n".join(reports)
    lines = text.splitlines()
    decoy_flagged = any(DECOY in l and any(s in l.upper() for s in ("HIGH", "MEDIUM")) for l in lines)
    commits = run(["git", "rev-list", "--count", "HEAD"], root, GIT_ENV)
    tsv, tsv_detail = results_tsv(root)
    checks = [
        check("source_unchanged", "preservation", True, final.get(MODULE) == initial[MODULE], f"{MODULE} byte-identical to initial"),
        check("no_files_outside_report", "scope", True, set(initial) <= set(final), "initial files retained"),
        check("real_bug_reported", "correctness", True, BUG in text and "HIGH" in text.upper(), f"a markdown report names {BUG} with HIGH severity"),
        check("decoy_not_reported", "correctness", False, not decoy_flagged, f"no report line flags {DECOY} as HIGH or MEDIUM"),
        check("active_marker_removed", "completeness", True, not (root / "autoresearch/.active").exists(), "autoresearch/.active absent"),
        check("results_tsv", "reporting", False, tsv is not None, tsv_detail or str(tsv)),
        check("handoff_json", "reporting", False, tsv is not None and handoff_ok(tsv), "handoff.json with schema_version 1"),
    ]
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
