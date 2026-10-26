#!/usr/bin/env bash
# Upstream-drift benchmark: counts upstream file deltas not yet reviewed into
# the local skills. A delta is "reviewed" once the skill's recorded pin moves to
# the frozen target commit (adopted or declined, recorded in ATTRIBUTION.md).
# Fetches are SHA-pinned, so results are deterministic.
set -euo pipefail
cd "$(dirname "$0")"
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
CACHE="${AUTORESEARCH_UPSTREAM_CACHE:-$HOME/.cache/omp-config-upstreams}"
export CACHE

"$PY" - <<'EOF'
import os, re, subprocess, sys

CACHE = os.environ["CACHE"]
CE = "muratcankoylan/Agent-Skills-for-Context-Engineering"
CE_T = "9ff0c99108b36d3b886defd825d8ac1f47dba374"
# (skill, repo, frozen target, upstream paths, regex extracting the pin from SKILL.md)
META = r'upstream_commit:\s*"?([0-9a-f]{40})'
SOURCES = [(s, CE, CE_T, [f"skills/{s}"], META) for s in [
    "advanced-evaluation", "bdi-mental-states", "context-compression", "context-degradation",
    "context-fundamentals", "context-optimization", "evaluation", "filesystem-context",
    "harness-engineering", "hosted-agents", "latent-briefing", "long-horizon-prompting",
    "memory-systems", "multi-agent-patterns", "project-development", "self-improvement-loops",
    "tool-design"]]
ML, ML_T = "ML-SystemDesign/MLSystemDesign", "8dd0d88852fe7445e9d2627c59124f0f161040c1"
SOURCES += [(s, ML, ML_T, [f"skills/{s}"], META)
            for s in ["lossless-doc-compress", "ml-system-design-review", "ai-stage-gate"]]
ADDY, ADDY_T = "addyosmani/agent-skills", "aeac41d4d005999432bb7312f7ff06383a91d59d"
SOURCES += [(s, ADDY, ADDY_T, [f"skills/{s}"], META)
            for s in ["api-and-interface-design", "source-driven-development"]]
SOURCES += [
    ("security-review", "affaan-m/ECC", "25278e7d7b6cf6e6a4e7a6c8e10f14ff22f0eb5b",
     ["skills/security-review", "skills/search-first"], META),
    ("autoresearch", "uditgoenka/autoresearch", "050e30dc4ba0974b03f2873111b9901ec3211390",
     [".claude/skills/autoresearch", ".claude/commands", "scripts/orchestrate.sh",
      "scripts/score-regression.sh", "tests/test-orchestrator.sh", "tests/test-regression.sh"], META),
    ("leancode", "multica-ai/andrej-karpathy-skills", "2c606141936f1eeef17fa3043a72095b4765b9c2",
     ["CLAUDE.md"], META),
    ("ui-craft", "jakubkrehel/make-interfaces-feel-better", "35545ea1512ad59fa463e6b1f95ca9c052981fe6",
     ["skills/make-interfaces-feel-better"], META),
    ("ui-craft", "pbakaus/impeccable", "989c484c091d26f10fa102767eefc0da2e62ec67",
     ["skill/reference", "crates/foundation/src/registry.rs"], r"impeccable at\s+([0-9a-f]{40})"),
    ("ui-craft", "Nutlope/hallmark", "7ec868225c6caa040558c321ee0fefa0e73f83a8",
     ["skills/hallmark/references", "skills/hallmark/scripts/sloplint.mjs"], r"hallmark at\s+([0-9a-f]{40})"),
]

def git(d, *a, check=True):
    r = subprocess.run(["git", "-C", d, *a], capture_output=True, text=True)
    if check and r.returncode: sys.exit(f"git {' '.join(a)} in {d}: {r.stderr.strip()}")
    return r

def repo_dir(repo, shas):
    d = os.path.join(CACHE, repo.replace("/", "_"))
    if not os.path.isdir(d):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout",
                        f"https://github.com/{repo}", d], check=True)
    for s in shas:
        if git(d, "cat-file", "-e", f"{s}^{{commit}}", check=False).returncode:
            git(d, "fetch", "-q", "origin", s)
    return d

attribution = open("ATTRIBUTION.md").read()
files = lines = unattributed = 0
for skill, repo, target, paths, rx in SOURCES:
    m = re.search(rx, open(f"skills/{skill}/SKILL.md").read())
    if not m: sys.exit(f"{skill}: no pin for {repo}")
    pin = m.group(1)
    if pin not in attribution:
        unattributed += 1
        print(f"UNATTRIBUTED {skill} {repo}@{pin}")
    d = repo_dir(repo, [pin, target])
    names = git(d, "diff", "--name-status", pin, target, "--", *paths).stdout.split("\n")
    names = [n for n in names if n]
    for n in names: print(f"PENDING {skill} {repo} {n}")
    for row in git(d, "diff", "--numstat", pin, target, "--", *paths).stdout.splitlines():
        a, r, _ = row.split("\t", 2)
        lines += (int(a) if a != "-" else 0) + (int(r) if r != "-" else 0)
    files += len(names)

print(f"METRIC pending_upstream_files={files}")
print(f"METRIC pending_upstream_lines={lines}")
print(f"METRIC unattributed_pins={unattributed}")
if unattributed: sys.exit("every recorded pin must appear in ATTRIBUTION.md")
EOF

# Guard: no new validator issues (baseline: 1 pre-existing ui-craft description-lock issue).
out=$("$PY" scripts/validate_skills.py 2>&1 || true)
issues=$(printf '%s\n' "$out" | sed -n 's/^validation failed: \([0-9]*\) issue.*/\1/p')
issues=${issues:-0}
echo "METRIC validator_issues=$issues"
if [ "$issues" -gt 1 ]; then printf '%s\n' "$out" | grep -v '^warning:' >&2; exit 1; fi
