# scenario: edge cases across 12 dimensions

Generate edge cases from a seed scenario. Default 20 iterations. Exploration, not optimization: no metric direction. Shared blocks: `skill://autoresearch/references/contracts.md`.

## Arguments

- `Scenario:` — seed scenario description (or all remaining invocation text if there is no keyword).
- `Domain:` or `--domain` — web, mobile, API, CLI, data pipeline, infrastructure.
- `Scope:` or `--scope` — file globs for codebase context.
- `Focus:` or `--focus` — specific dimension to prioritize.
- `--depth` — shallow (10), standard (20), deep (40+).
- `--format` — markdown (default), json, gherkin.
- `Iterations:` or `--iterations` — default 20, or `unlimited`.
- `--evals`, `--evals-interval N`, `--chain`, `--<subcommand>`.

## Setup (if Scenario or Domain is missing)

Ask the user once, batching:

1. Scenario: describe the feature or flow to explore.
2. Domain: web app, mobile app, API, CLI, data pipeline, infrastructure.
3. Scope: which files for context? Suggested globs plus the entire codebase.
4. Depth: quick (10), standard (20), deep (40+), unlimited.

If all are provided, skip setup.

## 12 dimensions

| # | Dimension | Explores |
|---|---|---|
| 1 | Happy path | Normal successful flows |
| 2 | Validation | Input boundaries, types, formats |
| 3 | Permissions | Auth, roles, access control |
| 4 | Concurrency | Race conditions, deadlocks, ordering |
| 5 | State | Invalid transitions, corruption |
| 6 | Scale | High volume, large data, many users |
| 7 | Failure | Network errors, timeouts, partial failures |
| 8 | Security | Injection, abuse, bypass attempts |
| 9 | Integration | Third-party failures, API contract violations |
| 10 | Data | Null, empty, unicode, injection, overflow |
| 11 | UX | Confusion, misuse, accessibility |
| 12 | Recovery | Retry, rollback, idempotency |

## Baseline

1. Read the seed scenario and codebase context.
2. Create `autoresearch/scenario-<YYMMDD>-<HHMM>/`; write the active marker (contracts).
3. TSV: common columns plus `timestamp`, `scenario`, `dimension`, `classification`, `severity`. No `# metric_direction` comment. `metric` is the cumulative count of logged scenarios; `status` is `new` or `extension`; `commit` is `-`.

## Iteration loop

1. **Review.** Read the TSV, check dimension coverage, identify underexplored dimensions. With `--focus`, prioritize that dimension.
2. **Generate.** Pick the next dimension (round-robin, or priority with `--focus`). Generate 3-5 specific scenarios for it; each has title, dimension, classification, severity, description.
3. **Classify.**
   - `new` — genuinely novel edge case.
   - `extension` — builds on a previously found scenario.
   - `duplicate` — already covered; skip, do not log.
4. **Log.** Append new and extension scenarios; skip duplicates. Severity: critical, high, medium, low.
5. **Saturation check.** If 3 consecutive iterations produce only duplicates, the dimension is saturated: move to the next. If ALL dimensions are saturated, stop early.
6. **Eval checkpoint.** Stats line `New scenarios: {n} | Dimensions covered: {x}/12 | Saturation: {status}`; early-stop recommendation after 3 or more checkpoints that are mostly duplicates.
7. **Bounded check.** At the bound, exit the loop.

## Output

- `scenarios.md` — organized by dimension, severity-ranked within each.
- `edge-cases.md` — flat severity-ranked list.
- `scenario-results.tsv`.

## Summary

Print: total scenarios (new, extension, duplicate), dimension coverage X/12, severity distribution.

## Finish

Write `handoff.json`: `source: "scenario"`, `findings` = scenarios by severity, `config` = scenario, domain, scope. Delete the active marker, then follow `--chain` (contracts).
