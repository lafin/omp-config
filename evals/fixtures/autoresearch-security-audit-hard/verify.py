#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MODULES = ['auth.py', 'handlers.py']
BUGS = ['search_invoices', 'export_invoices', 'delete_tenant']
DECOYS = ['get_invoice', 'list_invoices', 'download_export']
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


import re

SEV = re.compile(r"\b(HIGH|MEDIUM)\b", re.I)


def flagged(text, name, levels):
    """True if a report line, or a heading section whose heading names `name`, carries a severity in `levels`."""
    hits = set()
    for line in text.splitlines():
        if name in line:
            hits |= {m.upper() for m in SEV.findall(line)}
    for section in re.split(r"\n(?=#)", text):
        head = section.split("\n", 1)[0]
        if head.startswith("#") and name in head:
            hits |= {m.upper() for m in SEV.findall(section)}
    return bool(hits & levels)


def main():
    root = Path(sys.argv[1]).resolve()
    initial, final = files(INITIAL), files(root)
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(root.rglob("*.md"))
                      if not {".git"} & set(p.relative_to(root).parts))
    tsv, tsv_detail = results_tsv(root)
    checks = [
        check("sources_unchanged", "preservation", True, all(final.get(m) == initial[m] for m in MODULES), "source modules byte-identical"),
        check("no_files_removed", "scope", True, set(initial) <= set(final), "initial files retained"),
        check("active_marker_removed", "completeness", True, not (root / "autoresearch/.active").exists(), "autoresearch/.active absent"),
    ]
    for name in BUGS:
        checks.append(check(f"bug_{name}_high", "correctness", True, flagged(text, name, {"HIGH"}), f"{name} reported HIGH"))
    for name in DECOYS:
        checks.append(check(f"decoy_{name}_not_flagged", "correctness", True, not flagged(text, name, {"HIGH", "MEDIUM"}), f"{name} not reported HIGH or MEDIUM"))
    checks += [
        check("results_tsv", "reporting", False, tsv is not None, tsv_detail or str(tsv)),
        check("handoff_json", "reporting", False, tsv is not None and handoff_ok(tsv), "handoff.json with schema_version 1"),
    ]
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
