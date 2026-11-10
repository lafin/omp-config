# Skill anatomy guides, cross-skill asset migration, objective validation, and catalog audit

- **Status:** Completed
- **Date:** catalog anatomy audit 2026-09-16; cross-skill asset migration complete 2026-10-06
- **Source:** [Skill Set Improvement Plan §10 Workstream E: Skill Anatomy, Contributor Guidance, and Objective Validation](../skill-set-improvement-plan.md#10-workstream-e-skill-anatomy-contributor-guidance-and-objective-validation) (§10.1 action, §10.4, §10.6, §10.7, §10.8); §15.2; §16 Change 4; §17 file-change-map rows

## Decision

The anatomy content contract (§10.1), description guidance (§10.2), progressive disclosure (§10.3), script convention (§10.5), and the §10.6 limit on static checks remain in the plan as standing rules for new and changed skills. The completed work below moved here.

### §10.1 Contributor documentation

Add `CONTRIBUTING.md` and `docs/skill-anatomy.md`, then link both from the [README](../../README.md).

### §10.4 Cross-skill asset migration

Status (2026-10-06): complete. No `skill://project-development/references/...` link remains in `evaluation`, `multi-agent-patterns`, or `tool-design`, and the validator rejects cross-skill asset URIs (`cross-skill-asset`). The original requirement was: six asset links made three skills depend on `project-development/references/case-studies.md`: `evaluation` had one, `multi-agent-patterns` three, and `tool-design` two. A standalone install of any of those skills lost cited evidence.

For each link, copy only the needed evidence into an owning skill-local reference, including the original source URL and date, or remove the claim. Do not create a root-shared evidence file. Bare references to another skill owner may remain, but a path such as `skill://other-skill/references/file.md` may not.

Extend the validator to reject cross-skill asset URIs while allowing `skill://<current-skill>/...` and bare owner references such as `skill://other-skill`. Inventory and remove all existing violations before making the rule a release gate.

§15.2 recorded the same result: the six cross-skill asset links from `evaluation`, `multi-agent-patterns`, and `tool-design` into `project-development/references/case-studies.md` were migrated under Workstream E (complete as of 2026-10-06), and validation fails future cross-skill asset URIs.

### §10.6 Extend `scripts/validate_skills.py`

Add hard errors only for objective rules:

- directory and frontmatter `name` use lower-case kebab case;
- directory and frontmatter names match;
- description length is at most 1,024 characters;
- asset URIs may not traverse from one skill into another skill's files;
- existing provenance, revision, license, link, fragment, Python syntax, dependency, and README inventory checks continue to pass.

Add a warning, not an error, when `SKILL.md` exceeds 500 lines.

Do not add static checks that pretend to prove trigger quality, exclusion completeness, workflow correctness, exit-evidence adequacy, or semantic overlap. Those belong to contributor review and live evaluation.

### §10.7 Catalog-wide manual conformance audit

Record a manual audit of all 25 existing skills against the eight anatomy concepts in Section 10.1 and of every script-owning skill against the five operational fields in Section 10.5. The audit must identify the reviewer, skill, concept or field, evidence location, and disposition. Remediate every gap without imposing cosmetic headings. The audit is complete only when every in-scope skill and script-owning skill has a recorded review and no anatomy or script-convention gap remains open.

### §10.8 Tests

Extend `tests/test_validate_skills.py` with focused cases for:

- invalid directory name;
- invalid frontmatter name;
- description over 1,024 characters;
- a body over 500 lines producing a warning without failure;
- a valid boundary case at exactly 1,024 characters;
- a cross-skill asset URI failing while an owning-skill asset URI and a bare adjacent-owner reference pass.

Keep the tests fixture-based and deterministic.

### §16 Change 4: Anatomy, portability, and objective validation

- add contributor and anatomy guides;
- audit all 25 existing skills against the anatomy contract and every script-owning skill against the script convention;
- remediate every recorded semantic gap;
- migrate the six cross-skill asset links into owning skill-local evidence;
- update README links;
- add kebab-case, 1,024-character, cross-skill asset, and 500-line warning checks;
- add focused validator tests.

**Exit:** objective rules pass, every audit row has a disposition, no anatomy or script-convention gap remains open, each current skill is independently installable, and semantic rules remain explicitly review-based.

### §17 file-change-map rows

| Path | Action | Required content | Verification |
|---|---|---|---|
| `CONTRIBUTING.md` | Add | authoring, provenance, evaluation, and review process | link validation |
| `docs/skill-anatomy.md` | Add | flexible anatomy and progressive disclosure | contributor review |
| all 25 existing skill directories | Audit; update only recorded gaps | anatomy conformance and script convention where applicable | recorded catalog-wide manual review |
| `evaluation/SKILL.md`, `multi-agent-patterns/SKILL.md`, `tool-design/SKILL.md` | Done (2026-10-06) | remove six cross-skill asset dependencies without losing cited evidence | skill validator and standalone-install review |
| `scripts/validate_skills.py` | Update | objective name, description, body-size, and cross-skill asset rules | validator tests |
| `tests/test_validate_skills.py` | Update | new hard-error, portability, and warning boundaries | focused unit tests |

## Evidence

- [CONTRIBUTING.md](../../CONTRIBUTING.md) and [docs/skill-anatomy.md](../skill-anatomy.md), linked from [README.md](../../README.md).
- [docs/catalog-skill-anatomy-audit.md](../catalog-skill-anatomy-audit.md): review date 2026-09-16; 25 of 25 skills pass all applicable anatomy concepts; all 12 script owners pass all five operational fields; no gap remains open.
- Migrated evidence: [skills/evaluation/references/multi-agent-research-evidence.md](../../skills/evaluation/references/multi-agent-research-evidence.md), [skills/multi-agent-patterns/references/multi-agent-research-evidence.md](../../skills/multi-agent-patterns/references/multi-agent-research-evidence.md), [skills/tool-design/references/d0-evidence.md](../../skills/tool-design/references/d0-evidence.md).
- [scripts/validate_skills.py](../../scripts/validate_skills.py): `MAX_DESCRIPTION_LENGTH = 1_024`, `MAX_SKILL_LINES = 500`, `metadata-name-format`, `skill-directory-name`, `cross-skill-asset`.
- [tests/test_validate_skills.py](../../tests/test_validate_skills.py): `test_rejects_invalid_directory_name`, `test_rejects_invalid_frontmatter_name`, `test_accepts_description_at_1024_characters`, `test_rejects_description_over_1024_characters`, `test_warns_without_failure_when_skill_exceeds_500_lines`, `test_rejects_cross_skill_asset_but_allows_local_asset_and_bare_owner`.
- [tests/test_script_contracts.py](../../tests/test_script_contracts.py): script operational-contract checks cited by the audit.
