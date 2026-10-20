#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MODULE = 'grades.py'
SUB = 'loop'
INITIAL_METRIC = 17
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
            if any(r[status] == "baseline" for r in body) and any(r[status] != "baseline" for r in body):
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
    initial = files(INITIAL)
    final = files(root)
    checks = []

    tests = run([sys.executable, "-m", "unittest", "-q"], root)
    checks.append(check(
        "tests_pass" if SUB == "fix" else "guard_passes", "correctness", True, tests.returncode == 0,
        "python3 -m unittest -q exits 0" if tests.returncode == 0 else "python3 -m unittest -q fails: " + tests.stderr.strip()[-200:],
    ))
    if INITIAL_METRIC is not None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / MODULE).write_bytes(final.get(MODULE, b""))
            (Path(tmp) / "metric.py").write_bytes(initial["metric.py"])
            measured = run([sys.executable, "metric.py"], tmp)
        try:
            value = int(measured.stdout.strip())
        except ValueError:
            value = None
        limit = INITIAL_METRIC * 0.9
        checks.append(check(
            "metric_at_most_90_percent_of_initial", "correctness", True, value is not None and value <= limit,
            f"initial {INITIAL_METRIC}, final {value}, required <= {limit}",
        ))

    frozen = [n for n in initial if n != MODULE and n != "setup_git.sh"]
    changed = [n for n in frozen if final.get(n) != initial[n]]
    checks.append(check("tests_and_metric_unchanged", "preservation", True, not changed, "frozen files identical" if not changed else f"changed: {changed}"))

    outside = sorted({n for n in final if n not in initial} | {n for n in initial if n not in final})
    outside += [n for n in ("setup_git.sh",) if final.get(n) != initial[n]]
    checks.append(check("scope_respected", "scope", True, not outside, f"only {MODULE} may change" if not outside else f"outside scope: {outside}"))

    count = run(["git", "rev-list", "--count", "HEAD"], root, GIT_ENV)
    commits = int(count.stdout) if count.returncode == 0 and count.stdout.strip().isdigit() else 0
    checks.append(check("commit_after_initial", "verification", True, commits >= 2, f"{commits} commit(s) in HEAD history"))

    marker = (root / "autoresearch" / ".active").exists()
    checks.append(check("active_marker_removed", "completeness", True, not marker, "autoresearch/.active exists" if marker else "no active marker"))

    tsv, why = results_tsv(root)
    checks.append(check("results_tsv", "reporting", False, tsv is not None, f"{tsv.relative_to(root)}" if tsv else why))
    checks.append(check("handoff_json", "reporting", False, tsv is not None and handoff_ok(tsv), "handoff.json has schema_version 1" if tsv and handoff_ok(tsv) else "handoff.json missing, unparseable, or schema_version != 1"))
    print(json.dumps({"checks": checks}))


main()
