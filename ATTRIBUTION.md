# Skill Sources and License Scope

This repository contains original work, imported skills, and adaptations.
The root [MIT license](LICENSE) covers repository-original material only.
Imported material keeps its source notice below.

## Context Engineering Skills

Source: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering

Fetched commit: `58b55a8921758d13453b440704fb1b5b208c0b0e` (upstream v2.6.0,
synced 2026-10-06). The original import used
`c578e85e40fe2bda7c1fec91ff64cf5285434934`. Between the two commits, upstream
changed 12 of the 17 imported skills not at all. From the remaining changes,
this repository adopted the retired-model-ID fix in
`skills/project-development/scripts/pipeline_template.py` and the prefix-cache edit
cost sentence in `context-optimization`. It did not import the new
`self-managed-context` skill or the routing lines that point to it; see
[conditional skill decisions](docs/conditional-skill-decisions.md#self-managed-context).

Copyright (c) 2025 Context Engineering Agent Skills Contributors. Imported
materials are provided under the MIT License; see
[LICENSE-context-engineering](LICENSE-context-engineering).

Import scope: the 17 direct child skill directories from upstream `skills/`,
including their `SKILL.md` files, references, and illustrative scripts.
Upstream plugin, researcher, and examples infrastructure was excluded.

Import date: 2026-07-18.

## ML System Design Skills

Source: https://github.com/ML-SystemDesign/MLSystemDesign

The following local skills contain material from the named source snapshots:

| Local skill | Source path | Source commit | Adaptation |
|---|---|---|---|
| `lossless-doc-compress` | `skills/lossless-doc-compress` | `61b9bcdb971e7424cdc4d400085338dc35da910e` | Modified (hedging examples, self-check, templates, exclusions; 2026-10-06) |
| `ml-system-design-review` | `skills/ml-system-design-review` | `90830cd7e52dc2cd6ff2a0d69d96f042759d3430` | Modified (metadata; rubric and pass^k additions, 2026-10-06) |
| `ai-stage-gate` | `skills/ai-stage-gate` | `e439d91dbbd6a303115e42a6b9545563a7c4641f` | Modified metadata |

The upstream repository distributes these skills under the MIT License. Keep
the upstream notice in
[LICENSE-ml-system-design](LICENSE-ml-system-design). The exact
`lossless-doc-compress` snapshot includes that license. The license file was
added after the other two named source snapshots, at upstream commit
`d330164abcfe296330180962a5b8a92aeb736842`. This record distinguishes the
content snapshot from the later repository license record.

The `ai-stage-gate` source also credits Hushpar as conceptual inspiration. No
Hushpar code or license grant is asserted here.

## Leancode Skills

The four Leancode skills first appear in local commit
`e929566264f23040891a2c4c521d3e9110869bf5`, authored and committed by
`lafin` on 2026-07-18T22:17:02+03:00. That commit has no source note or
co-author trailer for these files.

`skills/leancode/SKILL.md` shares wording and the four-principle structure with
`multica-ai/andrej-karpathy-skills` at commit
`8462496b34419f20b32778610571ac723e91f94c`, authored and committed by
Jiayuan Zhang on 2026-01-27T03:53:00Z. The external commit message describes
the file as Karpathy-inspired and has a `Co-Authored-By: Claude Opus 4.5`
trailer.

A trimmed-line comparison between those two first snapshots found these 21
distinct exact lines:

- `## 1. Think Before Coding`
- `Don't assume. Don't hide confusion. Surface tradeoffs.` (bold in both)
- `If a simpler approach exists, say so. Push back when warranted.`
- `If something is unclear, stop. Name what's confusing. Ask.`
- `## 2. Simplicity First`
- `Minimum code that solves the problem. Nothing speculative.` (bold in both)
- `## 3. Surgical Changes`
- `Touch only what you must. Clean up only your own mess.` (bold in both)
- `When editing existing code:`
- `Don't "improve" adjacent code, comments, or formatting.`
- `Don't refactor things that aren't broken.`
- `Match existing style, even if you'd do it differently.`
- `When your changes create orphans:`
- `Remove imports/variables/functions that YOUR changes made unused.`
- `Don't remove pre-existing dead code unless asked.`
- `## 4. Goal-Driven Execution`
- `Define success criteria. Loop until verified.` (bold in both)
- `Transform tasks into verifiable goals:`
- `1. [Step] → verify: [check]`
- `2. [Step] → verify: [check]`
- `3. [Step] → verify: [check]`

The external snapshot predates the local commit, but the available history
does not establish copying direction. The external repository and both
implementations cite Andrej Karpathy's public observations as inspiration.
The external repository declares MIT in its README and skill metadata but
does not contain a complete license notice at the inspected commit. This
repository licenses its local Leancode material under the root MIT license
without asserting ownership of third-party wording.

No substantive external match was found for `leancode-review`,
`leancode-audit` (merged into `leancode-review`), or `leancode-debt`.

## Addy Osmani Agent Skills Adaptations

`skills/source-driven-development` and `skills/api-and-interface-design`
(admitted) adapt the matching `skills/<name>/SKILL.md` files from
https://github.com/addyosmani/agent-skills, originally at commit
`be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39`, re-reviewed at
`aeac41d4d005999432bb7312f7ff06383a91d59d` (2026-10-26). The only delta in
either source path is `throw;` → `throw e;` in the upstream JavaScript
idempotency example; not applicable, because the local skill replaced that
example with language-neutral pseudocode. The rejected
`deprecation-and-migration` proposal is retained at git tag
`admit/deprecation-and-migration-treatment`. The upstream MIT notice is
preserved in [LICENSE-addy-agent-skills](LICENSE-addy-agent-skills).

## ECC Adaptations

Material below is adapted from https://github.com/affaan-m/ECC at commit
`4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2`. Each adapted reference file names
its source path in a provenance header. Upstream paths are given as URLs at
that commit. The upstream MIT notice is preserved in [LICENSE-ecc](LICENSE-ecc).

- `skills/security-review/` (admitted): modified from
  https://github.com/affaan-m/ECC/blob/4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2/skills/security-review/SKILL.md
  and https://github.com/affaan-m/ECC/blob/4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2/skills/security-review/cloud-infrastructure-security.md.
- `deprecation-and-migration/references/database-migrations.md` (rejected
  proposal, git tag `admit/deprecation-and-migration-treatment`): modified from
  https://github.com/affaan-m/ECC/blob/4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2/skills/database-migrations/SKILL.md.
- `skills/source-driven-development/SKILL.md` step 0 and the
  adopt / extend / build decision (admitted): inspired by
  https://github.com/affaan-m/ECC/blob/4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2/skills/search-first/SKILL.md.

## Autoresearch Skill

Source: https://github.com/uditgoenka/autoresearch

Pinned commit: `050e30dc4ba0974b03f2873111b9901ec3211390` (upstream v2.2.2).

Copyright (c) 2026 Udit Goenka. Imported material is provided under the MIT
License; see [LICENSE-autoresearch](LICENSE-autoresearch).

Import scope: `.claude/skills/autoresearch/` (`SKILL.md`, references),
`.claude/commands/autoresearch.md` and `.claude/commands/autoresearch/*.md`,
scripts/orchestrate.sh, scripts/score-regression.sh,
tests/test-orchestrator.sh, tests/test-regression.sh, and their fixtures.
These became `skills/autoresearch/`, `commands/autoresearch.md`, and Python
helpers and `unittest` tests under `skills/autoresearch/`.

Adaptation: modified. Frontmatter reduced to OMP-valid keys; the 13
subcommand commands became `skills/autoresearch/references/*.md` behind one
`/autoresearch <subcommand>` command; repeated blocks moved to
`skills/autoresearch/references/contracts.md`; host tool names and paths rewritten to
model-neutral wording and `skill://` URIs; helpers ported from Bash to Python
with documented contract fixes; the simplify gate in `ship` became a
`git diff --numstat` size check routed to `leancode-review`. The `security`
subcommand became a bounded loop over the repository `security-review`
procedure (metric: trust boundaries checked); the upstream OWASP 2021 and
STRIDE composite score and `security-checklist.md` were dropped. The run guard
is a repository hook (`hooks/pre/autoresearch.ts`) instead of the upstream
hooks.

Dropped surfaces: other-harness distributions and mirrors (`claude-plugin/`,
`plugins/`, `.agents/`, `.opencode/`, `.claude-plugin/`), the Claude hook
layer (`.claude/hooks/autoresearch/`), install, transform, and release
scripts, .github/preprgate/ and its workflow, scripts/score-debug-fix.sh,
`.claude/skills/.env.example`, hook and maintenance tests, and upstream
README, `guide/`, `docs/`, and context files.

## Simplified Engineering English

`simplified-engineering-english` is repository-original material inspired by
ASD-STE100 Issue 9, published in January 2025:
https://asd-ste100.org/

ASD owns ASD-STE100. The local skill adapts controlled-language concepts and
does not distribute the standard or its dictionary. The root MIT license
covers only the local adaptation.

## UI Craft Skill

`skills/ui-craft/` is inspired by Jakub Krehel's Interface Cheat Sheet
(https://interfaces.dev/cheat-sheet, fetched 2026-10-21) and
https://github.com/jakubkrehel/make-interfaces-feel-better at commit
`35545ea1512ad59fa463e6b1f95ca9c052981fe6` (MIT). Rules and values are
restated in this repository's own words; no upstream text or files were
imported. Paid Interfaces issues were not used.

The 2026-10-24 update also draws rules, thresholds, and detection signals
from https://github.com/pbakaus/impeccable at commit
`936867543ac2576920d663cc9803597f6044f3ac` (Apache-2.0; `skill/reference/`,
`crates/foundation/src/registry.rs`) and https://github.com/Nutlope/hallmark
at commit `7ec868225c6caa040558c321ee0fefa0e73f83a8` (MIT;
`skills/hallmark/references/`, `skills/hallmark/scripts/sloplint.mjs`).
Rules are restated in this repository's own words and recipes are written
fresh; no upstream text, code, or files were imported, so neither license's
notice requirement is triggered.
