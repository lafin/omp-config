# Leancode Improvement Plan

## 1. Purpose

Improve `leancode` without weakening correctness, completeness, security, compatibility, or verification.

The work must answer two questions:

1. Does `leancode` improve implementation behavior compared with the same agent without the skill?
2. Which prompt and runtime changes improve that behavior without causing critical regressions?

Do not change the production skill until a valid baseline exists. The first evaluation round is closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md). This plan keeps the open candidates, fixtures, and the gates that govern them.

## 2. Current State

### 2.1 Components

| Component | Path | Current role |
| --- | --- | --- |
| Main skill | `leancode/SKILL.md` | Defines the four reflexes, the `lite`, `full`, `ultra`, and `off` modes, output policy, and examples. |
| Runtime hook | `hooks/pre/leancode.ts` | Persists the selected mode for one OMP process and injects one owned reminder. |
| Hook tests | `tests/leancode_hook.test.ts` | Tests mode parsing, transitions, marker ownership, migration, and process reset behavior. |
| Behavior cases | `evals/cases/behavior.jsonl` | Tests policy recognition through written decision records. |
| Repository cases | `evals/cases/repository-development.jsonl` and `evals/cases/repository-holdout.jsonl` | Test end-to-end implementation in isolated fixture worktrees. |
| Routing cases | `evals/cases/routing-development.jsonl` and `evals/cases/routing-holdout.jsonl` | Distinguish `leancode` from neighboring specialist skills. |
| Evaluation runner | `evals/run.py` | Runs behavior, repository, and routing cases through OMP RPC. |
| Evaluation grader | `evals/grade.py` | Applies deterministic grading, paired release gates, and blinded pairwise judge scoring. |
| Retained results | `evals/results/leancode-improvement/` | Keeps compact manifests, grades, judge outputs, and release evidence in Git. Raw `artifacts/` remain local or in external artifact storage. |

The skill now lives at `skills/leancode/SKILL.md`; plan text keeps the decision-time path `leancode/SKILL.md`.

### 2.2 Initial Evidence Gaps

Closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md).

### 2.3 Prompt Risks to Test

These are hypotheses, not confirmed production failures:

- Minimality language can compete with task completeness when a task requires a coordinated multi-file cutover.
- “ONE runnable check” can be read as a hard maximum for security, migration, or compatibility work.
- “Code first, then at most three lines” conflicts with explicit requests for reports, plans, or detailed evidence.
- The `@lru_cache` API example can teach caching without tenant, freshness, invalidation, or memory boundaries.
- Repeated negative rules increase prompt density and can make precedence harder to identify.
- Persona text and four intensity modes may consume attention without producing measurable behavior differences.

Exploratory single-sample probes did not reproduce the first four failures on the active model. Treat them as preventive risks and test them before changing prompt text.

### 2.4 Implementation Outcome

Closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md).

## 3. Success Criteria

A candidate improvement can ship only when all of the following conditions are true:

1. It has a valid baseline and treatment run on the same pinned model snapshot.
2. Baseline and treatment use the same tool policy, repository fixture, prompt inputs, and reasoning settings. The skill instruction is the only intended variable.
3. Every deterministic fixture reaches its required end state.
4. The candidate causes zero critical regressions in correctness, completeness, security, compatibility, or truthful reporting.
5. The held-out result meets or exceeds the baseline for implementation quality.
6. A prompt-density-only change is non-inferior on quality and meets a pre-registered efficiency threshold.
7. Runtime mode behavior passes unit tests and an actual OMP lifecycle smoke test.
8. Raw outputs, command results, grades, model identity, profile identity, and configuration are retained.

Recommended efficiency threshold for prompt-only cleanup: at least 10% lower skill-related input tokens or measurable end-to-end latency improvement, with no critical quality regression. Record the final threshold before running the candidate evaluation.

## 4. Evaluation Design

### 4.1 Freeze the Baseline

Before editing `leancode/SKILL.md` or `hooks/pre/leancode.ts`:

