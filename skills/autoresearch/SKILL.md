---
name: autoresearch
description: >
  Bounded modify, verify, keep-or-revert loops toward a mechanical metric,
  plus the subcommands built on them: plan, debug, fix, security, ship,
  scenario, predict, learn, reason, probe, evals, improve, regression. One
  change per iteration, committed, verified by a command that prints a number
  or error count, reverted if worse, logged to a results TSV. Use when the
  user says "autoresearch", "iterate until the tests pass", "optimize X
  against this command", "fix errors one by one until zero", "keep trying
  until the metric improves", "run a regression gate", or "/autoresearch".
  Not for a one-shot security review (security-review) or over-engineering
  review (leancode-review), designing evals or rubrics (evaluation), or
  optimizing an agent's own harness or prompts (self-improvement-loops,
  harness-engineering).
license: MIT
metadata:
  upstream: "uditgoenka/autoresearch"
  upstream_commit: "050e30dc4ba0974b03f2873111b9901ec3211390"
  upstream_path: ".claude/skills/autoresearch/SKILL.md"
  adaptation: modified
  license_notice: LICENSE-autoresearch
---

# Autoresearch

Goal-directed iteration against a mechanical signal. The unit of work is a bounded loop: make one change, commit it, run a verify command, keep the change if the number improved and the guard still passes, otherwise revert; append a row to the results TSV; repeat until the bound, the goal, or saturation. Git history is the loop's memory.

Invocation: `/autoresearch [<subcommand>] [Goal:|Metric:|Verify:|Scope:|Guard:|Iterations:] ...`. `/skill:autoresearch` loads this skill without the dispatcher.

## Safety invariants

- Never push, publish, or deploy without explicit user approval.
- Bounded by default. Only `Iterations: unlimited` removes the bound.
- One change per iteration; commit before verifying so a revert is one command (`git revert HEAD --no-edit`).
- Verify mechanically: a command whose output is a number or a count. A metric that needs judgment is not a loop metric (see failure modes).
- Revert on regression, guard failure, crash, or an unparseable metric. Never keep a change because it "looks better".
- Screen every Verify, Guard, and Target command before running it (`screen-cmd` below).
- Stay inside `Scope:`. Edits outside it are a defect, not progress.
- Results go to `autoresearch/<subcommand>-<YYMMDD>-<HHMM>/` under the project root. Evals read `*-results.tsv`; chained commands read `handoff.json`.

## Dispatch

| First word of the arguments | Read |
|---|---|
| `plan`, `debug`, `fix`, `security`, `ship`, `scenario`, `predict`, `learn`, `reason`, `probe`, `evals`, `improve`, `regression` | the matching reference in the table below, plus the shared contracts |
| anything else, or nothing | `skill://autoresearch/references/loop.md` (core loop, setup wizard, orchestrator) |

Always read `skill://autoresearch/references/contracts.md` before starting a run: it owns setup and precondition rules, the results TSV, `handoff.json`, orchestrator state, flags, eval checkpoints, chaining, and the active marker.

## Subcommands

