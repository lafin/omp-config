# Critical-Gain Admission Path

- **Status:** Accepted
- **Date:** 2026-10-13
- **Source:** owner decision after the blind v3 holdout gates failed (`evals/results/ecc-plan/fix9/`); [backlog](../backlog.md) Workstream C Changes 5–7 and `scr-3`

## Context

The `improvement` path for behavior suites requires every development and holdout attempt to pass every check, no critical regression on any attempt, and a stated `--correctness-benefit` for higher token cost. Multi-skill suites with 66–105 attempts cannot meet it under sampling noise. In fix9, refresh-behavior went from 36/105 to 100/105 holdout critical passes and catalog-behavior went from 8/66 to 48/66. Both failed because of 1–2 single-attempt critical regressions and the all-checks requirement.

## Decision

Add a third admission path, `python3 evals/grade.py gate --case-kind behavior --admission-path critical-gain`. The existing `improvement` and `procedural-value` paths are unchanged. Admission requires all of:

1. **Regression tolerance:** no case is critically regressed in more than 1 attempt (`CRITICAL_GAIN_MAX_CASE_REGRESSIONS`), counted across development, holdout, and routing holdout. A critical regression is an attempt where the baseline passes every critical check and the paired treatment does not.
2. **Development gain:** the treatment critical-pass rate minus the baseline rate is at least 0.25 (`CRITICAL_GAIN_MIN_DELTA`).
3. **Holdout gain:** at least 18 holdout attempts, a critical-pass rate gain of at least 0.25, and a treatment critical-pass rate of at least 0.9 (`CRITICAL_GAIN_MIN_HOLDOUT_RATE`).
4. **Routing holdout:** every routing holdout attempt passes, with no regression (unchanged).
5. **Cost:** token, tool, and question metrics are recorded. Higher cost is reported in `increased_metrics` but does not fail the gate.

Non-critical checks do not decide admission. They stay in `check_coverage` and `regressions` for review.

## Provenance and limits

These thresholds were chosen after the fix9 results were seen, so applying the rule to fix9 is post hoc. Admission evidence is a fresh capture of the frozen v3 holdout cases, run after this record and the evaluator change are committed. Changing a threshold is an evaluator change and needs a new decision record before any treatment run (invariant 9).

## Evidence

- `evals/grade.py` (`merge_gate`, `CRITICAL_GAIN_*` constants)
- `tests/test_evaluation_harness.py::test_critical_gain_gate_boundaries`
