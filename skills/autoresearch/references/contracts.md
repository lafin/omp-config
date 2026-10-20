# Autoresearch shared contracts

Every subcommand reference points here for the blocks that used to be repeated per command: setup questions, preconditions, run directory and active marker, results TSV, handoff JSON, orchestrator state, flags, eval checkpoints, and chain handoff. A subcommand reference keeps only its own steps, defaults, and extension columns.

## Setup questions

- Ask the user once, batching every open setup question. Offer concrete options (detected globs, detected commands) where the reference lists them.
- If every required field arrives in the invocation arguments, skip setup.
- A run that cannot ask (headless subagent, CI, no TTY, `Mode: autonomous`) must not guess: fail fast and name the missing fields. Loop setup needs `Goal:` and `Verify:` (or `Target:` for `fix`) in the arguments.

## Preconditions (looping commands that edit or commit)

1. Inside a git repository (`git rev-parse --git-dir`).
2. Working tree clean (`git status --porcelain`). Warn when dirty; unrelated uncommitted changes would be reverted or mixed into commits, so ask the user to commit or stash first.
3. No stale lock files, no detached HEAD.
4. Commit check: run `git commit --allow-empty --dry-run`. If it fails (for example `commit.gpgsign=true` with no usable signing key), stop and ask the user before starting.
5. If `Guard:` is set, run it once to establish the guard baseline. A failing baseline guard is a critical failure.
6. Stale marker check (see Active marker below).
7. Fail fast on any critical issue; warn on non-critical ones.

## Verify safety screen

Screen every derived or user-supplied `Verify:`, `Guard:`, and `Target:` command before its first dry-run with `python3 scripts/orchestrate.py screen-cmd "<command>"` (path relative to the skill directory). `refuse` blocks the command: it flags `rm -rf` in any flag arrangement, `curl|sh` style pipes, fork bombs, embedded credentials, and outbound writes. Report the refusal and ask for a different command. The screen is a heuristic, not a sandbox: also read the command and refuse anything that mutates state outside the working tree.

## Run directory

`autoresearch/<subcommand>-<YYMMDD>-<HHMM>/` under the project root. Contents:

| File | When |
|---|---|
| `<subcommand>-results.tsv` | Every command that logs iterations |
| `handoff.json` | Every command that can chain, written at completion |
| `orchestrator-state.json` | Orchestrator runs only (run directory `autoresearch/orchestrator-<YYMMDD>-<HHMM>/`) |
| `evals-summary.md` / `.json` | With `--evals` or `evals` |
| command-specific reports | Listed in each reference |

## Active marker

File `autoresearch/.active` in the project root. Content: one line, the run directory path relative to the project root, for example `autoresearch/fix-261020-1405`. A run-scoped git guard hook keys only on this file's existence: while it exists, `git push`, `git reset --hard`, `git clean -f`, and `rm -rf` are blocked, and context compaction re-injects the run configuration and last TSV rows.

| Command | Writes marker |
|---|---|
| loop (core), `fix`, `debug`, `security`, `scenario`, `learn`, `reason`, `probe`, `improve`, `regression`, orchestrator | yes |
| `plan`, `predict`, `evals`, `ship` | no (`ship` pushes after explicit approval, so no run may hold the guard) |

Lifecycle:

1. **Before setup**: apply the stale-marker rule below.
2. **Write**: after the baseline succeeds (iteration 0 logged), write the marker.
3. **Delete on completion**: after `handoff.json` is written and before any chained command starts, delete the marker.
4. **Delete on abort**: user interrupt, unrecoverable error, or `ERROR` status also delete the marker, after the handoff is written.
5. **Inside an orchestrator run**: a hop started by the orchestrator neither writes nor deletes the marker; only the orchestrator does. The orchestrator deletes it before invoking `ship`.

