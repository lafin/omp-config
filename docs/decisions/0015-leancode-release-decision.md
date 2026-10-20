# Leancode Improvement Release Decision: Runtime Hardening Only

- **Status:** Accepted
- **Date:** not stated (run manifests: 2026-09-10 to 2026-09-11)
- **Source:** [Leancode Improvement Plan §2.4 Implementation Outcome](../leancode-improvement-plan.md#24-implementation-outcome); also [§1](../leancode-improvement-plan.md#1-purpose), [§2.2](../leancode-improvement-plan.md#22-initial-evidence-gaps), [Candidate 1](../leancode-improvement-plan.md#candidate-1-state-authority-and-completeness-first), [Candidate 2](../leancode-improvement-plan.md#candidate-2-make-verification-risk-based), [Candidate 6](../leancode-improvement-plan.md#candidate-6-validate-intensity-modes), [Phase 2](../leancode-improvement-plan.md#phase-2-small-prompt-candidates), [Phase 4](../leancode-improvement-plan.md#phase-4-density-and-mode-experiments), [§12](../leancode-improvement-plan.md#12-final-deliverables)

## Decision

Paths are as recorded at decision time: `leancode/SKILL.md` is now `skills/leancode/SKILL.md`; `.omp/hooks/pre/leancode.ts` is now `hooks/pre/leancode.ts`.

### Initial state (plan §1, §2.2)

Before this work, evidence showed policy coverage and mode plumbing, but it did not show end-to-end implementation quality. The repository did not contain a valid baseline-versus-treatment result for implementation tasks.

The initial behavior suite had eight decision-record cases and no repository edits or tool use. It could detect policy misunderstandings, but it could not prove correct, complete, minimal implementation.

The initial routing suites did not cover the base `leancode` skill against all neighboring skills. The hook suite tested the module in isolation and did not prove behavior across an actual OMP reload or process restart. The only retained result was one mode-smoke artifact without model outputs, grades, baseline, treatment, or holdout evidence.

### Outcome (plan §2.4)

The evaluation rejected every production prompt change. The unmodified repository-development baseline passed 21 of 21 attempts. The combined prompt passed 20 of 21 development attempts and 6 of 9 holdout attempts. The corresponding baseline holdout passed 7 of 9 attempts. The merge gate therefore failed and contains no efficacy claim.

The density variants did not meet the quality and efficiency gate. The mode experiment suggested collapsing `lite` and `ultra`, but the exact collapsed production candidate passed only 6 of 9 holdout attempts. The release gate overrides that exploratory recommendation. The production skill retains its original prompt and all four modes.

The accepted production change is limited to runtime hardening in `.omp/hooks/pre/leancode.ts`: generated reminders now have agent attribution, replacement uses a stable marker for owned messages, and unattributed migration removes only exact known legacy reminders. Focused hook tests and `mode-smoke-production-v3.json` cover all four modes, reload persistence, process reset, model identity, and user marker preservation. See [Leancode Runtime Hook Hardening](0017-leancode-runtime-hook-hardening.md).

Routing passed 78 of 78 development attempts and 78 of 78 holdout attempts. No skill-description change was required. The final decision makes no `leancode` efficacy claim.

All decision-time holdout manifests bind the same frozen case-file hash, `aa649030dcd049ee2ddbb54d0a7b62a90f1448f4e63fd0ceac284d10f85a8049`. After all decision-time holdout runs, the source suite corrected a visual-claim regular expression for future runs. Its new hash is `752de8a3c6840920ff08863e08ddd55680c65a912f47e779a62de2f4f80a8b6f`; the decision runs were not regraded or used to tune the frozen holdout.

Gate details from `combined-release-gate.json`: development critical regression `repository-security-boundary:2`, holdout critical regression `repository-untrusted-instruction:2`; tokens rose from 1,019,141 to 2,120,933 (development) and 426,918 to 904,657 (holdout), and tool events rose from 159 to 184 and 73 to 76.

Rejection reasons recorded in `release-decision.json`:

- Combined prompt Candidates 1–4: failed development, holdout, critical-regression, and cost gates.
- Density variants: no variant established repository-level non-inferiority and a preregistered efficiency benefit.
- Mode collapse: exploratory modes were not distinct, but the exact collapsed production candidate regressed holdout from 7/9 to 6/9.

Recorded evaluation limits: repository attempts use temporary worktrees but no operating-system read sandbox; run untrusted prompts or fixtures only inside an external sandbox without host credentials; historical run manifests bind the evaluator version used at capture, and the hardened evaluator does not rewrite those immutable artifacts; raw artifact directories are excluded from Git because individual captures exceed GitHub's file-size limit.

### Rejected Candidate 1: State Authority and Completeness First

Add near the start of `leancode/SKILL.md`:

> Leancode is a default optimization policy. Explicit task requirements and higher-authority constraints win. First identify and satisfy the complete observable contract. Then minimize.

Replace raw “shortest diff” language with:

> Prefer the smallest coherent change. Use line and file count only as tie-breakers after correctness, security, compatibility, required performance and operability, maintainability, and verification.

Acceptance:

- Multi-file migration fixtures complete every required caller change.
- Surgical fixtures still reject unrelated edits.
- The candidate has no increase in critical failures.

Result: development rerun (`candidate-1-authority-development-rerun`) passed 21/21 critical; rejected with the combined prompt.

### Rejected Candidate 2: Make Verification Risk-based

Replace “ONE runnable check” as a universal instruction with:

> For implementation work, run the smallest sufficient set of consumer-observable checks for changed behavior and plausible regressions. One focused check is often sufficient, but it is not a cap. Reuse existing harnesses and fixtures.

State that report-only research does not require an implementation check.

Acceptance:

- Simple local changes usually use one focused check.
- Security, migration, and compatibility tasks run all checks needed to cover their distinct risks.
- The agent does not add a new framework when an existing harness is sufficient.

Result: development run (`candidate-2-verification-development`) passed 21/21 critical; rejected with the combined prompt.

### Rejected Candidate 6: Validate Intensity Modes

Compare every proposed active mode on the same task distribution.

Measure:

- task quality by dimension;
- prompt tokens;
- latency;
- mode selection and persistence errors;
- whether each mode changes observable implementation behavior.

If two modes do not produce a stable, useful difference, collapse them. Keep `off` as an explicit state unless runtime evidence proves that removing its marker cannot cause stale skill activation.

Acceptance:

- Every retained mode has a documented use case and a measurable behavior difference.
- Mode transitions remain deterministic.
- Removed modes have no retained documentation, parser path, test, or stale reminder.

Result (`mode-summary.json`; tasks `framework` and `cache`, 3 attempts per task and mode, `openai-codex/gpt-5.6-sol`, profile `skill-eval-isolated`, thinking off, no tools): `full` and `ultra` produced the same decision in all six matched trials; `lite` matched in five of six, was unstable on the remaining trial, and used more tokens and latency. The exploratory recommendation was to collapse `lite` and `ultra` into `full` and keep `off`. The exact collapsed production candidate regressed holdout from 7/9 to 6/9, so all four modes were retained.

### Executed Phase 2: Small Prompt Candidates

Files: `leancode/SKILL.md`; `hooks/pre/leancode.ts` only for reminder alignment; relevant behavior cases.

Work:

1. Test Candidate 1 independently.
2. Test Candidate 2 independently.
3. Test Candidate 3 independently.
4. Test Candidate 4 independently.
5. Select only candidates that pass the release gate.
6. Test the selected combined prompt against the untouched baseline and holdout.

Exit gate: the combined candidate has zero critical regressions and improves or preserves every required quality dimension. Result: failed (see Outcome).

### Executed Phase 4: Density and Mode Experiments

Files: experimental skill variants outside the production load path; evaluation manifests and results.

Work:

1. Run the persona and deduplication ablation matrix.
2. Run mode differentiation experiments.
3. Measure quality, tokens, latency, and tool use.
4. Adopt only changes that meet pre-registered gates.
5. Remove obsolete production text, modes, tests, and documentation in the same cutover.

Exit gate: every retained prompt section and mode has measured value or a stated safety function. Result: no change adopted.

Density run (`density-summary.json`; exploratory policy ablation on `evals/cases/behavior.jsonl`, 1 attempt per variant, `openai-codex/gpt-5.6-sol`, profile `skill-eval-isolated`, thinking off, no tools; not repository-level efficacy evidence). No efficiency threshold was registered before these runs, so efficiency cannot justify adoption.

| Variant | Deterministic passed | Tokens | Elapsed (s) |
| --- | --- | --- | --- |
| current | 6/8 | 42027 | 138.299 |
| neutral persona | 7/8 | 41623 | 96.555 |
| deduplicated rules | 6/8 | 40068 | 88.122 |
| neutral persona + deduplicated rules | 5/8 | 39346 | 82.718 |

Decision: reject. The combined neutral-and-deduplicated variant regressed deterministic quality; the other variants lack a pre-registered efficiency threshold, long-history evidence, and repository-level non-inferiority evidence. Candidate 5 stays open in the plan.

### Final deliverables (plan §12)

The improvement project is complete only when it produces:

1. a valid baseline artifact;
2. deterministic repository fixtures with development and holdout sets;
3. per-dimension baseline and treatment results;
4. the accepted `leancode/SKILL.md` change, if evidence supports one;
5. an aligned hook reminder and lifecycle behavior;
6. focused hook and routing coverage;
7. a real-session smoke result;
8. a release decision with explicit accepted and rejected candidates;
9. retained local or external raw evidence sufficient to reproduce the decision, with compact integrity bindings kept in Git.

All nine were produced; item 4 produced no change because evidence supported none.

## Evidence

- [`release-decision.json`](../../evals/results/leancode-improvement/release-decision.json): decision `ship_runtime_hardening_only`, `efficacy_claim: null`, skill sha256 `4eac28a7cb610f6c25f94eedd345e1cdd329eee2262587ff8ee8cff3eb490a9f` (matches pre-change source), hook sha256 `2c38dd3e105f406ab80d390a8b24ac3d9990ab7e339a60d959f07e4a85ec9b0f`; verification: `bun test tests/leancode_hook.test.ts` 9 passed, `python3 -m unittest discover -s tests` 38 passed, `python3 scripts/validate_skills.py` passed, release evidence audit 246 complete local raw artifacts and routing 156/156
- [`combined-release-gate.json`](../../evals/results/leancode-improvement/combined-release-gate.json)
- [`density-summary.json`](../../evals/results/leancode-improvement/density-summary.json)
- [`mode-summary.json`](../../evals/results/leancode-improvement/mode-summary.json), [`mode-experiment-distribution.json`](../../evals/results/leancode-improvement/mode-experiment-distribution.json)
- [`repository-final-holdout-treatment/grade-summary.json`](../../evals/results/leancode-improvement/repository-final-holdout-treatment/grade-summary.json) (6/9), [`repository-holdout-baseline/grade-summary.json`](../../evals/results/leancode-improvement/repository-holdout-baseline/grade-summary.json) (7/9), [`repository-development-baseline/grade-summary.json`](../../evals/results/leancode-improvement/repository-development-baseline/grade-summary.json) (21/21)
- [`routing-development-final/grade-summary.json`](../../evals/results/leancode-improvement/routing-development-final/grade-summary.json), [`routing-holdout-final/grade-summary.json`](../../evals/results/leancode-improvement/routing-holdout-final/grade-summary.json) (78/78 each)
- `evals/results/leancode-improvement/candidate-{1,2,3}-*-judge/`, `combined-{development,holdout}-judge/` (judge output is optional evidence and cannot replace deterministic paired gates); `candidate-4-cache-development{,-rerun}/` retain manifests without a grade summary
- [`rollback.json`](../../evals/results/leancode-improvement/rollback.json): restore source commit `a2384f71dc317446706c66799d26e15e6b18836a` for `leancode/SKILL.md` and `.omp/hooks/pre/leancode.ts` together
