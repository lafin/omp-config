# plan: goal to validated config

Convert a goal into a validated Scope, Metric, Direction, Verify, Guard, and Iterations config. Not a looping command: no results TSV, no active marker. Shared blocks: `skill://autoresearch/references/contracts.md`.

## Arguments

- `Goal:` — text after the keyword, or all remaining invocation text if there is no keyword.
- `--chain <targets>` and `--<subcommand>` shorthand.

Remaining text is the goal description.

## Setup (if Goal is missing)

Ask the user once, batching:

1. Goal: what do you want to achieve? (open text)
2. Type: what kind of goal: improve a metric, fix errors, audit security, explore edge cases, document code, ship something.

If Goal is provided, skip setup.

## Phase 1: Analyze goal

Determine: is it measurable (metric-driven) or subjective; the natural scope (files, modules, whole codebase); which subcommand fits best (core loop, `fix`, `debug`, `security`, and so on).

## Phase 2: Derive scope

1. Scan the project structure.
2. Identify files relevant to the goal.
3. Propose file globs.
4. If ambiguous, ask the user to confirm.

## Phase 3: Derive metric and direction

Metric-driven goals: identify what to measure (test coverage, error count, bundle size, latency, and so on), decide `higher_is_better` or `lower_is_better`, propose a metric name and description.

Subjective goals: suggest proxy metrics where possible, or recommend `skill://autoresearch/references/reason.md` for goals that cannot be measured.

## Phase 4: Derive Verify command

1. Identify how to extract the metric as a number from a shell command.
2. Propose the Verify command (for example `npm test -- --coverage | grep "All files" | awk '{print $10}'`).
3. Safety screen with `screen-cmd` (contracts: Verify safety screen): `rm -rf`, fork bombs, `curl|sh`, credentials.
4. Dry-run the command and confirm it outputs a valid number.
5. If the dry-run fails, adjust the command and retry.

## Phase 5: Derive Guard (optional)

Propose a Guard if applicable: the test suite (`npm test`, `pytest`, `go test ./...`), a type check (`tsc --noEmit`, `mypy`), a build (`npm run build`), or none.

## Phase 6: Suggest iterations

- Simple metric improvement: 10-15.
- Moderate refactoring: 20-25.
- Complex multi-file changes: 30 or more.

Recommend a bounded default and mention the `Iterations: unlimited` option.

## Phase 7: Present config

Output a ready-to-run config block:

```
/autoresearch
Goal: {derived goal}
Scope: {derived globs}
Metric: {derived metric}
Direction: {higher_is_better|lower_is_better}
Verify: {derived command}
Guard: {derived guard or omit}
Iterations: {suggested count}
```

Ask the user: run this config now, or adjust?

## Chain handoff

With `--chain`: write `handoff.json` with `source: "plan"`, `status: "COMPLETE"`, `config` = the derived config block, then invoke the next target with it (contracts: Chain handoff). `plan` writes no active marker.