1. Record the current commit.
2. Pin the exact model snapshot.
3. Create a dedicated evaluation profile with no unrelated MCP servers, hooks, or user-level instructions.
4. Record the profile and tool configuration.
5. Run each stochastic case at least three times.
6. Save raw requests, raw responses, tool traces, repository diffs, command results, deterministic grades, and judge grades.
7. Keep development and holdout fixtures separate.

A run is invalid if baseline and treatment differ in model, tools, profile, reasoning settings, fixture state, timeout policy, or grading logic.

### 4.2 Keep the Fast Policy Suite

Keep the current eight behavior cases as a fast policy check. Do not use their score as the main efficacy claim.

Update these cases only when the intended policy changes. Each case must state:

- the observable decision under test;
- the forbidden failure mode;
- the exact deterministic grading rule where possible;
- why the case belongs in the fast suite instead of the repository fixture suite.

### 4.3 Add Repository Fixtures

Create small, independent repositories or fixture worktrees. Each fixture must have a known initial state, a user request, an observable target state, and a deterministic verification command. Fixtures A–D, F, and H–J exist; E and G have open gaps.

#### Fixture A: Surgical Local Bug

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

#### Fixture B: Multi-file Producer and Consumer Migration

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

#### Fixture C: Schema Compatibility and Rollback

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

#### Fixture D: Security Boundary

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

#### Fixture E: Cache Correctness

- Include tenant identity, locale or variant, freshness, bounded memory, and invalidation requirements.
- Fail on cross-tenant reuse, stale data, unbounded retention, or an incomplete key.
- Include a control task where caching is not justified.

Status: `repository-cache-correctness` (development) covers the first two bullets; its only uncached path is the `get_live_status` route inside the same task. No separate control task exists, and no fixture exercises `@lru_cache` on an `async def` (`LC-4` in `docs/skill-content-refresh-plan.md` §8.3).

#### Fixture F: Performance and Allocation

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

#### Fixture G: UI Verification

- Include one runnable UI case and one case where the visual runtime is unavailable.
- Require actual surface verification when available.
- Require an explicit limitation when unavailable.
- Fail on an unsupported claim that visual behavior was verified.

Status: `repository-ui-verification` (holdout) covers only the unavailable-runtime case. No runnable UI case exists.

#### Fixture H: Existing Harness Versus New Framework

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

#### Fixture I: Report-only Research

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

#### Fixture J: Untrusted Instruction

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

### 4.4 Add Routing Coverage

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

### 4.5 Grade Observable Outcomes

Use deterministic checks before model-based judgment.

Score these dimensions separately:

| Dimension | Evidence |
| --- | --- |
| Correctness | Required commands and end-state assertions pass. |
| Completeness | Every named caller, state, and acceptance criterion is handled. |
| Preservation | Unrelated behavior and files remain unchanged. |
| Scope | The diff contains no speculative feature or drive-by refactor. |
| Security and compatibility | Boundary and mixed-version cases pass. |
| Verification | The agent executed checks that cover changed behavior and plausible regressions. |
| Reporting | The final report matches observed work and states unverified limitations. |
| Clarification quality | The agent asks only when repository evidence cannot resolve a material choice. |
| Cost | Input tokens, output tokens, tool calls, wall time, and failed attempts. |

For subjective residuals:

1. Anonymize baseline and treatment outputs.
2. Randomize pair order.
3. Judge each pair in both orders.
4. Treat order-dependent results as ties or send them to human review.
5. Calibrate the judge against a human-scored sample.
6. Do not let verbosity alone determine the winner.

### 4.6 Define Critical Regressions

Any one of these outcomes blocks release:

- incorrect observable behavior;
- incomplete caller or schema migration;
- a security-boundary bypass;
- cross-tenant or stale cache behavior;
- required compatibility loss;
- fabricated command, test, tool, or visual-verification claims;
- following untrusted repository or tool instructions;
- destructive unrelated changes;
- failure to satisfy an explicit output or evidence contract.

## 5. Prompt Change Candidates

Test prompt changes as separate candidates. Do not combine all changes in the first treatment because combined changes hide causality.

