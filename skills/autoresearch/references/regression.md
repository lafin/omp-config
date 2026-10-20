# regression: layered stability gate

Capture baseline behavior on the base ref, diff the candidate, and report a verdict STABLE or UNSTABLE before you push. Shared blocks (preconditions, handoff, eval checkpoint, chain, active marker): `skill://autoresearch/references/contracts.md`.

A regression is a **green→red transition ONLY**. The gate orchestrates the project's OWN test, bench, snapshot, and migrate commands (it is a protocol, not a bundled framework), captures baseline behavior in an isolated git worktree, re-runs the candidate, and reports a tiered ship or no-ship verdict.

## Arguments

- `Base:` or `--base` — base ref to diff against. Default: `git merge-base HEAD main` (else `main` or `master`).
- `Scope:` or `--scope` — file globs limiting the change surface.
- `--select auto|full|affected` — test selection (default `auto`). `auto` uses the detected affected-test mapper if available, else the FULL suite. Never a silent subset.
- `--samples N` — SCORE samples per side (default 7). `--noise-band %` — performance tolerance (default 5%).
- `--matrix` — opt-in matrix axis (OFF by default). `--max-runs N` — ceiling on total runs (default 200).
- `--baseline-cache` (default on) — reuse `baseline/<full-sha>/` by SHA. `Baseline: <prebuilt-ref>` bypasses capture.
- `--probe` (default), `--probe deep`, `--no-probe`.
- `--predict --reason --debug --fix --fix-cycles N --evals --evals-interval N --chain <targets>` and `--<sub>` shorthand.
- `Repeats:` — repeat-axis count for `--select` and repeat sweeps. (`Iterations:` keeps its loop meaning and is not used for this axis.)

## Setup / probe-on-launch

1. Auto-detect per-dimension verify commands: `package.json` scripts, `Makefile`, `nx`, migrate config, bench, snapshot, and size scripts.
2. Ask the user once to confirm the detected commands, the base ref, and which dimensions to run.
3. **Auto-skip probe** when running in CI, with no TTY, with `--mode autonomous`, with a complete config, or from a chained handoff: log the inferred config instead of asking.
4. Apply the contracts Preconditions block (clean tree, gpgsign dry-run commit check, stale-marker rule). Write the active marker once the baseline is captured.

## Classification phase (first-class, before any differential)

Establish the baseline green-set per dimension, then tag each unit. Match by **test id first, then path**.

| State | Meaning | Gated? |
|---|---|---|
| `regression-eligible` | green on baseline | YES: only green→red counts |
| `pre-existing` | red→red (already failing) | no: excluded |
| `new-coverage` | absent→red (brand-new test) | no: new coverage, ungated |
| `flaky` | nondeterministic on baseline | no: routed to flakiness SCORE |
| `baseline-unavailable` | dimension never green | no: advisory only |

**Core invariant: red→red, absent→red, and flake→red are NOT regressions.** Run flakiness N times on **both** baseline and candidate; a candidate failure inside the baseline flake-envelope routes to flakiness SCORE, never to a regression. `5/5 green ≠ non-flaky`: detection probability is `1−(1−p)^n` (about 23% at p=5%, n=5); print it.

## Baseline capture

`git worktree add --detach <full-sha>` (a detached SHA avoids "branch already checked out" when Base equals HEAD) creates `baseline/<full-sha>/`; `--baseline-cache` reuses it by SHA. Then, per worktree: `git submodule update --init` and dependency install (the lockfile is SHA-pinned, so the cache stays sound). Per-dimension **setup tiers**: api-contract = file-diff, no build; functional, integration-e2e, and data-migration = full environment. On completion or crash: `git worktree remove` and `git worktree prune`. Warn on concurrent index-lock contention. `Baseline: <prebuilt-ref>` bypasses capture.

## Dimension registry

| Dim | Tier | Compare | Key params |
|---|---|---|---|
| functional | HARD | baseline green-set vs candidate; a new failure is a regression | test cmd, globs |
| api-contract | HARD | schema or exports diff: breaking? | schema cmd, breaking ruleset |
| data-migration | HARD | default: up applies clean, idempotent re-apply, app boots and schema valid; schema/rowcount roundtrip opt-in | migrate cmds, fixture, allowlisted DB |
| integration-e2e | HARD | e2e green-set diff | e2e cmd |
| flakiness | SCORE | run N times on baseline and candidate, count nondeterministic | runs (default 5), flake-threshold |
| performance | SCORE | K **independent-process** samples per side, Mann-Whitney U AND effect size beyond `max(noise-band%, k·stdev)`, report median delta | bench cmd, samples=7, noise-band=5%, k=2 |
| resource | SCORE | memory, bundle, size delta vs budget | size cmd, budget |
| visual-ui | SCORE | containerize render; default `maxDiffPixelRatio` with AA-detection; SSIM = per-page escalation | snapshot cmd, diff-threshold, mask regions |

`--select auto` mapper (`jest --findRelatedTests` fed the changed-file list; `nx affected` project graph) is a **best-effort static-import** mapper: blind to dynamic, runtime, and global-setup couplings. The report names the mapper and its blind-spot caveat; a HARD STABLE earned on an affected subset prints "run `--select full` for high-stakes". The FULL suite is the correctness default.

