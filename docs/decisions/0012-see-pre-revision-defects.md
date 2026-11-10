# SEE Pre-Revision State and Confirmed Defects

- **Status:** Completed
- **Date:** not stated
- **Source:** [Simplified Engineering English Improvement Plan §3.1 Components and §3.2 Confirmed High-Risk Defects](../simplified-engineering-english-improvement-plan.md#3-current-state)

## Decision

The plan recorded the pre-revision state of `simplified-engineering-english` and the confirmed high-risk defects below. The revised skill corrects every listed defect. Release of the revised skill remains open; see the plan's §14 and the [release report](../../evals/results/see-improvement/release-report.md).

### Pre-revision components (§3.1)

| Component | Path (at the time) | Role (at the time) |
| --- | --- | --- |
| Main skill | `simplified-engineering-english/SKILL.md` | Defined activation, 82 rules, artifact modes, conformance levels, enforcement guidance, and governance. |
| Dictionary | `simplified-engineering-english/references/dictionary.md` | Defined confusable terms, rewrite pairs, part-of-speech locks, procedural verbs, glossary policy, and exemptions. |
| Development routing cases | `evals/cases/routing-development.jsonl` | One positive SEE routing case and one nearby negative case against `leancode`. |
| Holdout routing cases | `evals/cases/routing-holdout.jsonl` | One positive SEE routing case and one nearby negative case against `leancode`. |
| Evaluation runner | `evals/run.py` | Captures real OMP baseline and treatment runs. |
| Evaluation grader | `evals/grade.py` | Deterministic grading, paired gates, token accounting, and optional blinded judgment. |
| Evaluation guide | `evals/README.md` | Immutable run artifacts, baseline and treatment parity, holdout discipline, and efficacy-claim requirements. |
| Repository validator | `scripts/validate_skills.py` | Validates skill structure and repository contracts. |

The skill directory later moved to `skills/simplified-engineering-english/` (commit `d052c8d`).

### Confirmed defects (§3.2) and resolution

**No preservation-first invariant.** Protected spans covered some literal text, but no rule required preservation of all source meaning before stylistic revision. A rewrite could alter a fact, an actor, a condition or exception, a number or unit, a version range, obligation force, uncertainty or epistemic status, causal status, or a security boundary. This was critical because a fluent rewrite can satisfy surface rules while changing a technical contract. Resolved: `SKILL.md` "Preservation Invariant" and `SEE-PRESERVE-01`.

**Direct internal conflicts.**

| Location | Conflict | Required correction | Resolution |
| --- | --- | --- | --- |
| Rule 8.6 and its example | The rule prohibited internal paths. The example included `/etc/app.yaml`. | Distinguish actionable local paths from sensitive server paths and secret-bearing values. | `SEE-DISCLOSE-01`; legacy row `8.6` "corrected local versus server-path policy". |
| Rule 9.1 and dictionary rewrite pairs | Rule 9.1 prohibited `now`. The dictionary replaced "at this point in time" with `now`. | Prefer a version, date, or deletion when time scope matters. Permit ordinary `now` only outside version-sensitive claims. | Dictionary rewrite pair: `now` only for an immediate unambiguous observation or procedure; otherwise a date or version, or delete. |
| Dictionary definition of `stale` | The definition used the prohibited word `now`. | Define the term without violating the time-reference rule. | Defined as correct for an earlier state or time but not for the declared reference state or time. |
| Dictionary part-of-speech rule for `default` | The table excluded verb use and then permitted "defaults to." | Record the permitted intransitive verb sense or prohibit it consistently. | Noun, adjective, and intransitive verb in `defaults to`. |
| Dictionary part-of-speech rule for `surface` | The table prohibited verb use. An earlier explanation said an error may "surface." | Use an approved verb or permit the intended sense consistently. | Noun only; use `display`, `return`, or `result in` as the verb. |
| Core-principle and section-origin claims | The skill said Sections 7 through 9 had no STE equivalent. Section 8 called itself an analogue of STE warnings and cautions. | Describe obligations and evidence as additions, and risk and writing mechanisms as adaptations. | Per-rule source/relationship column in `references/rules.md`. |

**Source and adaptation boundaries were unclear.** The skill combined official ASD-STE100 rules, BCP 14 keyword semantics, EARS syntax, ISO plain-language principles, general developer style guidance, and local SEE policy; a reader could not determine which source required a rule, which rule was adapted, and which was an untested local recommendation. Resolved: every rule record in `references/rules.md` names its source and relationship.

**Requirements guidance combined separate layers.** Section 7 combined obligation force, EARS clause order, atomicity and verification, and rationale placement; it misstated parts of RFC 2119, RFC 8174, and EARS and treated one syntax as a complete requirements-quality system. Resolved: `SEE-BCP14-01`, `SEE-BCP14-02`, `SEE-EARS-01`, `SEE-REQ-01`, `SEE-VERIFY-01`.

**Machine-checkability was overstated.** Level 1 was called fully machine-checkable but included semantic tasks: selecting the correct word sense, resolving ambiguous pronouns, distinguishing an entity from a concept, enforcing part of speech in context, and validating project glossary governance. The Vale mapping assigned capabilities too broadly: `occurrence` counts a configured token; `conditional` relates regular-expression matches; Vale vocabularies enforce accepted and rejected expressions, spelling, and casing. These mechanisms do not establish semantic correctness. Resolved: `SEE-COVERAGE-01` and the "Coverage Declaration" in `references/rules.md`.

## Evidence

- [skills/simplified-engineering-english/SKILL.md](../../skills/simplified-engineering-english/SKILL.md)
- [skills/simplified-engineering-english/references/rules.md](../../skills/simplified-engineering-english/references/rules.md) ("Legacy Rule Inventory", "Coverage Declaration")
- [skills/simplified-engineering-english/references/dictionary.md](../../skills/simplified-engineering-english/references/dictionary.md)
- Commit `50cf61c` (2026-09-12) "Improve simplified engineering English evaluation"
