# Conditional gap decisions recorded

- **Status:** Completed
- **Date:** not stated in source
- **Source:** [Skill Set Improvement Plan §16 Change 13: Conditional decisions](../skill-set-improvement-plan.md#change-13-conditional-decisions)

## Decision

Change 13 required:

- run security audit and debugging baseline;
- review observability and performance demand evidence;
- record an explicit add, defer, or reject decision for each.

**Exit:** no conditional skill is added on intuition alone.

All four decisions are recorded as **DEFER**, not **REJECT**; no conditional skill was added. Each DEFER keeps its unblocking threshold open under plan §13 ([Workstream H: Conditional Gap Investigations](../skill-set-improvement-plan.md#13-workstream-h-conditional-gap-investigations)):

- **Agent security boundaries:** DEFER after live audit. Skills-disabled baseline `15/18` critical passes, current-owner treatment `18/18` (`evals/results/conditional-security/home-v4-baseline`, `home-v4-treatment`; `openai-codex/gpt-5.6-sol`, profile `home`, thinking off, no tools). `hosted-agents`, `harness-engineering`, and `tool-design` express every audited boundary.
- **Debugging:** DEFER. Skills-disabled baseline `18/18` critical passes (`evals/results/conditional-debugging/home-v13-baseline`); no case reaches the two-of-three critical-failure threshold.
- **Observability:** DEFER; no three distinct real tasks and no production incident blocked by missing telemetry guidance are recorded.
- **Performance and remaining lifecycle gaps:** DEFER; no evidence set establishes the five §13.4 conditions.

## Evidence

- [docs/conditional-skill-decisions.md](../conditional-skill-decisions.md)
- [evals/cases/conditional-agent-security-development.jsonl](../../evals/cases/conditional-agent-security-development.jsonl)
- [evals/cases/conditional-debugging-development.jsonl](../../evals/cases/conditional-debugging-development.jsonl)
