# fix: reduce errors to zero

Fix errors one at a time until none remain: tests, types, lint, build. Default 20 iterations. Shared blocks (preconditions, gpgsign check, TSV, handoff, eval checkpoint, chain, active marker): `skill://autoresearch/references/contracts.md`.

## Arguments

- `Target:` or `--target` — command that shows errors (for example `npm test`, `tsc --noEmit`).
- `Scope:` or `--scope` — file globs that may be modified.
- `Guard:` or `--guard` — safety command that must always pass.
- `Iterations:` or `--iterations` — default 20, or `unlimited`.
- `--from-debug` — read `handoff.json` from the previous `debug` run (scope and findings).
- `--category` — filter: test, type, lint, build.
- `--evals`, `--evals-interval N`, `--chain`.

## Setup (if required context is missing)

If Target and Scope are both missing:

1. Auto-detect failures: run the test suite, type checker, linter, and build.
2. Present the results and ask the user once, batching:
   1. Fix what: "Found N test failures, M type errors, K lint errors. Fix what?" Everything, only tests, only types, only lint.
   2. Guard: a safety command that must always pass (`npm test`, `tsc`, `npm run build`, skip).
   3. Scope: which files may be modified? Suggested globs from error locations, plus all.
   4. Launch: fix until zero, fix with a limit, cancel.

If all are provided, skip setup. With `--from-debug`, read `handoff.json` for scope and findings.

## Preconditions

Apply the contracts block: git repo, clean tree, no lock files, no detached HEAD, `git commit --allow-empty --dry-run` passes, stale-marker rule. Screen `Target:` and `Guard:` with `screen-cmd`.

## Baseline (iteration 0)

1. Run Target and count errors. Metric = error count, direction `lower_is_better`.
2. Create `autoresearch/fix-<YYMMDD>-<HHMM>/`. TSV: `# metric_direction: lower_is_better`, then the common columns plus `timestamp`, `error_type`, `error_fixed`. Record the baseline row (`baseline`).
3. Write the active marker (contracts).

## Iteration loop (until zero errors or the bound)

1. **Review.** Read the results TSV and git log. Run Target for the current error list. If the error count is 0, exit the loop (SUCCESS).
2. **Prioritize.** Order: crash or fatal, test failures, type errors, lint, warnings. Within a category, easiest first (single-file fixes before cross-file).
3. **Fix ONE thing.** Pick the highest-priority error and make one atomic fix that addresses exactly one error. Record the error type and which error was fixed.
4. **Commit.** `experiment: fix {error_type} — {description}`.
5. **Verify.** Run Target, count errors, compute delta. Expect the count to drop by 1 or more.
6. **Guard.** If Guard is set and fails, revert.
7. **Decide.**
   - `keep` — error count decreased AND guard passes.
   - `keep (reworked)` — the fix needed adjustment; the second attempt worked.
   - `discard` — error count same or higher; `git revert HEAD --no-edit`.
   - `crash` — Target or Guard failed to run; revert.
   - `hook-blocked` — a git hook blocked the commit.
   - `metric-error` — Target output not parseable; revert.
8. **Log.** Append the row (`error_type`, `error_fixed`, commit or `-`, error count as `metric`, delta, guard, status, description).
9. **Eval checkpoint.** Stats line `Errors: {start} → {end} ({delta}) | Kept: {n}/{total} | Trend: {up/flat/down}`.
10. **Bounded check.** At the bound, exit the loop.

## Summary

Print: total errors fixed, remaining errors, error-type distribution, fix success rate.

## Finish

Write `handoff.json`: `source: "fix"`, `findings` = unfixed errors, `config` = target, scope, guard. Delete the active marker, then follow `--chain` (contracts).
