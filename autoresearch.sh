#!/usr/bin/env bash
# Skill-uplift benchmark (offline, deterministic: reads committed eval results only).
# Primary: mean over skills of (treatment - baseline) critical pass rate on a FIXED set of
# canonical holdout files (frozen 2026-11-09), so adding cases cannot move it; only skill
# edits re-captured against these files can. Guards: both validators must pass.
set -euo pipefail
cd "$(dirname "$0")"
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
"$PY" scripts/validate_skills.py >/dev/null
"$PY" evals/validate.py >/dev/null

"$PY" - <<'EOF'
import json, glob, os, collections
suites = json.load(open("evals/suites.json"))
FIXED = {"catalog-behavior-holdout-v3", "depth-behavior-holdout", "depth10-behavior-holdout",
         "depth11-behavior-holdout", "depth12-behavior-holdout", "depth2-behavior-holdout-v3",
         "depth3-behavior-holdout-v5", "depth4-behavior-holdout-v4", "depth5-behavior-holdout-v2",
         "depth6-behavior-holdout", "depth7-behavior-holdout", "depth8-behavior-holdout",
         "depth9-behavior-holdout", "leancode-merge-behavior-holdout",
         "pilot-api-and-interface-design-behavior-holdout",
         "pilot-security-review-behavior-holdout-v2",
         "pilot-source-driven-development-behavior-holdout-v2", "refresh-behavior-holdout-v3",
         "security-review-severity-holdout", "see-behavior-boundary-holdout",
         "see-behavior-holdout-final", "ui-craft-behavior-holdout-v2"}
files = {f["path"]: f["frozen_sha256"] for f in suites["case_files"]
         if f["kind"] == "behavior" and f["split"] == "holdout" and f["status"] == "canonical"
         and os.path.basename(f["path"])[:-6] in FIXED}
target = {}
for p in files:
    for line in open(p):
        if line.strip():
            c = json.loads(line); target[c["id"]] = c["target_skill"]
# Per (case files, condition): pool every run sharing the newest run's evaluated catalog,
# model and grader; older pins, models and graders are superseded, never mixed in.
groups = collections.defaultdict(list)
for m in glob.glob("evals/results/**/manifest.json", recursive=True):
    man = json.load(open(m))
    matched = tuple(sorted(cf["path"] for cf in man.get("case_files", [])
                           if cf.get("path") in files and cf.get("sha256") == files[cf["path"]]))
    if not matched or not os.path.exists(os.path.join(os.path.dirname(m), "grades.jsonl")):
        continue
    version = ((man.get("evaluated_catalog") or {}).get("revision"), man.get("model_requested"),
               (man.get("evaluator_files") or {}).get("grade.py"))
    groups[(matched, man["condition"])].append((man.get("created_at", ""), version, m))
selected = []
for rs in groups.values():
    newest = max(rs)[1]
    selected += [m for _, v, m in rs if v == newest]
runs = collections.defaultdict(dict)
for m in selected:
    for line in open(os.path.join(os.path.dirname(m), "grades.jsonl")):
        r = json.loads(line)
        if r["case_id"] in target:
            runs[(r["condition"], r["case_id"])][(m, r["attempt"])] = r["critical_passed"]
skills = sorted(d for d in os.listdir("skills") if os.path.exists(f"skills/{d}/SKILL.md"))
attempts = collections.Counter(); uplift = collections.Counter()
for (cond, cid), res in runs.items():
    if cond != "treatment": continue
    s = target[cid]; attempts[s] += len(res)
    base = runs.get(("baseline", cid), {})
    if all(res.values()) and base and not all(base.values()):
        uplift[s] += 1
deep = [s for s in skills if attempts[s] >= 18 and uplift[s] >= 1]
strong = [s for s in skills if attempts[s] >= 18 and uplift[s] >= 2]
# Paired pass rates over cases captured in both conditions.
paired = [c for (cond, c) in runs if cond == "treatment" and ("baseline", c) in runs]
rate = lambda cond: 100 * sum(sum(runs[(cond, c)].values()) for c in paired) / sum(len(runs[(cond, c)]) for c in paired)
print(f"METRIC uplift_pp={rate('treatment') - rate('baseline'):.1f}")
print(f"METRIC treatment_pass_pct={rate('treatment'):.1f}")
print(f"METRIC baseline_pass_pct={rate('baseline'):.1f}")
per_skill = {}
for s in skills:
    cs = [c for c in paired if target[c] == s]
    if cs:
        r = lambda cond: 100 * sum(sum(runs[(cond, c)].values()) for c in cs) / sum(len(runs[(cond, c)]) for c in cs)
        per_skill[s] = r("treatment") - r("baseline")
    print(f"SKILL {s} holdout_attempts={attempts[s]} uplift_cases={uplift[s]} uplift_pp={per_skill.get(s, 0):.1f}")
print(f"METRIC mean_skill_uplift_pp={sum(per_skill.values()) / len(per_skill):.1f}")
print(f"METRIC min_skill_uplift_pp={min(per_skill.values()):.1f}")
print(f"METRIC strong_skills={len(strong)}")
print(f"METRIC deep_skills={len(deep)}")
print(f"METRIC holdout_attempts={sum(attempts[s] for s in skills)}")
print(f"METRIC skills_with_uplift={sum(1 for s in skills if uplift[s])}")
print(f"METRIC skills_total={len(skills)}")
EOF
