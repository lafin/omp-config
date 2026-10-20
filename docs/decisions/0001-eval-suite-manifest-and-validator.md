# Evaluation suite manifest, structural validator, and safe suite selection

- **Status:** Completed
- **Date:** not stated in source; implementing commit `7529a16` ("Harden skill catalog evaluation and admission gates") is dated 2026-09-16
- **Source:** [Skill Set Improvement Plan §6 Workstream A: Evaluation Suite Manifest and Structural Validator](../skill-set-improvement-plan.md#6-workstream-a-evaluation-suite-manifest-and-structural-validator); §16 Change 1 and Change 2; §17 file-change-map rows

## Decision

The manifest decision, suggested shape, lifecycle matrix, `retired_skills`, and `admission_candidate` rules (§6.2) and the pilot-file and proposal-pin rules (end of §6.3) remain in the plan because they govern open pilot and historical work. The implemented requirements below moved here.

### §6.1 Problem

The [evaluation guide](../../evals/README.md) describes nine canonical suites, but `evals/cases/` contains 25 JSONL files. Versioned, independent, final, and release files are not machine-classified. A contributor can accidentally omit a file, run historical data as active data, duplicate an ID, or report incomplete coverage.

### §6.3 Validator requirements

`evals/validate.py` must fail when:

1. a JSONL file under `evals/cases/` is absent from the manifest or listed more than once;
2. a manifest path does not exist, escapes the repository, or is not under `evals/cases/`;
3. a row is invalid JSON or lacks the fields required by its `kind`;
4. a manifest `kind` or `split` disagrees with a row;
5. case IDs are duplicated within the global active-ID scope;
6. an active-validation row references a `target_skill`, `available_skills`, or `evaluated_skills` entry that is not a current root skill directory;
7. a historical row references a missing skill that is not declared exactly once in `retired_skills`;
8. an active-validation file references a `retired_skills` identity;
9. a canonical routing case omits its target from `available_skills` or `evaluated_skills`;
10. an active-validation routing case lacks a critical exact-route check;
11. an A/B routing pair lacks its reverse case without an explicit, reviewed exception;
12. any enabled skill other than the manifest's sole `admission_candidate` lacks canonical development and holdout coverage as both a target and an evaluated skill, or the candidate lacks canonical development coverage in both roles;
13. a new enabled skill, defined as a current enabled root absent from the catalog at `base_catalog_revision`, lacks the canonical behavior cases required by its admission phase;
14. a file is selected outside the lifecycle matrix, including a historical file without `--allow-historical`, a proposal development file outside proposal-baseline mode, or any `split: holdout` file outside guarded holdout execution;
15. a routing or behavior suite selectable by an execution mode lacks a complete pre-registered comparison contract, or a holdout comparison lacks recorded immutable `baseline_catalog_revision` and `treatment_catalog_revision` values;
16. a proposal file references more than one root absent from the current catalog, or its rows do not consistently use the same single proposed root;
17. independent-holdout or release selection can execute a holdout without satisfying the guarded holdout preconditions;
18. `admission_candidate` is non-null but does not name exactly one current root absent at `base_catalog_revision`, its immutable treatment revision is missing or unresolvable, its current root differs from the root at that revision, or any of its proposal holdout entries is unfrozen or pins a different treatment revision;
19. `admission_candidate` is cleared without full canonical development and holdout coverage for that root, or release selection is attempted while it remains non-null;
20. a historical entry has lost all retained immutable evaluated-catalog revision pins, or a retained pin is unresolvable.

Historical duplicate IDs may remain only when all duplicates are outside the global active-ID scope and the manifest explains their status.

The validator must not call a model, infer semantic trigger quality, or declare a behavior correct from source text.

### §6.4 Runner changes

Extend `evals/run.py` with a suite-oriented entry point:

- normal `--suite <name>` selects only `split: development` files with `canonical` status and rejects any request that would expose a holdout;
- `--mode holdout` is the sole guarded holdout executor. Direct `--suite <name> --mode holdout` or `--cases <path> --mode holdout` entry verifies the locked comparison-contract hash and recorded immutable `baseline_catalog_revision` and `treatment_catalog_revision`, resolves both revisions to isolated catalog roots, runs the selected frozen cases only against those two roots, and never evaluates the working tree;
- `--suite <name> --mode independent-holdout` selects only `independent-holdout` files, and `--mode release` selects the eligible `canonical`, `independent-holdout`, and `release-only` files required by that suite. Both modes must dispatch every `split: holdout` selection to the same guarded holdout executor and fail if its preconditions are unmet;
- existing `--cases <path>` remains an explicit low-level development mode subject to the same lifecycle matrix. It rejects every `split: holdout` file unless combined with `--mode holdout`. A historical development file additionally requires `--allow-historical --historical-catalog baseline|treatment`; the runner selects the requested retained `baseline_catalog_revision` or `treatment_catalog_revision`, fails if that pin is absent or unresolvable, resolves it to an isolated catalog root, and never evaluates the working tree. When both pins exist, the explicit selector permits reproduction of either side;
- `--proposal-baseline <path>` is the only development execution path for a `proposal` file: it requires the manifest entry and frozen file hash, resolves that entry's `baseline_catalog_revision` to an isolated catalog root, and runs only its development cases against that pre-treatment catalog without activating the file, adding coverage, or making the proposed root available. Proposal holdout runs only through guarded holdout mode and may reuse the manifest-pinned baseline and treatment revisions;
- every result manifest records suite and mode, case-file paths and hashes, manifest schema version and hash, case-source revision, comparison-contract path and hash, model, profile, tool configuration, attempt count, effective per-attempt and overall timeout seconds, and each evaluated catalog revision and resolved root. A final holdout manifest always records both immutable baseline and treatment revisions and roots; changing either root or the locked configuration invalidates the pair.

Keep explicit case paths for forensic reproduction. The manifest is an inventory and safe default, not an abstraction that hides evidence.

### §6.5 Repository integration

- document statuses, fields, and commands in the [evaluation guide](../../evals/README.md);
- add focused validator tests, preferably in a new `tests/test_eval_validation.py` rather than expanding the already large evaluation-harness test module;
- add runner-option tests to `tests/test_evaluation_harness.py` only where they exercise runner behavior;
- run `evals/validate.py` in `.github/workflows/validate-skills.yml` after skill validation;
- keep errors actionable: file, row, field, violated invariant, and repair direction.

### §6.6 Acceptance criteria

- all 25 current JSONL files appear exactly once in the manifest;
- status- and split-aware selection follows the lifecycle matrix: normal suites are development-only, and neither `--suite` nor low-level `--cases` can expose a holdout outside guarded holdout mode;
- the immutable base catalog and each proposal's actual pre-treatment catalog resolve from their pinned revisions; proposal files remain outside active coverage, proposal development runs only through proposal-baseline mode, and proposal holdout runs only through the guard after the treatment revision and configuration are frozen;
- coverage numbers are generated only from canonical rows; the sole pending `admission_candidate` validates with canonical development coverage and frozen proposal holdout entries pinned to its immutable treatment revision, but clearing the state and release both require full canonical development and holdout coverage;
- historical development execution requires an explicit retained baseline or treatment pin, resolves only that revision to an isolated root, and fails rather than using the working tree when the selected pin is missing or unresolvable;
- missing files, duplicate IDs in the active-ID scope, unknown or undeclared retired skills, active-validation references to retired skills, split mismatches, absent exact-route checks, invalid lifecycle selection or proposal baseline revision, holdout selection outside the guard, missing or mutable holdout revisions, invalid proposal identity, invalid or multiple admission candidates, candidate pin/root mismatch, candidate-state clearing without full canonical coverage, release with a pending candidate, missing or unresolvable historical pins, and incomplete comparison contracts each have a regression test. Runner regressions must cover early holdout rejection through both `--suite` and `--cases`, guarded delegation from independent-holdout and release modes, and baseline and treatment reproduction for a historical development case without working-tree fallback;
- validation performs no network or model calls.

### §16 Change 1: Evaluation manifest and validator

- add `evals/suites.json`;
- register the complete comparison contract for each execution-selectable routing and behavior suite, including immutable baseline and treatment catalog revisions for every holdout comparison;
- record the immutable `base_catalog_revision`, the nullable single-root `admission_candidate`, and each proposal's actual pre-treatment `baseline_catalog_revision` and later frozen `treatment_catalog_revision`;
- require a candidate's canonical development coverage and matching revision-pinned proposal holdout entries, then full canonical coverage when the state is cleared or release is selected;
- retain immutable evaluated-catalog pins when entries become historical;
- classify all 25 JSONL files;
- add `evals/validate.py` and focused tests;
- update CI and the evaluation guide.

**Exit:** every case file is classified exactly once, pinned catalog revisions resolve deterministically, a valid frozen admission candidate passes without adding proposal holdout to active coverage, historical entries retain their evaluated roots, and existing active-validation data validates.

### §16 Change 2: Safe suite selection

- add lifecycle- and split-aware `--suite`, `--mode`, `--allow-historical`, `--historical-catalog`, `--proposal-baseline`, and guarded holdout behavior to the runner;
- make normal `--suite` and low-level `--cases` development-only, rejecting every holdout outside `--mode holdout`;
- make the holdout guard verify locked comparison configuration and immutable baseline/treatment revisions, evaluate only their isolated roots, and serve proposal, canonical, independent-holdout, release-only, and permitted historical selections;
- make historical development execution require an explicit retained baseline or treatment pin, resolve it to an isolated root, and fail on a missing or unresolvable pin instead of using the working tree;
- route independent-holdout and release holdout selection through that guard rather than around it;
- record every evaluated revision and root, manifest and case hashes, comparison metadata, and effective timeouts in result metadata;
- add runner regressions for early canonical-holdout rejection through both `--suite` and `--cases`, guarded success, independent-holdout/release delegation, and historical baseline/treatment root selection without working-tree fallback.

**Exit:** normal and low-level runs cannot expose holdout data; every holdout execution uses the locked contract and recorded immutable baseline and treatment roots; frozen proposal development data runs only as a pinned, non-covering baseline; historical development runs only against the explicitly selected retained archived root.

### §17 file-change-map rows

| Path | Action | Required content | Verification |
|---|---|---|---|
| `evals/suites.json` | Add | exhaustive case-file lifecycle manifest, nullable single-root admission candidate, immutable baseline and treatment catalog revisions retained for historical reproduction, and suite-specific locked comparison contracts including timeout policy | evaluation validator tests |
| `evals/validate.py` | Add | deterministic schema, path, ID-scope, skill, admission-candidate, historical-pin, proposal-revision, pairing, comparison-contract, split-aware selection, holdout-revision, and coverage checks | direct run and focused unit tests |
| `evals/run.py` | Update | development-only normal selectors, one guarded paired holdout executor over immutable roots, independent/release delegation, explicit retained-root historical development, pinned proposal-baseline execution, and complete result metadata | evaluation harness tests |
| `evals/README.md` | Update | statuses, admission-candidate and archived-pin fields, lifecycle matrix, development-only selectors, guarded holdout sequencing, explicit historical root selection, baseline critical semantics, and evidence policy | link and command review |
| `.github/workflows/validate-skills.yml` | Update | run skill and evaluation validators | workflow syntax and local commands |
| `tests/test_eval_validation.py` | Add | failure cases for all structural invariants, including invalid candidate state, candidate clearing or release without full coverage, absent historical or holdout revisions, and guard bypasses | unit-test discovery |
| `tests/test_evaluation_harness.py` | Update narrowly | normal `--suite` and low-level `--cases` early-holdout rejection, guarded paired execution, independent/release delegation, historical baseline/treatment root selection and failures, proposal development baseline behavior, and result metadata including immutable roots and timeouts | focused unit tests |

## Evidence

- [evals/suites.json](../../evals/suites.json): `schema_version`, `base_catalog_revision` `50cf61c53aea66ebf60d89088b453eadd788d092`, `admission_candidate: null`, `retired_skills: []`, `routing_pair_exceptions`, `comparison_contracts`, and `case_files`. The corpus has grown from 25 to 53 JSONL files; all 53 are classified (15 canonical, 22 proposal, 13 historical, 2 independent-holdout, 1 release-only).
- [evals/validate.py](../../evals/validate.py): `python3 evals/validate.py` reports `validated 53 case files; canonical coverage is derived from canonical rows only`.
- [evals/run.py](../../evals/run.py): `--suite`, `--proposal-baseline`, `--mode development|holdout|independent-holdout|release`, `--allow-historical`, `--historical-catalog baseline|treatment`.
- [tests/test_eval_validation.py](../../tests/test_eval_validation.py) (22 tests) and the selector and locked-contract tests in [tests/test_evaluation_harness.py](../../tests/test_evaluation_harness.py).
- [.github/workflows/validate-skills.yml](../../.github/workflows/validate-skills.yml): "Validate evaluation suites" step runs `python3 evals/validate.py` after `python3 scripts/validate_skills.py`.
- [evals/README.md](../../evals/README.md) § "Manifest lifecycle and selection".
