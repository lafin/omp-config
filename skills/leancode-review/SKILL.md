---
name: leancode-review
description: >
  Code review focused exclusively on over-engineering, for a diff or a whole
  repository. Finds what to delete: reinvented standard library, unneeded
  dependencies, speculative abstractions, dead flexibility, drive-by
  refactoring. One line per finding: location, what to cut, what replaces it.
  Use when the user says "review for over-engineering", "what can we delete",
  "is this over-engineered", "simplify review", "audit this codebase for bloat",
  "find bloat", or invokes /skill:leancode-review. Complements
  correctness-focused review, this one only hunts complexity.
license: MIT
metadata:
  provenance: repository-original
---

Review a diff or a whole repository for unnecessary complexity. One line per
finding: location, what to cut, what replaces it. The best outcome is a shorter
codebase.

## Scope

- **Diff** (default): review only the changed lines and their direct callers.
- **Repository**: when the user asks to audit the codebase, repo, or tree
  rather than a change. Rank findings biggest cut first, drop the `scope:` tag
  (there is no request to compare against), and apply the repository rules
  below.

### Repository rules

- Exclude dependencies, generated code, build artifacts, and lockfiles unless
  the user asks to audit that surface. State which paths were scanned.
- If the repository already has a dead-code analyzer (for example knip or
  vulture), run it and cite its output. Do not install one without asking.
- Confirm each `delete:` with a reference search. File size alone is not a
  finding; each finding names its evidence (callers, references, analyzer
  output).
- Hunt: deps the stdlib or platform already ships, single-implementation
  interfaces, factories with one product, wrappers that only delegate, modules
  whose single export has a single caller, dead flags and config, fallbacks for
  states internal code cannot reach, comments that restate the code.

## Format

`L<line>: <tag> <what>. <replacement>.`, or `<file>:L<line>: ...` for
multi-file diffs. Repository scope: `<tag> <what to cut>. <replacement>. [path]`,
ranked biggest cut first.

Tags:

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.
- `scope:` change unrelated to the request, drive-by refactor, restyle, added type hints. Revert it.

## Examples

❌ "This EmailValidator class might be more complex than necessary, have you
considered whether all these validation rules are needed at this stage?"

✅ `L12-38: stdlib: 27-line validator class. "@" in email, 1 line, real validation is the confirmation mail.`

✅ `L4: native: moment.js imported for one format call. Intl.DateTimeFormat, 0 deps.`

✅ `repo.py:L88: yagni: AbstractRepository with one implementation. Inline it until a second one exists.`

✅ `L52-71: delete: retry wrapper around an idempotent local call. Nothing replaces it.`

✅ `L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line.`

✅ `L7: scope: quote-style change in an unrelated function. Revert, not part of this fix.`

## Scoring

End with `net: -<N> lines possible.` Repository scope: `net: -<N> lines, -<M> deps possible.`

If there is nothing to cut, say `Lean already. Ship.` and stop.

## Boundaries

Complexity and scope creep only, correctness bugs, security holes, and
performance go to a normal review pass, not this one. Never flag for deletion:
a smoke test or `assert`-based self-check (the leancode minimum, not bloat),
validation at trust boundaries, error handling that prevents data loss,
security or accessibility code, or anything the request required. Does not
apply the fixes, only lists them.
