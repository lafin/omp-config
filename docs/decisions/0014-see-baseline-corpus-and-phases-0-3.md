# SEE Baseline, Evaluation Corpus, and Implementation Phases 0–3

- **Status:** Completed
- **Date:** not stated (candidate freeze V24 `frozen_at` 2026-09-11T18:54:50Z; commit `50cf61c` 2026-09-12)
- **Source:** [Simplified Engineering English Improvement Plan §12.2–§12.3 and §13 Phases 0–3](../simplified-engineering-english-improvement-plan.md#13-implementation-sequence)

## Decision

The baseline was frozen before production edits, the behavior and routing corpora were built, and Phases 0–3 were implemented. The combined candidate was evaluated through remediation iterations V1–V24 (see the [release report](../../evals/results/see-improvement/release-report.md) "Iteration Disposition"). Phases 4–6 and release remain open in the plan.

### Former §1 precondition

"Do not change the production skill until a valid baseline exists. Current repository evidence covers skill routing only. It does not establish that the skill improves prose or preserves technical contracts." Satisfied: the baseline was captured before treatment; behavior evidence now exists (development 29/42 → 42/42, holdout 24/36 → 36/36 deterministic, local captures only).

### §12.2 Behavior corpus

Twelve initial transformation cases across four families:

- *Procedure and runbook* — ordinary: vague actors, mixed terminology, missing expected result; adversarial: destructive command, warning placement, protected command, and required negative prohibition; no-op: an already precise read-only diagnostic procedure.
- *Requirement and API contract* — ordinary: vague performance and compound obligations; adversarial: valid `MUST NOT`, valid `SHOULD`, EARS-incompatible quality constraint, and multiple verification methods; no-op: an atomic measurable requirement with correct BCP 14 force.
- *Explanation and ADR* — ordinary: mixed mechanism and rationale, floating version reference, and terminology drift; adversarial: legitimate passive voice, future asynchronous behavior, and a required qualification; no-op: a concise version-scoped explanation.
- *Error and incident record* — ordinary: vague error with no affected input or next action; adversarial: actionable local path, sensitive server path, uncertain cause, quoted logs, and an inaccessible visual-only cue; no-op: a safe error plus a fact-only incident timeline.

Delivered: `evals/cases/see-behavior-development.jsonl` (14 cases), `evals/cases/see-behavior-holdout-final.jsonl` (6), `evals/cases/see-behavior-independent-holdout-v21.jsonl` (12: four families × ordinary/adversarial/no-op), `evals/cases/see-behavior-release-holdout.jsonl` (6); historical versions retained and classified in `evals/suites.json`.

### §12.3 Routing corpus

At least eight cases: four positive cases spanning distinct SEE artifacts; four negative cases that belong to adjacent skills. Comparisons with `lossless-doc-compress` (information-preserving compression), `evaluation` (evaluation-system design), `tool-design` (tool-interface contracts), `leancode` (implementation minimality), `ml-system-design-review` (architecture-quality review), and general code-review skills (source-code correctness). A routing case must test the frontmatter description and must not require the full skill to run.

Delivered: `evals/cases/see-routing-development.jsonl` (10 cases: pairs against `lossless-doc-compress`, `evaluation`, `tool-design`, `leancode`, `ml-system-design-review`), `evals/cases/see-routing-holdout.jsonl` (8: `ml-system-design-review`, `context-compression`, `project-development`, `leancode-review`), `evals/cases/see-routing-independent-holdout.jsonl` (12).

### Phase 0: Baseline and rule inventory

Files: `evals/cases/see-behavior-development.jsonl`, `evals/cases/see-behavior-holdout.jsonl`, existing routing case files, `evals/run.py` and `evals/grade.py` only if the schemas could not express required checks.

Work: (1) inventory every rule and assign a provisional authority category, profile, severity, and enforcement class; (2) create the twelve transformation cases and eight routing cases; (3) freeze development and holdout splits; (4) add deterministic preservation checks; (5) capture the unmodified baseline with at least three attempts per case; (6) grade and retain the baseline.

Exit criteria: every case has an immutable manifest; critical preservation properties have deterministic checks; baseline artifacts satisfy `evals/README.md`; no production skill or dictionary text changed.

### Phase 1: Correctness and precedence

Files: `SKILL.md`, `references/dictionary.md`. Work: (1) add the technical-preservation invariant; (2) add rule precedence; (3) repair the path, `now`, `stale`, `default`, and `surface` conflicts; (4) correct the origin and attribution wording; (5) remove or mark unsupported superlatives and efficacy claims; (6) correct BCP 14 semantics and add `NOT RECOMMENDED`; (7) correct EARS syntax and scope; (8) replace test-only verification language. Check: run the focused development corpus; inspect every technical-fidelity and obligation-force result; do not use holdout results to tune this phase. Exit criteria: zero critical preservation regressions; all direct contradictions removed; source requirements and SEE adaptations distinguishable; development results improve or remain non-inferior on every critical dimension.

### Phase 2: Profiles and progressive disclosure

Files: `SKILL.md`, `references/rules.md`. Work: (1) add strict and engineering-default profiles; (2) add compact artifact cards; (3) move detailed rules into `references/rules.md`; (4) classify each rule as error, warning, suggestion, or project choice; (5) add source relationship and enforcement metadata; (6) clarify ambiguity reporting and companion-skill routing. Check: compare with the accepted Phase 1 candidate; measure quality and token changes independently; test mixed artifacts that combine a procedure with explanation or a contract with rationale. Exit criteria: profile selection is deterministic for the evaluation corpus; strict-profile controls remain available; engineering-default rewrites do not apply strict house style without selection; any claimed context-cost reduction is supported by paired evidence (no cost reduction is claimed; behavior token cost rose by +232,337 development and +200,547 holdout).

### Phase 3: Dictionary and glossary governance

Files: `references/dictionary.md`; a project glossary schema or fixture only if the evaluation requires it. Work: (1) keep material cross-domain distinctions; (2) mark ecosystem-dependent definitions as defaults; (3) add authoritative override precedence; (4) correct false absolutes in performance and architecture terms; (5) define the project glossary fields; (6) separate semantic glossary data from Vale-compatible accepted and rejected expressions; (7) define exemption and redaction precedence. Check: cases where two confusable terms are both correct; cases where a platform specification overrides an SEE default; cases where the project glossary replaces a general term. Exit criteria: the dictionary does not force terminology that contradicts an authoritative ecosystem; automatic checks enforce only the fields they can observe; semantic definitions remain subject to semantic and technical review.

### Caveat

The release report does not show separate Phase 1, 2, and 3 paired comparisons; the retained evidence evaluates the combined candidate across remediation iterations.

## Evidence

- [evals/suites.json](../../evals/suites.json)
- [evals/cases/see-behavior-development.jsonl](../../evals/cases/see-behavior-development.jsonl), [see-behavior-independent-holdout-v21.jsonl](../../evals/cases/see-behavior-independent-holdout-v21.jsonl), [see-routing-development.jsonl](../../evals/cases/see-routing-development.jsonl)
- [evals/results/see-improvement/remediation-freeze-v24.json](../../evals/results/see-improvement/remediation-freeze-v24.json), [remediation-holdout-freeze-v24.json](../../evals/results/see-improvement/remediation-holdout-freeze-v24.json)
- [evals/results/see-improvement/paired-results.json](../../evals/results/see-improvement/paired-results.json)
- [skills/simplified-engineering-english/references/rules.md](../../skills/simplified-engineering-english/references/rules.md) "Legacy Rule Inventory"
- `tests/test_evaluation_harness.py` (`test_see_case_manifest_and_exact_preservation_checks`, `test_see_semantic_regression_checks_reject_known_omissions`)