| Subcommand | Does | Default iterations | Read when |
|---|---|---|---|
| (none) | Modify → verify → keep or revert against a metric; or orchestrate a plain-language goal | 25 | Bare invocation: [loop](references/loop.md) |
| `plan` | Convert a goal into validated Scope, Metric, Verify, Guard | n/a | The metric or command is not yet known: [plan](references/plan.md) |
| `debug` | Hypothesize, test, falsify bugs | 15 | Hunting an unknown defect: [debug](references/debug.md) |
| `fix` | Reduce errors one by one to zero | 20 | A command shows failures to clear: [fix](references/fix.md) |
| `security` | STRIDE and OWASP audit with red-team personas | 15 | Iterative audit with coverage tracking: [security](references/security.md); checklist: [security-checklist](references/security-checklist.md) |
| `ship` | Eight-phase ship: checklist, dry-run, approved ship, verify | n/a | Shipping a PR, release, deployment, package, or content: [ship](references/ship.md) |
| `scenario` | Edge cases across 12 dimensions | 20 | Exploring a feature's failure space: [scenario](references/scenario.md) |
| `predict` | Persona debate before implementation | n/a | Reviewing a proposed change before building: [predict](references/predict.md); personas: [predict-personas](references/predict-personas.md) |
| `learn` | Scout the codebase, generate docs or a wiki, validate and fix | 10 | Documentation or wiki generation: [learn](references/learn.md) |
| `reason` | Adversarial debate with blind judges until convergence | 8 rounds | A decision with no mechanical metric: [reason](references/reason.md); judge rules: [reason-judge-protocol](references/reason-judge-protocol.md) |
| `probe` | Eight personas interrogate requirements until saturation | 15 rounds | Requirements are vague: [probe](references/probe.md) |
| `improve` | ICP research, improvement discovery, PRDs | 15 | Product research: [improve](references/improve.md) |
| `evals` | Analyze results TSVs: trends, plateaus, regressions | n/a | After or during a run: [evals](references/evals.md) |
| `regression` | Baseline vs candidate stability gate: STABLE or UNSTABLE | n/a | Before pushing a change: [regression](references/regression.md) |

Overlap with other skills: for a single code review at a trust boundary use `skill://security-review`, not `security`; for over-engineering review of a diff use `skill://leancode-review`; for designing evaluations or rubrics use `skill://evaluation`.

## Workflow

1. Read the contracts and the matching reference.
2. Collect Goal, Scope, Metric, Verify (and Guard) from the arguments; ask once for what is missing (headless runs fail fast, see failure modes).
3. Preconditions: git repo, clean tree, commit-signing check passes, no stale `.active` marker.
4. Screen commands, run the baseline (iteration 0), write the active marker.
5. Loop per the reference; log every iteration.
6. Write `handoff.json`, delete the marker (also on abort), print the summary, run any chain.

### Active marker

`<project>/autoresearch/.active` in the project root holds one line: the run directory relative to the project root. Setup writes it after the baseline; completion and abort delete it. A hook keyed on this file blocks `git push`, `git reset --hard`, `git clean -f`, and `rm -rf` while it exists. Stale-marker rule: if the marker exists at start and its run directory's newest results TSV is more than 30 minutes old (or the directory is gone), refuse to start and offer to delete the marker; if the TSV is fresh, another run is active, so stop. Full lifecycle in the contracts.

### Commit signing check

Before the first iteration run the commit-signing check from the contracts Preconditions block. If it fails (`commit.gpgsign=true` with no available key), stop and ask the user how to proceed. Do not disable signing yourself.

## Exit evidence

A run is complete when: the bound, goal, convergence, or saturation condition was reported; the results TSV has one row per iteration; `handoff.json` exists with a status; the active marker is gone; the summary names the starting and final metric (or findings count) and what was kept. For `fix`, the evidence is the Target command's error count at the end.

## Helper scripts

