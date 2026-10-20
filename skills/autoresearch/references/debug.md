# debug: scientific-method bug hunt

Hunt bugs by hypothesis: hypothesize, test, falsify, repeat. Default 15 iterations. Shared blocks (setup rules, TSV, handoff, eval checkpoint, chain, active marker): `skill://autoresearch/references/contracts.md`.

## Arguments

- `Scope:` or `--scope` — file globs to investigate.
- `Symptom:` or `--symptom` — error message or behavior description.
- `Iterations:` or `--iterations` — default 15, or `unlimited`.
- `--fix` — shorthand for `--chain fix`.
- `--severity` — filter: critical, high, medium, low.
- `--technique` — force a specific technique.
- `--evals`, `--evals-interval N`, `--chain`.

## Setup (if required context is missing)

If Scope and Symptom are both missing:

1. Auto-scan: run tests, lint, and typecheck to detect existing failures.
2. Ask the user once, batching:
   1. Issue: what is the problem? Hunt all bugs, a specific error, failing tests, a CI failure, performance.
   2. Scope: which files? Suggested globs plus the entire codebase.
   3. Depth: quick (5), standard (15), deep (30+), unlimited.
   4. After: when bugs are found, report only, find and fix (`--chain fix`), chain to another command, or ask each time.

If all are provided, skip setup.

## Investigation techniques

| Technique | When to use |
|---|---|
| Binary search | You know when it worked; find when it broke |
| Differential | Compare working versus broken state |
| Minimal reproduction | Simplify to the smallest failing case |
| Trace | Follow the execution path through code |
| Pattern search | Grep for known anti-patterns |
| Working backwards | Start from the error, trace to the root cause |

## Baseline (before the loop)

1. Auto-scan for failures if no symptom was provided.
2. Create `autoresearch/debug-<YYMMDD>-<HHMM>/`; write the active marker (contracts).
3. TSV: `# metric_direction: higher_is_better`, then the common columns plus `timestamp`, `hypothesis`, `technique`, `evidence`, `file_line`. `metric` is the cumulative confirmed-findings count; `status` is `confirmed`, `disproven`, or `inconclusive`; `commit` is `-` (debug does not commit).

## Iteration loop

1. **Review context.** Read the results TSV (past findings). Assess what was tested and which vectors remain. If no hypotheses are left, stop early.
2. **Hypothesize.** Form ONE specific, falsifiable hypothesis, different from all previous: "I hypothesize that {X} because {evidence}. Test by {Y}."
3. **Investigate.** Apply the fitting technique: read relevant code, run targeted tests, check logs. Collect evidence; `file:line` references are required.
4. **Classify.**
   - `confirmed` — hypothesis correct, bug found with evidence.
   - `disproven` — hypothesis wrong, evidence against it.
   - `inconclusive` — cannot be proven or disproven; needs a different approach.
5. **Log.** Append the TSV row.
6. **Eval checkpoint.** With `--evals` at `iteration % interval == 0`; stats line `Findings: {confirmed} confirmed | Trend: {up/flat/down}`; plateau means no new confirmed finding for 3 or more checkpoints.
7. **Bounded check.** At the bound, exit the loop.

## Summary

Print: total hypotheses tested, confirmed / disproven / inconclusive counts, every confirmed bug with severity and `file:line`.

## Finish

Write `handoff.json`: `source: "debug"`, `findings` = confirmed bugs with severity and `file:line`, `config` = scope, symptom. Delete the active marker. With `--fix`, chain to `fix` automatically; otherwise follow `--chain` (contracts).