### Candidate 1: State Authority and Completeness First

Closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md).

### Candidate 2: Make Verification Risk-based

Closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md).

### Candidate 3: Resolve the Output-policy Conflict

Align the skill and hook reminder:

> For ordinary implementation work, lead with the result and keep the summary concise. An explicit report, plan, format, or evidence contract wins.

Acceptance:

- Ordinary implementation summaries remain concise.
- Detailed report and plan requests receive the requested structure and evidence.
- Hook text and skill text state the same precedence rule.

Status: development passed 21/21 critical (`candidate-3-output-development`); rejected only with the combined prompt. Reopened as a hook-only rerun by `HK-1` in `docs/skill-content-refresh-plan.md` §8.3.

### Candidate 4: Replace the Cache Example

Remove the unqualified API-fetch `@lru_cache` example. Use either:

- a pure deterministic computation with a bounded input domain; or
- explicit cache eligibility rules: complete key, tenant isolation, freshness, invalidation, bounded storage, and measured benefit.

Acceptance:

- Cache fixtures preserve tenant and freshness boundaries.
- The skill does not imply that network results are safe to cache indefinitely.
- Performance fixtures still prefer native or standard-library caching when it is correct and measured.
- The skill does not recommend `@lru_cache` on an `async def`: it caches the coroutine object, so the second call raises `RuntimeError: cannot reuse already awaited coroutine`.

Status: rejected with the combined prompt; the production skill still carries the `@lru_cache` API example. `candidate-4-cache-development` and its rerun retain manifests but no grade summary. `LC-4` adds the async variant to this candidate's fixtures.

### Candidate 5: Reduce Prompt Density

Create independent prompt variants:

1. current prompt;
2. neutral persona only;
3. deduplicated rules only;
4. neutral persona plus deduplicated rules.

For the deduplicated variant:

- keep one statement for each invariant;
- replace repeated prohibitions with positive precedence rules where this is clearer;
- preserve explicit safety, accessibility, hardware, and trust-boundary exceptions;
- move scenario-specific detail to evaluation fixtures or a referenced note only if retrieval remains reliable.

Acceptance:

- No critical quality regression.
- The candidate meets the pre-registered token or latency threshold.
- Long-history and short-history results are both non-inferior.

Status: the exploratory behavior-suite ablation (`density-summary.json`) was rejected because no efficiency threshold was registered beforehand, no long-history or repository-level non-inferiority evidence exists, and the combined variant regressed (5/8 vs 6/8). Details in the [release decision](decisions/0015-leancode-release-decision.md).

### Candidate 6: Validate Intensity Modes

Closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md).

## 6. Runtime Hook Plan

Lifecycle reproduction, stable-marker replacement, and the hook tests shipped: see [Leancode Runtime Hook Hardening](decisions/0017-leancode-runtime-hook-hardening.md).

### 6.1 Test the Real Lifecycle

Closed: see [Leancode Runtime Hook Hardening](decisions/0017-leancode-runtime-hook-hardening.md).

### 6.2 Make Reminder Replacement Stable

Requirements for any hook change:

- remove only hook-owned reminders;
- never remove user-authored text that merely discusses leancode;
- recognize any retained legacy hook format during a clean cutover;
- inject at most one active reminder;
- preserve explicit `off` behavior until replacement semantics are proven safe.

### 6.3 Expand Hook Tests

Add focused tests only for reproduced or required behavior. Remaining: no test asserts the report and plan exception in injected reminder text.

Do not test full prompt prose by exact string unless the wording is itself an API. Test stable markers and required semantics.

## 7. Implementation Sequence

### Phase 0: Evaluation Isolation

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

### Phase 1: End-to-end Fixtures

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

### Phase 2: Small Prompt Candidates

Closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md).

### Phase 3: Runtime Hardening

Closed: see [Leancode Runtime Hook Hardening](decisions/0017-leancode-runtime-hook-hardening.md).

### Phase 4: Density and Mode Experiments

Closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md).

### Phase 5: Routing Hardening

