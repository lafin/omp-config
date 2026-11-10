# improve: ICP research, improvement discovery, PRDs

Research the ideal customer's challenges, discover improvements, rank them, and generate PRDs for the selected ones. Default 15 iterations. Terminal emitter: no downstream chain. Shared blocks: `skill://autoresearch/references/contracts.md`. If the goal is a source-pinned implementation against an external API rather than product research, use bare `skill://source-driven-development`.

## Arguments

- `Goal:` — product area to improve (or all remaining invocation text if there is no keyword).
- `--icp` or `ICP:` — ideal customer profile description.
- `--discover` — force an inline codebase scan even when context exists.
- `--no-discover` — skip auto-discover; warn instead.
- `--seeds <categories>` — override the default research category seeds.
- `--depth` — shallow (5 iterations), standard (15), deep (30).
- `--features` — comma-separated feature names to pre-select for PRD generation.
- `Iterations:` or `--iterations` — default 15, or `unlimited`.
- `--evals`, `--evals-interval N`.

If an upstream `handoff.json` exists in the working directory, read it and map the source findings to default seed categories (override with `--seeds`):

- `probe` → ICP challenges, UX & experience
- `predict` → Competitor gaps, Revenue & growth
- `debug` or `security` → Competitor gaps, ICP challenges

## Setup (if Goal or ICP is missing)

Ask the user once, batching:

1. Goal: what product area to improve? (open text)
2. ICP: who is your ideal customer? (target buyer or user)
3. Pain points: the top 3 pain points your customers face.
4. Competitors: key competitors, or skip.
5. Depth: shallow (5 iterations, quick scan), standard (15, recommended), deep (30+, exhaustive).

If all are provided inline, skip setup.

## Phase 1: Product context

Resolve product context in priority order:

1. Learn summary (`autoresearch/learn-*/summary.md`, most recent): read it.
2. `README.md` (at least 500 characters, non-boilerplate): extract the product description.
3. `package.json`, `pyproject.toml`, or `Cargo.toml` description (at least 10 characters): use it.
4. If ALL the above are absent AND NOT `--no-discover`: auto-discover by scanning 10 key files (manifest, routes, models, config), capped at 1500 tokens.
5. With `--discover`: force the scan regardless of the above.
6. If nothing is found, warn: "No product context. Run `/autoresearch learn Mode: summarize` for better results."

## Phase 2: Research loop

Create `autoresearch/improve-<YYMMDD>-<HHMM>/`; write the active marker (contracts). TSV: `# metric_direction: higher_is_better`, then the common columns plus `timestamp`, `category`, `research_question`, `source`, `insight_problem`, `insight_mechanism`, `confidence`, `classification`. `metric` = cumulative insights; `status` = `new` or `extension`; `commit` is `-`.

Five research categories:

1. ICP challenges — pain points, jobs-to-be-done, unmet needs.
2. Competitor gaps — weaknesses, missing features, technical differentiators.
3. Market trends — timing signals, emerging patterns, regulatory shifts.
4. UX & experience — interaction models, onboarding, retention mechanics.
5. Revenue & growth — pricing, acquisition, monetization, upsell and expansion.

Iteration protocol:

- Reserve the first 5 iterations: one per category (forced breadth).
- Remaining iterations target the categories with the richest signal.
- Per iteration: form a research question, run a web search, synthesize, normalize to the canonical insight schema, classify (new, extension, duplicate), tag confidence (HIGH: 3 or more sources, MEDIUM: 2, LOW: 1), cross-check against the codebase, log.
- **Saturation:** net-new insights below 2 for 3 consecutive non-reserved iterations means SATURATED: exit the loop.
- The iteration bound is the infinite-loop guard.

Insight schema: `{problem: 10-word canonical form, affected_persona: ICP segment, proposed_mechanism: how to address, expected_outcome: what success looks like}`. Classification: **new** = novel `{problem, persona}` pair; **extension** = same pair, different mechanism; **duplicate** = same pair and mechanism: skip.

Eval checkpoint stats line: `Insights: {total} (+{new}) | Categories: {covered}/5 | Saturation: {window}/3`.

## Phase 3: Feature ranking and selection

1. ICP binary gate: filter out insights that do not serve the stated ICP.
2. Three-tier bucketing: Must-have, Nice-to-have, Moonshot.
3. Pairwise ranking within the Must-have tier only (cap 7-10 items).
4. A two-sentence rationale per item, citing research evidence.
5. A confidence indicator per item (HIGH, MEDIUM, LOW).

Write `improvement-plan.md` with the full tiered ranking. Present the tiered list to the user and ask which features become PRDs (multi-select). With `--features`, pre-select matching items and still show them for confirmation. A run that cannot ask writes PRDs only for `--features` items and records the rest in `improvement-plan.md`.

## Phase 4: PRD generation

For each selected feature write `prd-<feature-slug>.md`:

- Top disclaimer: "Auto-generated from research findings. DECISION NEEDED items and LOW-confidence sections require your judgment."
- Problem statement (from the research evidence chain).
- User stories (from ICP and persona data).
- Requirements (functional and non-functional, MoSCoW from the tier).
- Acceptance criteria.
- Technical approach (from codebase context, framed as "suggested starting points").
- Risks and confidence (evidence tiers: primary = codebase, secondary = web research).
- Success metrics.
- `DECISION NEEDED` markers for unresolvable tradeoffs.
- `Open Questions` section.

Write `research-findings.md` (all insights with citations and confidence) and `summary.md` (overview, research stats, category coverage, saturation status).

## Summary

Print: total iterations, insights discovered (new, extension), categories covered, saturation status, PRDs generated, output directory path.

With `--evals`, also write `evals-summary.md` to the run directory.

## Finish

Write `handoff.json`: `source: "improve"`, `status` ∈ `COMPLETE`, `SATURATED`, `USER_INTERRUPT`, `BOUNDED`, `ERROR`; `findings` = improvements with tier, confidence, `prd_path`; `config` = goal, icp, depth, categories_explored, insights_total, prds_generated. Delete the active marker. No chain.
