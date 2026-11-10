# Fork-and-flush

How a metric loop leaves an idea basin. Sources: Cai et al., "Fork-and-Flush: Escaping Idea Basins in Autoresearch Agents" ([arXiv:2610.07447](https://arxiv.org/abs/2610.07447)), for random branches; Zhang et al., "Stateless Language Agents: Scaling Long-Horizon Automated Research" ([arXiv:2610.07625](https://arxiv.org/abs/2610.07625)), for guided branches.

## Why

One loop keeps improving inside one family of ideas and plateaus there, because each idea is reasoned from the previous ones in the same context. Compaction does not fix this. Two moves do, best together:

- **Flush**: a fresh agent that starts from the files only, with no conversation, re-derives the intent and can land in another basin.
- **Fork**: run several such agents from the same state and keep the best.

Upstream-reported normalized scores at matched budget (13 tasks; ablations on 11): single run 0.47, best-of-4 0.54, flush only 0.55, fork only 0.57, fork-and-flush 0.78.

## Branch kinds

A round has K branches (`Forks: K`, default 4). `floor(K × R)` are **guided** (`Guided: R`, default 0.5): each gets one concrete experiment from the Advisor, so branches cover distinct ideas and none repeats a logged failure. The rest are **random**: told only the task, they are the only source of ideas the Advisor would not propose. Keep at least one random branch.

## Schedule

Rounds run on a fixed schedule; plateau triggers were dropped upstream because small gains keep resetting the stall clock.

| Mode | Rounds |
|---|---|
| Bounded, N ≥ 12 | after 33% and 66% of N |
| Bounded, N < 12 | one, at 50% of N |
| Unbounded | every 20 iterations |

Early trigger: 5 iterations since the last `keep` or round with no `keep`. An early round replaces the next scheduled one.

## One round

1. **Protect the incumbent** (best commit so far): `git tag -f autoresearch/incumbent <sha>`. No branch reverts or overwrites it.
2. **Fork.** Each branch is a fresh-context `task` subagent in its own `git worktree add` at the incumbent. Use K = 2, run one after another, when one Verify run takes over about 5 minutes or needs a single shared resource (one local stack, one test database). Branch budget: `max(2, round(0.06 × N))` iterations; 2 when unbounded.
3. **Advisor** (skip when no guided branches): one fresh-context subagent that reads Goal, Scope, Metric, Direction, the results TSV, `git log`, and the incumbent's diff against the baseline, never the leader's conversation. It edits nothing and returns one experiment per guided branch: one change, concrete enough for one iteration, all distinct, none repeating a `discard`, `crash`, or `metric-error` row. Prefer untried directions over more tuning of what worked.
4. **Flush.** Give each branch Goal, Scope, Metric, Direction, Verify, Guard, its budget, the results TSV path, and the incumbent-tag rule; a guided branch also gets its experiment and tests it first. Never pass the leader's hypotheses, plans, idea ranking, or a conversation summary. Do not tell random branches to "try something completely different": it had no measurable effect.
5. **Run.** Each branch runs the core loop on its worktree and returns its best metric and kept commits.
6. **Select.** Best metric wins; a tie with the incumbent goes to the branch (fresh context). Cherry-pick or fast-forward the winner's kept commits onto the loop branch, then remove every worktree. If no branch beat the incumbent the loop branch stays put.
7. **Hand over.** The winner continues as leader (message it if the platform can resume it). Otherwise the main agent continues after re-reading the TSV and `git log`, treating its earlier hypotheses as stale.
8. **Log.** One row per branch with status `fork-{k}` and its best metric, description starting `random:` or `guided: <experiment>`; one `fork-select` row naming the winner, its kind, and whether it beat the incumbent.

The loop's result is the best metric any branch or the leader reached. Compare wins by kind across `fork-select` rows; if one kind never wins, move R toward the other.

## Orchestrator

Branch Metric is Units remaining (lower), Verify is the pinned predicate. When `plateau` exits 0 and the ceiling is not reached, `verdict` answers `FORK` while `fork_rounds_since_progress` < 2: run one round, add 1, continue. Reset it to 0 whenever units improve. At 2, `verdict` answers `PLATEAU`. Under `--no-fork`, treat `FORK` as `PLATEAU`.

## Cost and opt-out

A round costs about K × 6% of the budget; the Advisor is one short call. With expensive Verify prefer K = 2 over skipping rounds: flushing alone recovers about half the gain. Use `--no-fork` for mechanical sweeps with no ideas to get stuck on (parameter grids, a fixed list of known fixes).
