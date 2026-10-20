# security: bounded security-review loop

Repeat the `security-review` procedure one trust boundary per iteration until every mapped boundary in scope is checked. Default 15 iterations. The per-boundary procedure, severity scale, failure modes, and finding format belong to bare `skill://security-review`: read it first and follow it exactly. This file adds only the loop, coverage tracking, and chaining. Shared blocks: `skill://autoresearch/references/contracts.md`. For one diff or a few files, use `skill://security-review` directly without this loop.

The loop never rewards finding count. Coverage of mapped boundaries is the metric; an iteration that checks a boundary and finds nothing is a successful iteration.

## Arguments

- `Scope:` or `--scope` — file globs to audit.
- `Focus:` — specific area (auth, API, uploads, payments, and so on).
- `Depth:` or `--depth` — quick (5 iterations), standard (15), deep (30+).
- `Iterations:` or `--iterations` — default 15, or `unlimited`.
- `--diff` — only boundaries whose files changed since the last audit (`handoff.json` of the previous `security` run).
- `--fix` — after the audit, fix `HIGH` findings (chains to `fix`).
- `--fail-on <high|medium>` — report non-zero status if findings at or above the threshold exist (CI gate).
- `--evals`, `--evals-interval N`, `--chain`, `--<subcommand>`.

## Setup (if required context is missing)

If Scope is missing and there is no `--diff`, scan routes, handlers, jobs, CLIs, and message consumers, then ask the user once, batching: scope (detected areas or the whole codebase), depth, and action (report only, report and fix, report and CI gate).

## Boundary map (once, before the loop)

1. Apply `security-review` step 1 (map trust boundaries) to the whole scope. Record each entry point with the privileged operations it reaches, the caller's identity source, and the data the caller controls.
2. Order the map: unauthenticated entry points first, then money and irreversible actions, then authorization on object or tenant IDs, then the rest.
3. Agent prompt injection, tool authority, and sandbox boundaries are out of scope; list them in `boundaries.md` as routed to `hosted-agents`, `harness-engineering`, or `tool-design`.

Create `autoresearch/security-<YYMMDD>-<HHMM>/`; write `boundaries.md` (the ordered map) and the active marker (contracts). TSV: `# metric_direction: higher_is_better`, then the common columns plus `timestamp`, `boundary`, `severity`, `file_line`, `exploit_path`. `metric` is boundaries checked; `status` is the highest severity found at that boundary, or `clean`; `commit` is `-` (the audit does not commit).

## Iteration loop

1. **Pick** the next unchecked boundary from the map (with `--diff`, only changed ones). If none remain, exit the loop (SUCCESS).
2. **Review** it with `security-review` steps 2-6: trace controlled data to sinks, check authorization at the operation, secrets and sensitive output, abuse limits. Read callers and guards before reporting.
3. **Log** one TSV row per boundary. A boundary with several findings gets one row per finding; a clean boundary gets one row with status `clean`. Every finding carries the `security-review` output fields.
4. **Eval checkpoint.** Stats line from the contracts.
5. **Bounded check.** At the bound, exit the loop and list the unchecked boundaries.

## After the loop

1. Write `findings.md`: findings ranked `HIGH`, `MEDIUM`, `LOW`, each in the `security-review` output format, and the boundaries checked clean.
2. With `--fix`, chain to `fix` with the `HIGH` findings; each fix adds the regression check `security-review` step 7 requires.
3. With `--fail-on`, compare findings against the threshold and report a non-zero status if exceeded.

## Summary

Print: boundaries checked / mapped, findings by severity, unchecked boundaries.

## Finish

Write `handoff.json`: `source: "security"`, `findings` = all findings with severity, `file_line`, exploit path; `config` = scope, focus, depth, boundaries checked and unchecked. Delete the active marker, then follow `--chain` (contracts).