Paths are relative to this skill directory (the `scripts` directory sits next to this file, never against the caller's working directory). Both helpers use only the Python standard library and do not mutate the repository.

### `orchestrate.py`

- **Status:** Production helper: deterministic routing seam for the orchestrator.
- **Boundary:** Classifies goal text by keyword, routes on a state file, computes Units remaining, detects plateau, and screens command strings with pattern rules. It does not run the predicate, does not prove a command is safe (`screen-cmd` is a heuristic, not a sandbox), and does not judge whether a classification is right; the orchestrator's confirm step does.
- **Run:** From the repository root, `python skills/autoresearch/scripts/orchestrate.py <subcommand> <arg> [options]`; from the skill directory, `python3 scripts/orchestrate.py ...`. Subcommands: `classify "<goal>"`, `next-hop <state.json>`, `units <results.json>`, `plateau <state.json or history.txt> [--window N]` (default 5), `screen-cmd "<command>"`, `verdict <state.json>`, `validate-state <state.json>`, `screen-state-predicate <state.json>`. `--help` lists them. State schema: `references/contracts.md`.
- **Output:** One word on stdout. `classify`: archetype label. `next-hop`: `fix`, `regression`, `debug`, `verify`, `ship`, `DONE`. `units`: a number or `unknown`. `plateau`: `PLATEAU`, `BLOCKED`, or no output while still improving. `screen-cmd` and `screen-state-predicate`: `ok` or `refuse` (the latter also `invalid`). `verdict`: `CONVERGED`, `PLATEAU`, `CEILING`, or `BLOCKED`, then `ship=yes` or `ship=no`. `validate-state`: `valid` or `invalid`.
- **Failure:** Exit 0 is success. `next-hop` and `units`: 2 on a missing or malformed file (message on stderr; `units` also prints `unknown`). `plateau`: 0 plateau, 1 still improving, 3 `BLOCKED` (no computed values, or a window of `unknown`s). `screen-cmd`: 1 on `refuse`. `verdict`: 0 `CONVERGED`, 1 not converged, 2 error. `validate-state` and `screen-state-predicate`: 2 `invalid`. 64 for a usage error. Repair a malformed state file against the contracts; do not route from it.

### `score_regression.py`

- **Status:** Production helper: scoring backend for the `regression` gate.
- **Boundary:** `verdict` reduces the 15-column regression results TSV to STABLE or UNSTABLE using the HARD rule and the weighted SCORE dimensions; it does not run tests or prove the TSV rows are truthful. `rubric` greps the regression reference for required invariants and flags and prints a count; it measures coverage of terms, not quality.
- **Run:** From the repository root, `python skills/autoresearch/scripts/score_regression.py verdict <results.tsv>` or `python skills/autoresearch/scripts/score_regression.py rubric [file]` (default `references/regression.md` next to the script). `REG_THRESHOLD` and the `REG_W_*` weights override the defaults.
- **Output:** `verdict`: stdout lines `VERDICT: STABLE|UNSTABLE|BASELINE_UNAVAILABLE|ERROR`, `score=<n>`, `blocking=<list>`, `dims_ran=<list>`, `dims_unavailable=<list>`; the per-dimension score math goes to stderr. `rubric`: `SCORE: N`.
- **Failure:** `verdict`: exit 0 STABLE, 1 UNSTABLE, 2 error, invalid schema or classification, missing TSV, or `BASELINE_UNAVAILABLE` (no dimension ran; never STABLE). `rubric`: exit 0, `SCORE: 0` if the file is missing. 64 for a usage error. Fix the TSV to the schema in `references/regression.md`.

## Failure modes

- **Non-mechanical metric.** "Cleaner", "better UX", or an LLM's opinion cannot drive keep or revert. Use `plan` to find a proxy number, or use `reason` or `predict` instead of a loop.
- **Verify command that mutates state.** A verify that writes files, hits live services, or leaves the tree dirty corrupts the next iteration and the revert. Make it read-only and idempotent, or refuse it.
- **Dirty tree.** Unrelated uncommitted changes get mixed into experiment commits or lost on revert. Require a clean tree or an explicit user decision to continue.
- **Gaming the metric.** Editing the verify script, the guard, or tests to pass them is a failure; revert and log `discard`. Keep verify and guard outside `Scope:`.
- **Same-signal acceptance.** Optimizing and accepting on one signal overfits; the orchestrator uses a held-out check (see loop).
- **Headless run cannot ask.** A subagent or CI run has nobody to answer setup questions. Setup then requires `Goal:` and `Verify:` (or `Target:` for `fix`) in the arguments and fails fast naming the missing fields; never invent them.
- **Unbounded loops.** Not passing a bound is never a license to run forever; default bounds apply.
- **Stale marker.** A crashed run leaves `<project>/autoresearch/.active`; the guard stays on until it is deleted. Follow the stale-marker rule.
- **Rationalizations.** "One more tweak before logging", "the guard failure is unrelated", "I'll skip the revert, it is nearly better": each produces an unlogged or unverified state. Log, revert, move on.
