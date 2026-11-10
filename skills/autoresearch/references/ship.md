# ship: eight-phase ship workflow

Ship anything through checklist, dry-run, approved ship, and verification. Not a metric loop: no iteration bound, no active marker (shipping pushes or publishes only after explicit approval, so no run may hold the git guard). Shared blocks: `skill://autoresearch/references/contracts.md`.

## Arguments

- `Target:` or `--target` — what to ship (path, PR, artifact, deployment).
- `--type <type>` — override auto-detection: `code-pr`, `code-release`, `deployment`, `content`, `docs`, `package`, `config`.
- `--dry-run` — validate everything but do not ship.
- `--auto` — treat approval as given if no errors were found. Never passed by the orchestrator; never applies to deploy, publish, or push to a protected target without the user having asked for it in this invocation.
- `--force` — skip non-critical items (blockers are still enforced).
- `--rollback` — undo the last ship action.
- `--monitor N` — post-ship monitoring for N minutes.
- `--checklist-only` — generate the checklist only; do not execute.
- `--chain`, `--<subcommand>`.

Remaining text is the description of what to ship.

## Setup (if Target or Type is unclear)

1. Auto-detect the ship type from context:
   - uncommitted changes or a PR → `code-pr`
   - version bump or changelog → `code-release`
   - Dockerfile or deploy config → `deployment`
   - markdown or content files → `content`
   - `package.json` version change → `package`
2. If still unclear, ask the user once, batching:
   1. What: code PR, release, deployment, content, docs, package.
   2. Target: current branch, a specific PR, a specific path.
   3. Mode: full workflow, dry-run only, checklist only.

If all are clear, skip setup.

## Phase 1: Identify

Determine the ship type (auto-detected or `--type`), identify the target artifacts, and map to the domain checklist.

## Phase 2: Inventory

Gather everything that will ship: files changed (`git diff`), dependencies affected, config changes, migration files, breaking changes.

### Size gate

Run `git diff --numstat` against the ship base (skip binary rows, whose counts are `-`). Sum added plus deleted lines over the remaining rows. If the sum exceeds 400, recommend `skill://leancode-review` on the diff before shipping and let the user decide; a recommendation is not a blocker.

## Phase 3: Checklist

Generate the domain checklist:

- **Code PR:** tests pass, types check, lint clean, no secrets, PR description, reviewers assigned.
- **Release:** version bumped, changelog updated, migration tested, rollback plan.
- **Deployment:** env vars set, health checks configured, rollback ready, monitoring active.
- **Content:** links valid, images optimized, SEO metadata, spell check.
- **Package:** version bumped, README updated, breaking changes documented, CI green.

With `--checklist-only`, output the checklist and stop.

## Phase 4: Prepare

Execute the pre-ship tasks: run the test suite, type checker, and linter; check the diff for secrets; validate configs. Flag blockers (must fix) versus warnings (can ship with). If blockers exist, STOP, report them, and ask the user to fix.

## Phase 5: Dry-run

With `--dry-run`, and always before an actual ship: simulate the ship action without executing and report what WOULD happen. With `--dry-run`, stop here.

## Phase 6: Ship

REQUIRES EXPLICIT USER APPROVAL (see `--auto`). Execute the ship action:

- Code PR: create or update the PR, request reviewers.
- Release: tag, build, publish.
- Deployment: deploy to the target environment.
- Content: publish to the CMS or platform.

If a regression run precedes this ship, read its `handoff.json` `verdict`: ship only on `STABLE`; `UNSTABLE` or `BASELINE_UNAVAILABLE` is a blocker unless the user explicitly overrides.

## Phase 7: Verify

Post-ship: confirm the artifact is live or accessible, run smoke tests if available, check monitoring for errors. With `--monitor N`, watch for N minutes.

## Phase 8: Log

Create `autoresearch/ship-<YYMMDD>-<HHMM>/` and write:

- `checklist.md` — completed checklist with pass or fail per item.
- `summary.md` — what shipped, verification results.
- `ship-results.tsv` — phase-by-phase log (common columns plus `timestamp`, `phase`; `metric` = checklist items passed; `status` = `pass`, `fail`, `warn`, `skipped`).

## Rollback

With `--rollback`: identify the last ship action from the most recent ship log, reverse it (revert the PR, unpublish, roll back the deployment), and verify the rollback succeeded.

## Finish

Write `handoff.json`: `source: "ship"`, `status` ∈ `COMPLETE`, `DRY_RUN`, `ROLLBACK`, `ERROR`; `findings` = blockers and warnings found during prepare. Then follow `--chain` (contracts).
