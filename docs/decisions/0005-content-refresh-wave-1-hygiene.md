# Content Refresh Wave 1: Upstream Sync and Repository Hygiene

- **Status:** Completed
- **Date:** 2026-10-06
- **Source:** [Skill Content Refresh Plan §3 Upstream Drift](../skill-content-refresh-plan.md#3-upstream-drift), [§5 Already Applied](../skill-content-refresh-plan.md#5-already-applied), [§6 Wave 1 — Repository Hygiene](../skill-content-refresh-plan.md#6-wave-1--repository-hygiene)

## Decision

Item locations are baseline-revision (`7529a16`) paths; skill paths were later moved under `skills/`. Wave 1 ran first and changed no skill behavior. Open follow-ups stay in the plan: `RP-6` (upstream contributions, owner decision), `CO-8` (Wave 3 gate), and the `RP-4` revisit trigger.

### Upstream drift (2026-10-06)

| Source | Pinned | Upstream HEAD on 2026-10-06 | Delta that touches local skills | Disposition |
|---|---|---|---|---|
| `muratcankoylan/Agent-Skills-for-Context-Engineering` | `c578e85e40fe2bda7c1fec91ff64cf5285434934` | `58b55a8921758d13453b440704fb1b5b208c0b0e` (v2.6.0) | New `self-managed-context` skill. Reciprocal routing lines in `context-compression`, `context-optimization`, `filesystem-context`, `self-improvement-loops`. One prefix-cache sentence in `context-optimization`. Retired model ID in `project-development/scripts/pipeline_template.py` (commit `0416003a`). Governance, researcher, and schema infrastructure outside `skills/`. | Model ID applied (`PD-0`). Prefix-cache sentence adopted as `CO-8`. Skill import deferred (`RP-4`). Routing lines to the non-imported skill rejected. Infrastructure out of scope per the Section 3.2 non-goals of the skill set plan. |
| `ML-SystemDesign/MLSystemDesign` | per-skill commits in [ATTRIBUTION](../../ATTRIBUTION.md) | `8dd0d88852fe7445e9d2627c59124f0f161040c1` | None under `skills/lossless-doc-compress`, `skills/ml-system-design-review`, or `skills/ai-stage-gate`. | No sync. Local fix `LDC-1` should also go upstream (`RP-6`). |
| `multica-ai/andrej-karpathy-skills` | `8462496b34419f20b32778610571ac723e91f94c` | `2c606141936f1eeef17fa3043a72095b4765b9c2` | `CLAUDE.md` unchanged. New `skills/karpathy-guidelines/SKILL.md` is `CLAUDE.md` plus frontmatter. New `EXAMPLES.md` (~520 lines; Goal-Driven Example 3 has identical ❌ and ✅ bodies). | Nothing to adopt. |
| `addyosmani/agent-skills` | `be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39` | `1401c8b8030e023baeebb31781a6653fe8e93026` | `api-and-interface-design` fixes `throw;` → `throw e;` (absent from the local proposal). `docs/skill-anatomy.md` adds a model-neutral procedure rule and restricts top-level frontmatter keys to the spec set. | Adopt both anatomy rules (`RP-1`). No proposal change needed. |

### Items

- **PD-0** · D · `project-development/scripts/pipeline_template.py:32,278,763` — Replaced retired `claude-sonnet-4-20250514` with `claude-sonnet-4-6`, matching upstream `0416003a`. Verified: `--help` runs and `python3 -m unittest tests.test_script_contracts` passes. Metadata still pinned `c578e85`; `RP-2` resolved that.
- **RP-1** · D · `docs/skill-anatomy.md`, `CONTRIBUTING.md`, `scripts/validate_skills.py`, `tests/test_validate_skills.py`
  - Add the model-neutral rule: a step that cannot be justified without naming a model, model version, or one host's private tool name does not belong in a skill.
  - Add a hard validator error for top-level frontmatter keys outside `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All 25 skills passed this at review time.
  - Add one validator test with a disallowed key.
  - Source: upstream `addyosmani/agent-skills` `docs/skill-anatomy.md` at `1401c8b`; <https://agentskills.io/specification>.
- **RP-2** · D · 17 context-engineering `SKILL.md` frontmatters, `ATTRIBUTION.md`, `README.md`
  - Bump `metadata.upstream_commit` to `58b55a8921758d13453b440704fb1b5b208c0b0e` for all 17 skills. The 12 skills that upstream did not touch have identical upstream content at both commits. The 5 touched skills keep `adaptation: modified`.
  - In `ATTRIBUTION.md`, record the new fetched commit and the drift disposition: adopted `PD-0` and `CO-8`; did not import `self-managed-context` or its reciprocal routing lines.
- **RP-3** (also **LD-1**) · D · `docs/skill-set-improvement-plan.md`
  - §10.4 (baseline line 443), §15.2 (line 729), and the file-change map (line 865): no cross-skill asset links into `project-development/references/case-studies.md` remain in `evaluation`, `multi-agent-patterns`, or `tool-design`. Mark the migration complete.
  - Baseline line 320: replace the `leancode-debt` oracle "extracts only syntactically valid debt markers" with "extracts every `lean-debt:` marker with its ceiling and revisit trigger, flags incomplete markers `no-ceiling` or `no-trigger`, and edits no source". The old text conflicted with `leancode-debt/SKILL.md:41-42`.
- **RP-4** · D · `docs/conditional-skill-decisions.md`
  - Add a `self-managed-context` section. Decision: **DEFER import**.
  - Evidence: the upstream skill is 276 lines, ~3,460 words (near the ~5k-token body ceiling), plus 23 KB of references. Its results rest on one paper (CLM, <https://arxiv.org/abs/2609.37725>, 2026-09-29). OMP exposes no model-editable live context, so no local task needs the skill.
  - Port its three general rules into existing owners instead: edit-position cost (`CO-8`), deterministic budget readouts (`CO-4`), summary text as untrusted data (`CC-4`, `CD-5`).
  - Revisit when a target host exposes model-editable context, or when an independent replication of the CLM results is published. The revisit trigger now lives in [conditional skill decisions](../conditional-skill-decisions.md#self-managed-context).
- **RP-5** · D · `CONTRIBUTING.md` — Add a recurring upstream drift check, run before each catalog release, and record each delta's disposition in `ATTRIBUTION.md`:

  ```sh
  gh api "repos/<owner>/<repo>/compare/<pinned-sha>...HEAD" \
    --jq '.files[] | select(.filename | startswith("skills/")) | "\(.status) \(.filename)"'
  ```

Definition of Done box "Wave 1 items `RP-1` to `RP-5` are merged, and the deterministic checks pass" is checked in the plan's §13.

## Evidence

- `PD-0`: `skills/project-development/scripts/pipeline_template.py:35,281,796` (`claude-sonnet-4-6`).
- `RP-1`: `docs/skill-anatomy.md:22` (model-neutral rule); `scripts/validate_skills.py:35` (`ALLOWED_FRONTMATTER_KEYS`); `tests/test_validate_skills.py:153` (`test_rejects_vendor_key_at_top_level_but_allows_spec_keys`); `CONTRIBUTING.md:12` links the anatomy as the content contract.
- `RP-2`: all 17 context-engineering `skills/*/SKILL.md` carry `upstream_commit: "58b55a8921758d13453b440704fb1b5b208c0b0e"` (line 7), none still pin `c578e85`; `ATTRIBUTION.md:11,18-19`.
- `RP-3`: `docs/skill-set-improvement-plan.md:320` (new `leancode-debt` oracle), `:443` (§10.4 status complete), `:742` (migration complete).
- `RP-4`: `docs/conditional-skill-decisions.md:155-171` (`## Self-managed context`).
- `RP-5`: `CONTRIBUTING.md:53-58`.
