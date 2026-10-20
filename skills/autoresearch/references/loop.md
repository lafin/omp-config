# Core loop and orchestrator

Read this for a bare `/autoresearch` invocation (no subcommand word). Shared blocks (setup questions, preconditions, TSV, handoff, flags, eval checkpoints, chain, active marker) live in `skill://autoresearch/references/contracts.md`.

## Dispatch

Parse the invocation arguments in this order:

| Condition | Mode |
|---|---|
| `--classic` flag | **Classic** regardless of goal text |
| `--auto` flag | **Orchestrator** regardless of goal text |
| `Metric:` or `Verify:` present | **Classic**: the metric loop below |
| Free-form natural-language goal, no metric or verify | **Orchestrator**: see Orchestrator below |
| Nothing | **Setup wizard**: ask the setup questions below, then run Classic |

Print a banner on every invocation: `[autoresearch] mode: classic | orchestrator | wizard`.

## Classic loop

### Parse arguments

- `Goal:` — what to improve.
- `Scope:` or `--scope` — file globs the loop may modify.
- `Metric:` — what to measure.
- `Direction:` — `higher_is_better` (default) or `lower_is_better`.
- `Verify:` — shell command that outputs a number.
- `Guard:` — optional safety command that must always pass.
- `Iterations:` or `--iterations` — integer N (default 25), or `unlimited`.
- `--evals`, `--evals-interval N`, `--chain <targets>`.

### Setup (if Goal, Scope, Metric, or Verify is missing)

Ask the user once, batching:

1. Goal: what do you want to improve?
2. Scope: which files? Suggest globs from the project.
3. Metric and Verify: how to measure; a shell command that outputs a number.
4. Guard: a safety command that must always pass (options: test command, build command, skip).

If all are provided inline, skip setup.

### Preconditions and safety screen

Apply the Preconditions and Verify safety screen blocks from the contracts, including the gpgsign dry-run commit check and the stale-marker rule.

### Baseline (iteration 0)

1. Run Verify and extract the numeric metric.
2. Create `autoresearch/loop-<YYMMDD>-<HHMM>/` and write `loop-results.tsv`: the `# metric_direction:` line, the header (common columns, then `timestamp`, `guard_metric`), and the iteration-0 row with status `baseline`, delta `0`.
3. Write the active marker (contracts).

### Iteration loop (1 to N, or unbounded)

1. **Review.** Read the last 10-20 TSV lines and `git log --oneline -20`. After a `keep`, read `git diff HEAD~1` to see what moved the metric. Note what worked, what failed, what is untried.
2. **Modify.** Make ONE focused, atomic change toward the metric, inside `Scope:`.
3. **Commit.** Stage and commit with the prefix `experiment: <description>`. Record the SHA.
4. **Verify.** Run Verify, extract the new metric, compute delta against the previous kept metric. Improvement in the configured direction makes it a keep candidate.
5. **Guard** (if configured). Run Guard. A failure reverts the change regardless of the metric.
6. **Decide.**
   - `keep` — metric improved and guard passed; the commit stays.
   - `discard` — metric worsened or did not improve; `git revert HEAD --no-edit`.
   - `crash` — Verify or Guard failed to run; `git revert HEAD --no-edit`.
   - `no-op` — no change was made this iteration.
   - `hook-blocked` — a git hook blocked the commit.
   - `metric-error` — Verify output was not a valid number; `git revert HEAD --no-edit`.
7. **Log.** Append the TSV row (common columns plus `timestamp`, `guard_metric`).
8. **Eval checkpoint.** With `--evals`, run the checkpoint when `iteration % interval == 0` (contracts).
9. **Bounded check.** When bounded and `iteration >= N`, exit the loop.

### Summary

Print: total iterations, kept and discarded counts, starting metric → final metric, improvement percentage, the top 3 most effective changes.

### Finish

Write `handoff.json` (`source: "loop"`, `findings: []`, `config`: goal, scope, metric, direction, verify), delete the active marker, then run any chain (contracts).

## Orchestrator

Activated by a plain-language goal without `Metric:` or `Verify:`. The deterministic seam is `python3 scripts/orchestrate.py` (path relative to the skill directory); all routing logic lives there. Its subcommands: `classify`, `next-hop`, `units`, `plateau`, `screen-cmd`, `verdict`, `validate-state`, `screen-state-predicate`.

### Goal archetypes