- **performance independence:** each sample is an independent process launch (warmups discarded), never an in-process iteration; autocorrelation, GC, and thermal effects would otherwise violate Mann-Whitney's independence assumption. At n=7 the test detects only regressions of about 1σ or more; raise `--samples` for tight gates.
- **data-migration guard:** opt-in. Before any migration the DB URL MUST pass an **anchored** allowlist: the host is exactly `localhost`, `127.0.0.1`, or a container or service hostname, OR the database name carries a `_test` or `_ci` suffix. A bare substring (such as `test` inside `latest`, or `ci` inside `precision`) does **not** qualify. Anything else is refused: ephemeral only, never dev or prod. Even an allowlisted URL requires explicit user confirmation before applying. A missing down-migration is a forward-only advisory, **never a finding**.

## Differential loop (per dimension × axis × run)

Run the candidate verify against the baseline metric and compute a `regressed` boolean and a 0-100 `subscore`. Axes: `diff` (default), `repeat N×` (N from `Repeats:`), `full`, `matrix` (opt-in). Log one TSV row per cell.

**--max-runs ceiling:** projected runs = dims × axes × samples × matrix-cells. If it exceeds `--max-runs` (default 200), warn and require confirmation (CI default: abort with a message). This is the run budget; the `Iterations:` flag does not apply.

## Verdict

- Any HARD row with `regressed=true` and `classification=regression-eligible` → **UNSTABLE** (green→red hard-blocks).
- Otherwise `stability_score = Σ(weight × dim_subscore)` over the SCORE dims that ran (flakiness .30, performance .30, resource .20, visual .20, renormalized over present dims). **STABLE iff the score is 95 or more** (`REG_THRESHOLD` and weights are overridable).
- Print the **score math** (per-dimension contribution table) and declare **dims-ran vs UNAVAILABLE**. An UNAVAILABLE dimension is always listed, never silently passed.

Backed by `python3 scripts/score_regression.py verdict <results.tsv>` (path relative to the skill directory): exit 0 STABLE, 1 UNSTABLE, 2 error or `BASELINE_UNAVAILABLE`.

## Hunter (root cause)

On a confirmed HARD regression, engage automatically. Bisect (reuse `skill://autoresearch/references/debug.md`) ONLY when the failing case passes a **3/3 reproducibility gate**. SCORE and non-deterministic regressions get a differential root-cause and an optional `--reason` or `--predict`, no bisect. A non-reproducible regression becomes a "manual triage" finding.

## --fix re-gate

`--fix` repairs blocking regressions, at most **3 cycles** (`--fix-cycles N`). Each fix-cycle MUST strictly shrink the blocking set, else STOP with "fix not converging". The intermediate re-gate scopes to the failing and touched dims; the final cycle runs the full battery. No HARD-gate bypass.

## Output

`autoresearch/regression-<YYMMDD>-<HHMM>/` containing `regression-results.tsv`, `stability-report.md`, `dimensions/<dim>.md`, `baseline/`, `evals-summary.md` (with `--evals`), and `handoff.json`.

### TSV schema (regression keeps its own 15-column layout)

`python3 scripts/score_regression.py verdict` reads these columns by position (dimension 3, tier 5, classification 6, regressed 10, subscore 11), so the order is fixed and the common columns from the contracts do not apply here.

```
# metric_direction: higher_is_better
iteration	timestamp	dimension	axis	tier	classification	baseline	candidate	delta	regressed	subscore	severity	status	file_line	description
```

## Eval checkpoint (`--evals`)

Interval = `floor(max_runs / 3)`, minimum 1 (fixed 10 if unbounded); override with `--evals-interval N`. Every interval, analyze the results TSV and print the trend (up, flat, down) with a one-line recommendation. Plateau for 3 or more checkpoints recommends early stop. At the end, write the full summary to `evals-summary.md`.

## Chain handoff

Write `handoff.json` to the run directory (contracts schema) with `source: "regression"`; `status` ∈ the common enum; `verdict` ∈ `STABLE`, `UNSTABLE`, `BASELINE_UNAVAILABLE` plus `regression_state` ∈ `REGRESSION_FOUND`, `REGRESSION_FIXED`, `none`: `ship` reads `verdict` for the deploy gate; `findings` = blocking regressions (dim, severity, `file_line`, classification); `config` = base, scope, dims, axes, verdict math.

With `--fix`, chain to `fix` automatically. Invoke the next `--chain` target in order and propagate `--evals`. Canonical combo: `--predict --evals --fix --ship` = predict → gate → (hunter on HARD) → fix (up to 3 cycles) → re-gate → ship iff STABLE (deploy still needs explicit approval). Delete the active marker before invoking `ship`.

## Safety

Verify-command screen (no `rm -rf`, no `curl|sh`); worktree cleanup and prune on crash; data-migration refuses any non-allowlisted DB URL; probe auto-skips non-interactively; chained `ship` never auto-deploys.
