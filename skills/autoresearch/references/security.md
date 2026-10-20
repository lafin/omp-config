# security: STRIDE and OWASP audit loop

Iterative audit with red-team personas. Default 15 iterations. Read `skill://autoresearch/references/security-checklist.md` for the STRIDE table, OWASP list, personas, severity scale, composite formula, and finding format. Shared blocks: `skill://autoresearch/references/contracts.md`. For a one-shot code review at a trust boundary without a loop, use bare `skill://security-review` instead.

## Arguments

- `Scope:` or `--scope` — file globs to audit.
- `Focus:` — specific area (auth, API, data handling, and so on).
- `Depth:` or `--depth` — quick (5 iterations), standard (15), deep (30+).
- `Iterations:` or `--iterations` — default 15, or `unlimited`.
- `--diff` — delta mode: only audit files changed since the last audit.
- `--fix` — after the audit, fix Critical and High findings (chains to `fix`).
- `--fail-on <severity>` — report non-zero status if findings at or above the threshold exist (CI gate).
- `--evals`, `--evals-interval N`, `--chain`, `--<subcommand>`.

## Setup (if required context is missing)

If Scope is missing and there is no `--diff`:

1. Scan the codebase for tech stack, frameworks, and API routes.
2. Ask the user once, batching:
   1. Scope: what to audit? Entire codebase, API and middleware, auth, external-facing.
   2. Depth: quick (5), standard (15), deep (30+), unlimited.
   3. Action: report only, report and fix, report and CI gate.

If all are provided, skip setup.

## Setup phase (once, before the loop)

1. **Reconnaissance.** Scan `package.json` / `requirements.txt` (dependencies), `.env.example` (secrets), Dockerfile (infrastructure), API route files (attack surface), auth and middleware (trust boundaries), DB schemas (data assets), CI/CD configs (supply chain).
2. **Asset identification.** Catalog data stores, auth systems, external services, user inputs.
3. **Trust boundary mapping.** Browser↔server, public↔authenticated, user↔admin, CI↔prod.
4. **STRIDE threat model.** Generate threats per category using the checklist.
5. **Attack surface map.** Entry points, data flows, abuse paths.
6. **Baseline.** Count known issues; initialize coverage tracking.

Create `autoresearch/security-<YYMMDD>-<HHMM>/`; write `overview.md`, `threat-model.md`, `attack-surface-map.md`, and the active marker (contracts). TSV: `# metric_direction: higher_is_better`, then the common columns plus `timestamp`, `finding`, `severity`, `owasp`, `stride`, `evidence`, `file_line`. `metric` is the composite score; `status` is the severity; `commit` is `-` (the audit does not commit).

## Iteration loop

1. **Review.** Read the TSV and coverage tracking; identify untested attack vectors from the threat model. Prioritize untested OWASP categories, then untested STRIDE, then depth on existing ones.
2. **Attack.** Adopt a red-team persona for the vector (rotate Security Adversary, Supply Chain, Insider Threat, Infra Attacker). Dive into the relevant code with an adversarial mindset: code paths, input handling, auth checks, data flows.
3. **Validate.** Construct proof: `file:line` plus a specific attack scenario. Every finding MUST have code evidence; no theoretical fluff. Classify severity Critical, High, Medium, Low, or Info. Map to OWASP (A01-A10) and STRIDE (S/T/R/I/D/E).
4. **Log.** Append the finding to the TSV; update coverage tracking. Every 5 iterations print `OWASP: [A01✓ A02✓ A03✗ ...] X/10 | STRIDE: [S✓ T✓ R✗ ...] Y/6 | Score: Z`.
5. **Eval checkpoint.** Stats line `Score: {start} → {end} | New findings: {n} | Coverage: OWASP {x}/10, STRIDE {y}/6`; early-stop recommendation after 3 or more checkpoints with no new findings.
6. **Bounded check.** At the bound, exit the loop.

### Composite metric

`score = (owasp_tested/10)*50 + (stride_tested/6)*30 + min(findings, 20)`

## After the loop

1. Write `findings.md` (severity-ranked).
2. Write `owasp-coverage.md`.
3. Write `recommendations.md`.
4. With `--fix`, chain to `fix` with the Critical and High findings.
5. With `--fail-on`, compare findings against the threshold and report a non-zero status if exceeded.

## Summary

Print: findings by severity, OWASP coverage X/10, STRIDE coverage Y/6, composite score.

## Finish

Write `handoff.json`: `source: "security"`, `findings` = all findings with severity, OWASP, STRIDE, `file:line`; `config` = scope, focus, depth. Delete the active marker, then follow `--chain` (contracts).
