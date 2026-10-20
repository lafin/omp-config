---
description: Run bounded modify, verify, keep-or-revert loops toward a mechanical metric, or one of the autoresearch subcommands.
argument-hint: "[<subcommand>] [Goal:|Metric:|Verify:|Scope:|Guard:|Iterations:] ..."
---

# /autoresearch

Invocation: `/autoresearch [<subcommand>] [Goal:|Metric:|Verify:|Scope:|Guard:|Iterations:] ...`

Subcommands: `plan debug fix security ship scenario predict learn reason probe evals improve regression`.

Examples:

- `/autoresearch Goal: reduce bundle size Verify: ./scripts/size.sh Scope: src/** Iterations: 15`
- `/autoresearch fix Target: npm test Iterations: 20`
- `/autoresearch regression Base: main`

## Procedure

Read `skill://autoresearch`. Parse only `$ARGUMENTS`.

If the first word of `$ARGUMENTS` is one of `plan debug fix security ship scenario predict learn reason probe evals improve regression`, read `skill://autoresearch/references/<word>.md` and `skill://autoresearch/references/contracts.md`, and pass the remaining arguments to that subcommand.

Otherwise run the core loop or orchestrator from `skill://autoresearch/references/loop.md` with all arguments.

Follow the safety invariants in the skill. Never push, publish, or deploy without explicit user approval.
