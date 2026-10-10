# Close the four canonical routing gaps

- **Status:** Completed
- **Date:** not stated in source; routing development runs in `evals/results/catalog-routing-home-v1` are dated 2026-09-16
- **Source:** [Skill Set Improvement Plan §7 Workstream B: Close the Four Canonical Routing Gaps](../skill-set-improvement-plan.md#7-workstream-b-close-the-four-canonical-routing-gaps); §16 Change 3; §17 file-change-map rows

## Decision

Add at least one distinct development pair and one frozen holdout pair for each missing skill. A pair contains the positive owner case and the nearest-neighbor negative case. Prompts must use user language rather than copied skill-description phrases.

| Target skill | Primary competitor | Positive boundary | Negative boundary |
|---|---|---|---|
| `bdi-mental-states` | `memory-systems` | beliefs, desires, intentions, rational traces, or RDF-to-belief transformation | persistence, retrieval, temporal memory, or entity consolidation without an agency-state model |
| `latent-briefing` | `context-optimization` | representation-level cross-agent compression with real KV/activation access | prompt, retrieval, partitioning, or token-budget optimization through ordinary APIs |
| `long-horizon-prompting` | `harness-engineering` | launch brief for an autonomous or parallel attack: exact success predicate, non-counting outcomes, persistence, stop/return contract, and adversarial audit | runtime loop controls, locked surfaces, logs, rollback, approvals, or execution governance |
| `lossless-doc-compress` | `simplified-engineering-english` | remove only provable redundancy while preserving every fact, qualifier, number, and caveat, with a removal log | rewrite engineering prose for actionability and lower ambiguity without a lossless-compression deliverable |

Each case must:

- name both competitors in `available_skills` and `evaluated_skills`;
- contain a critical exact-route check;
- contain a critical check against selecting the competitor where the boundary is exclusive;
- define observable success and prohibited outcomes;
- avoid vocabulary that makes the answer a string match;
- differ materially between development and holdout prompts;
- use the repository's existing routing schema rather than importing upstream-only fields.

Acceptance: generated canonical development-and-holdout routing coverage is 25 of 25, with no critical regression in existing routing cases.

### §16 Change 3: Four routing gaps

- add development and holdout pairs for the four missing skills;
- run canonical routing baseline and treatment comparisons.

**Exit:** canonical development-and-holdout routing coverage is 25 of 25.

### §17 file-change-map rows

| Path | Action | Required content | Verification |
|---|---|---|---|
| `evals/cases/routing-development.jsonl` | Update | four development routing pairs | eval validator and live run |
| `evals/cases/routing-holdout.jsonl` | Update | four independent holdout pairs | eval validator and guarded frozen run |

## Evidence

- [evals/cases/routing-development.jsonl](../../evals/cases/routing-development.jsonl) and [evals/cases/routing-holdout.jsonl](../../evals/cases/routing-holdout.jsonl): every one of the 25 root skills is a `target_skill` in both files; `python3 evals/validate.py` passes, and it fails any enabled skill lacking canonical development and holdout coverage (validator rule 12).
- `evals/results/catalog-routing-home-v1/development-baseline` and `development-treatment`: 102/102 critical passes each (`openai-codex/gpt-5.6-sol`, 3 attempts, `routing-development.jsonl`).
- Caveat: no guarded routing-holdout comparison result is in the repository, and [evals/baselines/catalog-evidence-status.json](../../evals/baselines/catalog-evidence-status.json) records no accepted live catalog-level gate result for these skills. That gate belongs to Workstream C (§8) and the catalog release gate (§18.3), not to this coverage criterion.
