# Autoresearch Admission Accepted as Process Consistency

- **Status:** Accepted
- **Date:** 2026-10-21
- **Source:** owner decision after review of `evals/results/autoresearch-admission/merge-gate-final.json`

## Context

The admission gate passed only with `--correctness-benefit`. Its note says treatment passed 12/12 repository attempts versus 0/12 baseline. That count is true, but the difference comes only from the non-critical `results_tsv` and `handoff_json` checks. On critical checks both conditions passed 12/12. Treatment used 6–8× the tokens (development 520K → 3.95M, holdout 795K → 4.88M).

## Decision

Keep `autoresearch` admitted. The accepted benefit is process consistency: a results TSV, a `schema_version` 1 handoff, and active-marker cleanup on every run. It is not a correctness gain. Read the gate note's "correctness" wording as this claim.

## Limits

- The `security` subcommand shows no gain over baseline: `evals/results/autoresearch-security`, `autoresearch-security-hard`, and `autoresearch-security-hard-6` all fail the gate. Every holdout miss rated `lookup_requester` MEDIUM; the fixture never defines requesters as tenant-owned, so that case is ambiguous and is now historical. A single-handler check (`evals/results/security-review-severity`) rated every unambiguous cross-tenant read HIGH, so the `security-review` severity rule is not shown to be defective.
- A future correctness claim needs a fresh holdout and a gate that passes without this decision.