Stale-marker rule: when `autoresearch/.active` exists at start, read the run directory it names. If the directory is missing, or its newest `*-results.tsv` was last modified more than 30 minutes ago, the marker is stale: refuse to start and offer to delete it (delete only on the user's confirmation). If the TSV is newer than 30 minutes, another run is active: stop and report the run directory. A stale marker only keeps the git guard on; the block message names the file to delete.

## Results TSV

Tab-separated, UTF-8, one row per iteration. Layout:

1. Optional `#` comment lines. Direction-bearing commands put `# metric_direction: higher_is_better` or `# metric_direction: lower_is_better` first. `scenario` omits it (exploration, not optimization).
2. Header row.
3. Row for iteration 0 (`baseline`) where a baseline exists, then one row per iteration.

Replace tabs and newlines inside a field with a space. Use `-` for a field that does not apply.

Common columns, in this order: `iteration`, `commit`, `metric`, `delta`, `guard`, `status`, `description`.

| Column | Meaning |
|---|---|
| `iteration` | Integer. `0` = baseline. Rounds (`reason`, `probe`) and phases (`ship`) use the same column |
| `commit` | Short SHA of the iteration commit, or `-` |
| `metric` | The command's number: loop metric, error count, cumulative findings, score. Reference states it |
| `delta` | `metric` minus the previous iteration's `metric`; `0` at baseline |
| `guard` | `pass`, `fail`, or `-` when no guard is configured |
| `status` | Vocabulary below |
| `description` | One line: what changed or what was found |

Extension columns follow the common ones. Every command except `regression` has `timestamp` (ISO 8601 UTC) as its first extension column, then its own columns from the table. Analysis (`evals`) detects columns by name and ignores unknown ones.

| Command | Extension columns after `timestamp` | `metric` is | Direction |
|---|---|---|---|
| loop (core) | `guard_metric` | the Verify number | `Direction:` flag |
| `fix` | `error_type`, `error_fixed` | error count | lower |
| `debug` | `hypothesis`, `technique`, `evidence`, `file_line` | cumulative confirmed findings | higher |
| `security` | `finding`, `severity`, `owasp`, `stride`, `evidence`, `file_line` | composite score | higher |
| `scenario` | `scenario`, `dimension`, `classification`, `severity` | cumulative logged scenarios | none (no direction comment) |
| `learn` | `file_documented`, `validation_status`, `issues_found`, `issues_fixed` | files with valid documentation (wiki mode: `pages_generated / pages_planned × 100`) | higher |
| `reason` | `candidate_label`, `judge_verdict` | `convergence_count` | higher |
| `probe` | `personas`, `questions`, `net_new` | total constraints | higher |
| `improve` | `category`, `research_question`, `source`, `insight_problem`, `insight_mechanism`, `confidence`, `classification` | cumulative insights | higher |
| `ship` | `phase` | checklist items passed | higher |
| orchestrator | `hop` | Units remaining (`unknown` when uncomputable) | lower |

Status vocabulary:

- Loop family (`loop`, `fix`, orchestrator hop outcomes aside): `baseline`, `keep`, `keep (reworked)` (`fix` only), `discard`, `crash`, `no-op`, `hook-blocked`, `metric-error`.
- Findings family: `debug` uses `confirmed`, `disproven`, `inconclusive`; `security` uses the severity as the status; `scenario` and `improve` use `new` or `extension`; `reason` uses `incumbent-kept`, `incumbent-replaced`, `converged`; `probe` uses `ok` or `saturated`; `learn` uses `pass` or `fail`; `ship` uses `pass`, `fail`, `warn`, `skipped`.
- Orchestrator rows: `progressed`, `no-op`, `failed`, `blocked`.

`regression` keeps its own 15-column schema, defined in `skill://autoresearch/references/regression.md`, because `scripts/score_regression.py verdict` consumes it by position.

## Handoff JSON

`handoff.json` in the run directory, written at completion and on abort:

```json
{
  "schema_version": 1,
  "source": "fix",
  "timestamp": "2026-10-20T14:05:00Z",
  "status": "COMPLETE",
  "results_tsv": "autoresearch/fix-261020-1405/fix-results.tsv",
  "findings": [],
  "config": {}
}
```

- `schema_version` is the handoff schema version (integer `1`), not a release string.
- `source`: the producing subcommand (`loop` for the core loop).
- `status`: one of `COMPLETE`, `CONVERGED`, `SATURATED`, `BOUNDED`, `USER_INTERRUPT`, `ERROR`. `ship` also uses `DRY_RUN` and `ROLLBACK`.
- `results_tsv`: path relative to the project root; omit for commands with no TSV.
- `findings`: command-specific list; each reference names its contents (unfixed errors, confirmed bugs, constraints, and so on).
- `config`: the inputs the next command needs (goal, scope, metric, direction, verify, and so on).
- `regression` adds `verdict` (`STABLE`, `UNSTABLE`, `BASELINE_UNAVAILABLE`) and `regression_state` (`REGRESSION_FOUND`, `REGRESSION_FIXED`, `none`).

## Orchestrator state

`orchestrator-state.json` is owned by the orchestrator and validated by `python3 scripts/orchestrate.py validate-state <file>` before every routing decision.

| Field | Type | Required | Read by |
|---|---|---|---|
| `goal` | non-empty string | yes | — |
| `archetype` | non-empty string | yes | `next-hop` (`ship-ready` routes to `ship`) |
| `predicate` | non-empty string, the pinned Success predicate command | yes | `screen-state-predicate` |
| `terminal_choice` | non-empty string (`stop-at-verified` or `proceed-to-ship`) | yes | — |
| `cycle` | integer ≥ 0 | yes | ceiling check |
| `units_remaining` | array of numbers or the string `"unknown"` | yes | `verdict` (last numeric element), `plateau` |
| `pipeline_log` | array of per-hop records | yes | — |
| `errors_remaining` | integer | optional | `next-hop` |
| `regression_verdict` | string (`UNSTABLE` routes to `regression`) | optional | `next-hop` |
| `untested_gaps` | integer | optional | `next-hop` |
| `pending_verify` | boolean | optional | `next-hop` |
| `plateau` | boolean | optional | `verdict` |
| `ceiling` | boolean | optional | `verdict` |

A `pipeline_log` record is `{ "cycle": N, "hop": "fix", "outcome": "progressed|no-op|failed|blocked", "units": N-or-"unknown" }`.

## Flags

| Flag | Applies to | Purpose |
|---|---|---|
| `Iterations: N` | looping commands | Loop iteration count. Always means loop iterations |
| `Iterations: unlimited` | looping commands | Opt-in unbounded |
| `Rounds: N` | `reason` | Debate rounds (the loop iterations of `reason`) |
| `Repeats: N` | `regression` | Repeat-axis count for repeat sweeps |
| `--evals` | looping commands | Mid-loop checkpoints and final summary |
| `--evals-interval N` | looping commands | Override checkpoint frequency |
| `--chain <targets>` | all | Comma-separated sequential handoff after completion |
| `--<subcommand>` | all | Shorthand for `--chain <subcommand>` |
| `--dry-run` | orchestrator, `ship` | Print derived config or planned pipeline; no execution |
| `--max-cycles N` | orchestrator | Hard ceiling on orchestration cycles (default 50) |
| `--classic` / `--auto` | bare invocation | Force Classic loop / Orchestrator mode |

`--iterations`, `--scope`, `--target`, `--guard`, `--depth`, and similar double-dash forms are accepted aliases of the `Keyword:` forms.

## Eval checkpoint (`--evals`)

- Interval: `floor(max / 3)`, minimum 1, where `max` is the iteration bound (`Rounds:` for `reason`, `--max-runs` for `regression`). Fixed `10` when unbounded. `--evals-interval N` overrides.
- Every `interval` iterations, pause and analyze the results TSV. Print at most five lines:

```
--- Eval Checkpoint (iterations {X}-{Y}) ---
{command-specific stats line}
{one-line recommendation}
---
```

- Stats line per command (the reference for each command names its line; summary here):

| Command | Stats line |
|---|---|
| loop | `Metric: {start} → {end} ({delta}) \| Kept: {n}/{total} \| Trend: {up/flat/down}` |
| `fix` | `Errors: {start} → {end} ({delta}) \| Kept: {n}/{total} \| Trend: {up/flat/down}` |
| `debug` | `Findings: {confirmed} confirmed \| Trend: {up/flat/down}` |
| `security` | `Score: {start} → {end} \| New findings: {n} \| Coverage: OWASP {x}/10, STRIDE {y}/6` |
| `scenario` | `New scenarios: {n} \| Dimensions covered: {x}/12 \| Saturation: {status}` |
| `learn` | `Docs written: {n} \| Validation: {pass}/{total} \| Gaps remaining: {m}` |
| `reason` | `Incumbent: {label} \| Convergence: {count}/{target} \| Oscillations: {n}` (header says `rounds`) |
| `probe` | `Constraints: {total} (+{new}) \| Saturation: {window_count}/3` (header says `rounds`) |
| `improve` | `Insights: {total} (+{new}) \| Categories: {covered}/5 \| Saturation: {window}/3` |
| `regression` | trend (up/flat/down) plus a one-line recommendation |

- Early stop: when the trend is flat (no new kept change, finding, scenario, document, or constraint) for 3 or more consecutive checkpoints, recommend stopping. `reason` recommends stopping on 3 or more checkpoints with oscillation.
- At loop end, write the full summary to `evals-summary.md` in the run directory (analysis rules in `skill://autoresearch/references/evals.md`).

| Command | Default | Interval | Checkpoints at |
|---|---|---|---|
| `reason` | 8 | 2 | 2, 4, 6, 8 |
| `learn` | 10 | 3 | 3, 6, 9, final |
| `debug`, `security`, `probe`, `improve` | 15 | 5 | 5, 10, 15 |
| `fix`, `scenario` | 20 | 6 | 6, 12, 18, final |
| loop | 25 | 8 | 8, 16, 24, final |
| unbounded | — | 10 | every 10 |

## Chain handoff

After a command completes (or aborts):

1. Write `handoff.json` (schema above).
2. Delete the active marker if this command wrote it.
3. If `--chain <targets>` (or a `--<subcommand>` shorthand, or `--fix` on `debug`, `security`, and `regression`) is set, invoke the next target in order, passing the handoff path and propagating `--evals`.
4. `improve` is a terminal emitter: no downstream chain.
5. `ship` never auto-deploys when chained; deployment still needs explicit approval.
