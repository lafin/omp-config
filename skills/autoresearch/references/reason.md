# reason: adversarial debate with blind judges

Refine an answer, proposal, design, or claim through generate → critique → counter → synthesize → blind judging until the incumbent stops changing. Default 8 rounds. Read `skill://autoresearch/references/reason-judge-protocol.md` for judge and convergence specs, critic rules, and domain criteria. Shared blocks: `skill://autoresearch/references/contracts.md`. A round is a loop iteration: the `iteration` TSV column holds the round number.

## Arguments

- `Task:` — question, proposal, design, argument, or claim to refine.
- `Domain:` or `--domain` — software, product, business, security, research, content.
- `Mode:` or `--mode` — `convergent` (default), `creative`, `debate`.
- `--judges N` or `Judges:` — blind judge count (3 default, 5 thorough, 7 deep).
- `--convergence N` or `Convergence:` — stop when the incumbent wins N consecutive rounds (default 3).
- `Rounds:` — round bound (default 8), or `unlimited`. `Iterations:` is accepted as an alias.
- `--judge-personas` — custom judge persona overrides.
- `--no-synthesis` — skip synthesis; pure debate only.
- `--temperature` — generation temperature hint.
- `--evals`, `--evals-interval N`, `--chain`, `--<subcommand>`.

Remaining text not matching flags is the task description.

## Setup (if Task or Domain is missing)

Ask the user once, batching:

1. Task: what should be reasoned about? (open text)
2. Domain: software architecture, product strategy, business decision, security, research, content.
3. Mode: convergent (stop when the winner repeats), creative (never auto-stop), debate (no synthesis).
4. Judges: 3 (default), 5 (thorough), 7 (deep).

If all are provided, skip setup.

## Setup phase

1. Read the judge protocol reference.
2. Parse the domain; select the domain-specific judge criteria.
3. Create `autoresearch/reason-<YYMMDD>-<HHMM>/`; write the active marker (contracts).
4. TSV: `# metric_direction: higher_is_better`, then the common columns plus `timestamp`, `candidate_label`, `judge_verdict`. `metric` = `convergence_count`; `status` = `incumbent-kept`, `incumbent-replaced`, or `converged`; `commit` is `-`.
5. Initialize `incumbent = null`, `convergence_count = 0`.

## Round loop

1. **Generate-A.** Round 1: Author-A generates the first candidate from the task description. Round N>1: the incumbent is Author-A's candidate. Cold start: Author-A sees ONLY the task description and domain context.
2. **Critic.** The critic receives candidate-A (cold start, no shared session). MUST find at least 3 specific weaknesses and MUST suggest what a superior candidate would do differently. Purely adversarial; never compliments.
3. **Generate-B.** Author-B receives the task, candidate-A, and the critique (cold start) and produces candidate-B, addressing the critique while preserving A's strengths.
4. **Synthesize** (unless `--no-synthesis` or debate mode). The synthesizer receives task, A, and B (cold start) and produces hybrid candidate-AB.
5. **Blind judge panel.** Each judge receives 3 candidates with RANDOMIZED labels (Label-X, Label-Y, Label-Z), evaluates independently on the domain criteria, and produces a ranking plus a one-paragraph justification. Verdict: majority vote; a tie goes to the synthesized candidate. Isolation (cold start, no shared state) applies to every role; where the host supports isolated sub-agents use them, otherwise run each role from a fresh prompt that contains only its permitted inputs.
6. **Convergence check.** Winner equals incumbent: `convergence_count++`. Otherwise `convergence_count = 1` and the winner becomes the incumbent. Convergent mode: `convergence_count >= N` means CONVERGED, stop. Creative mode: never auto-stop. Debate mode: as convergent, without synthesis.
7. **Oscillation guard.** If the incumbent changed 5 or more times in the last 8 rounds, recommend stopping early (not converging).
8. **Log.** Append the TSV row: round, timestamp, winning candidate label, judge verdict, convergence count, description.
9. **Eval checkpoint.** `iteration` means round here. Header `--- Eval Checkpoint (rounds {X}-{Y}) ---`; stats line `Incumbent: {label} | Convergence: {count}/{target} | Oscillations: {n}`; recommend early stop after 3 or more checkpoints with oscillation.
10. **Bounded check.** At the round bound, exit the loop.

## Output

- `reason-results.tsv` — per-round results.
- `lineage.md` — full history of candidates, critiques, and judge reasoning.
- `summary.md` — final winner, convergence trajectory, key insights.

## Summary

Print: total rounds, convergence status, final winner summary, judge agreement rate.

## Finish

Write `handoff.json`: `source: "reason"`, `status` ∈ `COMPLETE`, `CONVERGED`, `USER_INTERRUPT`, `BOUNDED`, `ERROR`; `findings` = `[{id, type: "recommendation", summary: <winner description>}]`; `config` = task, domain, mode. Delete the active marker, then follow `--chain` (contracts).
