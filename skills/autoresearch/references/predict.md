# predict: persona debate before implementation

Five expert personas analyze and debate a proposed change before it is built. Not a looping command: bounded by rounds, no results TSV, no active marker. Read `skill://autoresearch/references/predict-personas.md` for persona definitions, debate protocol, and output formats. Shared blocks: `skill://autoresearch/references/contracts.md`.

## Arguments

- `Scope:` or `--scope` — file globs to analyze.
- `Goal:` or `--goal` — focus area for analysis.
- `Depth:` or `--depth` — shallow (3 personas, 1 round), standard (5, 2), deep (8, 3).
- `--personas N` — override persona count (3-8).
- `--rounds N` — override debate rounds (1-3).
- `--adversarial` — use the hostile reviewer personas instead of the default set.
- `--budget N` — maximum findings across all personas (default 40).
- `--fail-on <severity>` — CI gate: report non-zero status if findings at or above the threshold exist.
- `--incremental` — reuse existing knowledge files, update only changed files.
- `--chain`, `--<subcommand>`.

Remaining text not matching flags is the goal description.

## Setup (if Scope or Goal is missing)

Ask the user once, batching:

1. Scope: which files to analyze? Suggested globs plus the entire codebase.
2. Goal: what should personas focus on? Code quality, security, performance, architecture, all.
3. Depth: shallow (3 personas, 1 round), standard (5, 2; recommended), deep (8, 3).
4. Chain: after analysis, chain to debug, security, fix, ship, scenario, or no chain.

If all are provided, skip setup.

## Phase 1: Reconnaissance

Scan all in-scope files and build structured knowledge: file inventory with purpose annotations, dependency graph (imports and exports), API surface (routes, handlers, types), data flow (inputs → processing → outputs → storage), existing test coverage map.

## Phase 2: Persona generation

Default set (5): Architect, Security Analyst, Performance Engineer, Reliability Engineer, Devil's Advocate. Adversarial set (`--adversarial`): Breaker, Cheater, Scaler, Newbie, Malicious Insider.

Each persona receives the task description, the codebase knowledge, and its own evaluation criteria. Personas are isolated: no shared context between them. Where the host supports isolated sub-agents, give each persona its own; otherwise run them sequentially and do not show a persona another's findings until the debate phase.

## Phase 3: Independent analysis

Each persona reads the relevant code through its lens and produces findings: title, severity, confidence (0-100%), `file:line`, recommendation. Maximum findings per persona: `budget / persona_count`.

## Phase 4: Debate (per round)

For each round:

1. Present all personas' findings to each other.
2. Each persona may challenge findings, raise new issues, or change confidence.
3. Cross-examination: personas must answer challenges with evidence.
4. No persona may dismiss a finding without counter-evidence.

## Phase 5: Consensus

The synthesizer aggregates all findings:

1. Deduplicate (same `file:line` and same issue merge; keep the highest severity).
2. Resolve conflicts; where personas disagree, note the dissent.
3. **Anti-herd check:** if all personas agree on everything, the synthesizer MUST find at least one counter-argument.
4. Rank by severity × average confidence × persona agreement count.

## Phase 6: Report

Create `autoresearch/predict-<YYMMDD>-<HHMM>/` and write:

- `summary.md` — top findings, consensus view, risk assessment.
- `debate.md` — full persona analysis and debate transcript, with per-persona sections.

Print the top 10 findings ranked by severity × confidence.

## Phase 7: CI gate

With `--fail-on`, compare findings against the threshold and report a non-zero status if exceeded.

## Finish

Write `handoff.json`: `source: "predict"`, `status` ∈ `COMPLETE`, `ERROR`; `findings` = consensus findings with severity, confidence, `file:line`; `config` = scope, goal, depth. Follow `--chain` (contracts).