| Archetype | Trigger keywords | Mode | Preset pipeline |
|---|---|---|---|
| `ship-ready` | ship, release, deploy, publish, production-ready, merge | loop | probe, debug, fix, regression, ship |
| `optimize-metric` | improve, optimize, increase, reduce, faster, smaller, coverage, score | loop | plan, (classic loop), holdout-verify, evals |
| `fix-broken` | fix, broken, failing, error, crash, bug, can't run, tests fail | loop | debug, fix, regression |
| `harden` | security, vulnerability, audit, OWASP, CVE, harden, lock down | loop | security, fix, security |
| `build-feature` | build, add, implement, create, new feature, acceptance test | loop | (acceptance-test derive), debug, fix, regression |
| `explore` | understand, explore, investigate, what does, how does, edge cases | loop | probe, scenario, plan |
| `document` | document, wiki, generate docs, explain codebase, write guide | dispatch | learn |
| `what-to-build` | what should I build, ideas, improvements, PRD, roadmap | dispatch | improve |
| `decide-design` | which approach, compare options, design decision, architecture choice | dispatch | reason |

Keyword matching is fuzzy: partial matches and synonyms qualify. When a goal matches several archetypes prefer the more specific one (`fix-broken` over `explore`; `ship-ready` over `fix-broken` when "ship" is explicit). When ambiguous, show the top two candidates in the confirm step and let the user choose. Presets are starting pipelines; the router may skip, repeat, or reorder steps from observed state.

### Two modes

- **Orchestration loop** — the goal has an external mechanical Success predicate: a shell command whose value can be compared across cycles. Used by `ship-ready`, `optimize-metric`, `fix-broken`, `harden`, `build-feature`, `explore`. Progress is objective (Units remaining falls) and the loop ends on convergence or a safety backstop.
- **Single-pass dispatch** — no mechanical predicate (`document`, `what-to-build`, `decide-design`). Route once to `learn`, `improve`, or `reason`, let it self-terminate, then report. No loop, no Plateau counter, no ship gate.

The test: can the orchestrator verify "done" without re-running the subcommand? Yes → loop; no → dispatch.

### Orchestration loop steps

1. **Classify.** `python3 scripts/orchestrate.py classify "<goal>"` prints the archetype label.
2. **Derive predicate.** Reuse `skill://autoresearch/references/plan.md` logic to produce a concrete Success predicate: exact shell command plus expected output. For `optimize-metric`, run the full plan derivation.
3. **Confirm.** Ask the user once, showing archetype, mode, the concrete predicate (command and expected output), and the terminal choice (`stop-at-verified` or `proceed-to-ship`). Misclassification is caught here, not mid-run.
4. **Round-0 dry-run.** Prove the predicate runs and returns a value. Run `screen-cmd` on every derived command. Print the projected cycle budget. Write `orchestrator-state.json` with the predicate verbatim and `validate-state` it. Write the active marker. Stop here when `--dry-run` is set.
5. **Loop until the predicate is met:**
   1. Assess state from cheap signals: the last `handoff.json`, the regression verdict, the error count, plus an affected-test verify.
   2. `python3 scripts/orchestrate.py validate-state orchestrator-state.json`, then `next-hop orchestrator-state.json` → next subcommand.
   3. Run that subcommand's reference with its own bounded inner loop.
   4. Record the hop outcome ∈ `progressed`, `no-op`, `failed`, `blocked`.
   5. Fold the hop's `handoff.json` into `orchestrator-state.json` (hop handoffs stay unchanged; two state objects, no overlap).
   6. `python3 scripts/orchestrate.py units <results.json>` recomputes Units remaining; append it to `units_remaining`.
6. **Stop conditions**, checked after each hop:
   - Predicate met → ship gate (only when `ship` is in the pipeline), else `CONVERGED`.
   - `plateau orchestrator-state.json` prints `PLATEAU` → stop and report.
   - `cycle` above the ceiling (default 50, `--max-cycles N`) → stop and report `CEILING`.
   - A hop outcome `blocked` or `failed` with no alternative route → checkpoint, stop, report `BLOCKED`.

### Router decision table

`next-hop` reads `orchestrator-state.json` and applies the first matching rule. Signals are cheap reads; never re-run the full suite just to route.

| State signal | Next hop |
|---|---|
| `errors_remaining > 0` | `fix` |
| `regression_verdict` is `UNSTABLE` | `regression` |
| `untested_gaps > 0` | `debug` |
| `pending_verify` is true | `verify` (fresh independent acceptance check) |
| none of the above, archetype `ship-ready` | `ship` |
| none of the above, any other archetype | `DONE` (exit the loop) |

