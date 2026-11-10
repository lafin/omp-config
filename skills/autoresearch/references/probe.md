# probe: persona interrogation until constraints saturate

Eight personas interrogate a topic or requirement round by round, extracting atomic constraints until new constraints stop appearing. Default 15 rounds. Shared blocks: `skill://autoresearch/references/contracts.md`. A round is a loop iteration.

## Arguments

- `Topic:` — strip the keyword; remaining text is the topic (or all remaining invocation text if there is no keyword).
- `Scope:` or `--scope` — file globs for codebase grounding.
- `Depth:` or `--depth` — shallow (5 rounds), standard (15), deep (30).
- `--personas N` or `Personas:` — active persona count (3-8, default 6).
- `--saturation-threshold N` — net-new constraints per round below which a round counts toward saturation (default 2).
- `--mode` or `Mode:` — `interactive` (default; asks the user) or `autonomous` (self-answers from the codebase).
- `--adversarial` — rotate hostile personas to the front.
- `Iterations:` or `--iterations` — default 15 rounds, or `unlimited`.
- `--evals`, `--evals-interval N`, `--chain`, `--<subcommand>`.

## Setup (if Topic is missing)

Ask the user once, batching:

1. Topic: what to probe? (open text describing a feature, requirement, or design)
2. Scope: which files for context? Suggested globs plus the entire codebase.
3. Depth: shallow (5 rounds), standard (15), deep (30), unlimited.
4. Mode: how to answer persona questions? Interactive (you answer) or autonomous (the agent infers from code).

If all are provided, skip setup.

## 8 personas

| # | Persona | Focus |
|---|---|---|
| 1 | Domain Expert | Business rules, domain constraints, terminology |
| 2 | End User | Usability, expectations, error recovery |
| 3 | Skeptic | Assumptions that might be wrong |
| 4 | Edge-Case Hunter | Boundary conditions, rare scenarios |
| 5 | Ops Engineer | Deployment, monitoring, scaling, failure modes |
| 6 | Security Reviewer | Attack vectors, data protection, auth |
| 7 | Contradiction Finder | Conflicts between requirements |
| 8 | Scope Guardian | Feature creep, unnecessary complexity |

With `--adversarial`: rotate Skeptic, Contradiction Finder, and Edge-Case Hunter to the front.

## Phase 1: Seed

Parse the topic into an initial constraint set, read codebase context (if `--scope` is given), initialize an empty constraint registry. Create `autoresearch/probe-<YYMMDD>-<HHMM>/`; write the active marker (contracts). TSV: `# metric_direction: higher_is_better`, then the common columns plus `timestamp`, `personas`, `questions`, `net_new`. `metric` = total constraints; `status` = `ok` or `saturated`; `commit` is `-`.

## Round loop

### Phase 2: Persona activation

Select 2-3 personas for this round (rotate through all 8). Each generates 3-5 probing questions from its perspective.

### Phase 3: Codebase grounding

Check the questions against existing code for evidence. Annotate each with the relevant `file:line`, existing behavior, and gaps.

### Phase 4: Answer capture

- **Interactive mode:** ask the user the questions and collect answers.
- **Autonomous mode:** infer answers from codebase context and label confidence (high, medium, low). A run that cannot ask must use this mode.

### Phase 5: Constraint extraction

Parse answers into atomic constraints: id, source persona, description, confidence, evidence. Deduplicate against the registry.

### Phase 6: Cross-check

Check new constraints against existing ones for conflicts. Flag contradictions for resolution (interactive: ask the user; autonomous: note the uncertainty).

### Phase 7: Saturation check

Count net-new constraints this round. If net-new is below the saturation threshold for 3 consecutive rounds, the run is SATURATED: exit the loop. Track total constraints, new this round, and the saturation window.

### Phase 8: Log

Append the TSV row (round number, personas active, questions asked, constraints extracted, net-new count).

### Eval checkpoint

Header says `rounds`: `--- Eval Checkpoint (rounds {X}-{Y}) ---`; stats line `Constraints: {total} (+{new}) | Saturation: {window_count}/3`; recommend early stop after 3 or more saturated checkpoints.

### Bounded check

At the bound, exit the loop.

## Phase 9: Synthesize and output

In the run directory:

1. Write `constraints.md` — full constraint registry organized by category.
2. Write `conflicts.md` — unresolved contradictions.
3. Write `summary.md` containing a ready-to-run autoresearch config (derived Goal, Scope, Metric, Verify from the constraints) as a code block.

Print: total rounds, total constraints, net-new trend, saturation status, unresolved conflicts, the top 5 most impactful constraints.

## Finish

Write `handoff.json`: `source: "probe"`, `status` ∈ `COMPLETE`, `SATURATED`, `USER_INTERRUPT`, `BOUNDED`, `ERROR`; `findings` = constraints; `config` = the derived autoresearch config. Delete the active marker, then follow `--chain` (contracts).