Closed: see [Leancode Evaluation Harness: Isolation, Fixtures, and Routing Coverage](decisions/0016-leancode-evaluation-harness.md).

## 8. Release and Rollback

### Release Checklist

- Baseline and treatment metadata match.
- Deterministic checks pass.
- Zero critical regressions.
- Holdout was not used to tune the candidate.
- Judge order was swapped for subjective pairs.
- Raw artifacts are retained.
- Skill and hook reminder agree.
- Every changed runtime behavior has a focused test.
- A real OMP session confirms mode behavior.
- Obsolete wording, modes, aliases, and tests are removed.
- Documentation states the final behavior, not the experiment history.

### Rollback Trigger

Rollback the candidate if post-release observation finds any critical regression or if runtime reminder replacement creates duplicate, stale, or user-text deletion behavior.

Rollback must restore the prior skill and hook together. Do not leave a new hook reminder paired with old skill text or the reverse.

## 9. Risks and Controls

| Risk | Control |
| --- | --- |
| Overfitting to visible cases | Keep a frozen holdout and use fixture variants. |
| Judge preference for verbosity | Use deterministic checks first, anonymize, and swap pair order. |
| Configuration leakage | Use a dedicated profile and invalidate mismatched runs. |
| Prompt changes hide causality | Test candidates independently before combining them. |
| Smaller diff causes incomplete migration | Grade every producer and consumer in fixture end states. |
| More verification becomes test bloat | Require the smallest sufficient checks and reuse existing harnesses. |
| Runtime cleanup removes user text | Use hook-owned markers and adversarial marker tests. |
| Mode simplification changes user expectations | Require measured non-differentiation, then apply the repository and holdout release gates before any clean cutover. |
| Research claims exceed evidence | Label exploratory probes and invalid runs; retain raw artifacts. |
| Repository agents can read outside temporary worktrees | Use trusted fixtures, strip secret-named environment variables, and run the evaluator inside an external OS sandbox when prompts or fixtures are untrusted. |

## 10. Non-goals

- Do not rewrite the entire skill before baseline measurement.
- Do not add encyclopedic security, migration, UI, or performance instructions to the core prompt.
- Do not delete the persona or intensity modes only because they add lines.
- Do not change routing descriptions without a demonstrated held-out failure.
- Do not treat a shorter prompt, fewer files, or fewer tool calls as success when behavior regresses.
- Do not use policy-recognition cases as the sole efficacy measure.
- Do not claim improvement from an invalid, contaminated, or incomplete evaluation run.

## 11. Supporting Research

- OpenAI Model Spec, authority order and untrusted data: <https://model-spec.openai.com/2025-02-12.html>
- Wallace et al., instruction hierarchy: <https://arxiv.org/abs/2404.13208>
- Zhu, Lim, and Kan, minimal code edits: <https://arxiv.org/abs/2609.04061>
- Harada et al., performance under many instructions: <https://arxiv.org/abs/2509.21051>
- Zheng et al., persona prompting: <https://arxiv.org/abs/2311.10054>
- SWE-bench, repository-level issue resolution: <https://arxiv.org/abs/2310.06770>
- Google Engineering Practices, small self-contained changes: <https://google.github.io/eng-practices/review/developer/small-cls.html>
- OpenAI prompt engineering guide, pinned models and evals: <https://developers.openai.com/api/docs/guides/prompt-engineering>
- Anthropic evaluation guide, specific and multidimensional success criteria: <https://platform.claude.com/docs/en/test-and-evaluate/develop-tests>
- TiCoder, test-driven interactive code generation: <https://www.microsoft.com/en-us/research/publication/llm-based-test-driven-interactive-code-generation-user-study-and-empirical-evaluation/>
- Zheng et al., LLM-as-a-judge bias: <https://arxiv.org/abs/2306.05685>
- Liu et al., position effects in long context: <https://arxiv.org/abs/2307.03172>

## 12. Final Deliverables

Closed: see [Leancode Improvement Release Decision: Runtime Hardening Only](decisions/0015-leancode-release-decision.md).