Fields absent from the state count as zero or false. `next-hop` vocabulary: `fix`, `regression`, `debug`, `verify`, `ship`, `DONE`. The rows above for plateau, blocked hops, and exhausted pipelines are not `next-hop` outputs: the orchestrator applies them from the stop conditions and uses `regression` as the convergence re-check when all preset steps are spent and the predicate is still unmet.

`verdict orchestrator-state.json` synthesizes the stop word. Vocabulary: `CONVERGED` (Units remaining is 0, no plateau or ceiling flag; prints `ship=yes`), `PLATEAU`, `CEILING`, `BLOCKED` (prints `ship=no`). It takes the current units from the last numeric element of `units_remaining`. `plateau` accepts the state JSON (uses `units_remaining`) or a newline history file; `--window N` sets the window (default 5).

### Independent verify and overfit guard

Never optimize and accept against the same signal. For `optimize-metric` and `build-feature`, the acceptance check runs on a held-out set (a fresh scenario set or holdout assertions) separate from the `units` signal used to choose the change. When a high-impact change is accepted on the working signal, set `pending_verify` in the state; `next-hop` then routes to a `verify` hop, dispatched to `reason` or `predict` as an independent adversarial check, before `DONE` or ship. The verify hop is advisory input to convergence and never approves ship.

### Build-feature: TDD ladder

`build-feature` has no pre-existing metric, so progress is `green-assertion-count` (monotone integer, higher is better). Keep a change that turns a red sub-test green; revert a change that regresses a green sub-test. A floor guard prevents reverting scaffolding commits that compile and add no new failures but pass zero new tests. When the scope is large and net-new (greenfield, no existing test suite), advise the user to plan the build separately rather than grinding cycles.

### Orchestrator safety invariants

- Never auto-approve ship, deploy, or push. The orchestrator never passes `--auto` to `ship`; deploy always needs explicit user approval. The orchestrator deletes the active marker before it invokes `ship`.
- Data migration stays behind the anchored DB-URL allowlist from `skill://autoresearch/references/regression.md`: host exactly `localhost`, `127.0.0.1`, or a container hostname, or a database name with a `_test` / `_ci` suffix. A bare substring does not qualify; anything else is refused.
- `screen-cmd` runs on every derived command before the loop starts AND on every command read from a persisted state file on resume. Persisted commands are never trusted: resume re-screens the pinned predicate with `screen-state-predicate` and refuses on `refuse`.
- No un-screened commands mid-loop: the loop cannot introduce shell commands that bypass `screen-cmd`.
- The predicate is pinned, not re-derived. Round 0 writes it verbatim into the state; every cycle and every resume reuses that exact string.
- Validate the ledger before routing: `validate-state` gates the state file; a malformed ledger is not trusted.
- Independent verify before convergence (above).
- Cycles whose `units` is `unknown` (for example a runner crash) are excluded from the Plateau counter; repeated `unknown` routes to `BLOCKED`.

### Glossary

| Term | Meaning |
|---|---|
| Goal archetype | Classification of the natural-language goal into one of the nine categories above |
| Success predicate | Exact shell command plus expected output that defines "done" for orchestration-loop goals |
| Units remaining | Scalar of open gaps (failing tests, errors, metric delta); lower is better; computed by `units` |
| Plateau | Units remaining flat or worse for N consecutive computed cycles (default 5); oscillation that nets zero also qualifies |
| Orchestration loop | The cycle-bounded assess → route → run → record loop for predicate-bearing archetypes |
| Single-pass dispatch | One-shot routing to a self-terminating subcommand; no loop, plateau, ceiling, or ship gate |
| Independent verify hop | A `verify` step (`reason` or `predict`) that checks an accepted high-impact change against a fresh signal; gated by `pending_verify` |
| Holdout-verify | Acceptance check on a held-out set, separate from the `units` signal, to prevent overfitting the metric |

### Orchestrator finish

Append one row per hop to `orchestrator-results.tsv` (contracts: columns `hop`, `metric` = Units remaining). On stop, write `handoff.json` (`source: "orchestrator"`, `status`: `CONVERGED` → `COMPLETE`, `PLATEAU`/`CEILING`/`BLOCKED` → `BOUNDED`, user stop → `USER_INTERRUPT`; `findings` = open gaps; `config` = goal, archetype, predicate, terminal choice), delete the active marker if it is still present, and report the stop word.
