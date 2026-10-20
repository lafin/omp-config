# Content Refresh Wave 2: Context Core Defects

- **Status:** Completed
- **Date:** 2026-10-06
- **Source:** [Skill Content Refresh Plan §7.2 Context core](../skill-content-refresh-plan.md#72-context-core)

## Decision

Applied as Class D (gate: deterministic checks plus the item's smoke check; no live evaluation). Wave 2 grouped commits by skill family, one commit per family, to keep review small and revert easy. Paths and line numbers below are the review baseline `7529a16`; skill directories now live under `skills/`.

- **CF-1** · `context-fundamentals/references/context-components.md:229-235`, `context-fundamentals/scripts/context_manager.py:79`, `context-optimization/scripts/compaction.py:85`, and the other scripts that use `len(text) // 4` — The 4 chars/token estimate undercounts by about 35–40% on the Claude tokenizer introduced with Opus 4.7 (1M tokens ≈ 2.5M characters). **Change:** state that the ratio depends on the tokenizer. Accept a token-counting function as a parameter, and keep `len // 4` only as a labeled fallback. Source: <https://platform.claude.com/docs/en/models/overview>.
- **CF-3** · `context-fundamentals/references/context-components.md:178-189` — `inject_summaries` appends a summary every 20 messages but keeps the summarized messages, so context grows. It also inserts mid-conversation `system` messages, which not every model accepts. **Change:** replace the summarized span with the summary, use a user-role message, or delete the example and link `context-compression`.
- **CF-4** · `context-fundamentals/scripts/context_manager.py:345`, `references/context-components.md:243-244` — The fixed 80,000-token "recommended limit" and fixed budget ranges contradict `SKILL.md:81`. **Change:** make the limit a required parameter, or label it as a demo value.
- **CF-5** · `context-fundamentals/SKILL.md:216-218` — External resources have no URLs. **Change:** link Liu et al. 2023 (<https://arxiv.org/abs/2307.03172>), Chroma Context Rot (<https://www.trychroma.com/research/context-rot>), NoLiMa (<https://arxiv.org/abs/2502.05167>), and Anthropic's context-window docs (<https://platform.claude.com/docs/en/build-with-claude/context-windows>).
- **CD-1** · `context-degradation/references/patterns.md:12-38,45-78,262-268` — The code hard-codes the first and last 10% of positions as "attention favored", needs attention weights that closed APIs do not expose, and fixes alerts at 70% and 90%. This contradicts `SKILL.md:35,87`. **Change:** replace it with a behavioral probe (recall by position and length). Make the thresholds parameters taken from a measured baseline.
- **CD-2** · `context-degradation/SKILL.md:93-97,236-238` — The three "counterintuitive findings" are Chroma's Context Rot results (July 2025, 18 models) and are uncited. **Change:** cite Chroma and NoLiMa.
- **CD-6** · `context-degradation/SKILL.md:61` — "the original errors retain attention weight" states a mechanism without a source. **Change:** "corrections layered on top are often ignored; measure on the target workload".
- **CD-7** · `context-degradation/SKILL.md:109-119` — **[INFERENCE]** The Write/Select/Compress/Isolate taxonomy appears to come from LangChain's 2025 context-engineering post. **Change:** verify the source, then attribute it or reword.
- **CC-1** · `context-compression/SKILL.md:15,35-47,103-125,176-220` — The skill restates Factory's "Evaluating Context Compression for AI Agents" (2025-12-16) without citing it. **Change:** restore the citation. Source: <https://factory.com/news/evaluating-compression>.
- **CC-2** · `context-compression/SKILL.md:37` — "This prevents drift" overstates the source, which says "less likely to drift". The anchored method scored 2.45/5 on artifact trail, and its overall lead was 0.26–0.35 on a 0–5 scale. **Change:** "reduces drift", with the effect size.
- **CC-5** · `context-compression/SKILL.md:280` — The talk is "The Infinite Software Crisis" by Jake Nations, AI Engineer Code 2025, not "Netflix Engineering, AI Summit 2025". **Change:** correct and link <https://ai.engineer/talks/eIoohUmYpGI-infinite-software-crisis>.
- **CC-6** · `context-compression/scripts/compression_evaluator.py:345,473-474` — The judge model is hard-coded to `gpt-5.2`. **Change:** make the judge model a required argument (model-neutral rule). Check: `python3 -m unittest discover -s context-compression/tests`.
- **CC-7** · `context-compression/SKILL.md:39` — Optional. Cite JetBrains (<https://arxiv.org/abs/2605.11051>): an embedding-based compressor succeeds on single-shot tasks and fails on multi-step agentic coding.
- **CO-5** · `context-optimization/SKILL.md:132,160`, `scripts/compaction.py:421` — Two different fixed trigger thresholds (0.8 and 70%) contradict `SKILL.md:84`. **Change:** use one named `measured_safe_limit` parameter.
- **CO-6** · `context-optimization/references/optimization_techniques.md:162-164` — "Place critical information at attention-favored positions (beginning and end)" contradicts the measure-first rule. **Change:** "test placement; use the measured best position".

## Evidence

- `CF-1`: `skills/context-fundamentals/scripts/context_manager.py:71-84` (`count_tokens` parameter, labeled `len(text) // 4` fallback); `skills/context-optimization/scripts/compaction.py:64-76`; `skills/filesystem-context/scripts/filesystem_context.py:80-85`; `skills/context-fundamentals/references/context-components.md:226` (ratio depends on tokenizer)
- `CF-3`: `skills/context-fundamentals/references/context-components.md:175,184` (replace span with summary; user-role message)
- `CF-4`: `skills/context-fundamentals/scripts/context_manager.py:153-166` (`context_limit` required)
- `CF-5`: `skills/context-fundamentals/SKILL.md:217-220`
- `CD-1`: `skills/context-degradation/references/patterns.md:7-48` (behavioral recall probe; `max_drop` from baseline variance)
- `CD-2`: `skills/context-degradation/SKILL.md:91,237`
- `CD-6`: `skills/context-degradation/SKILL.md:61`
- `CD-7`: `skills/context-degradation/SKILL.md:111` (attributed to LangChain)
- `CC-1`: `skills/context-compression/SKILL.md:35,285`
- `CC-2`: `skills/context-compression/SKILL.md:37` ("reduces drift", 0.26–0.35 lead)
- `CC-5`: `skills/context-compression/SKILL.md:284`
- `CC-6`: `skills/context-compression/scripts/compression_evaluator.py:345,474,746,760` (`judge_model` required)
- `CC-7`: `skills/context-compression/SKILL.md:39` (JetBrains 2605.11051)
- `CO-5`: `skills/context-optimization/SKILL.md:51,101,136,164`; `skills/context-optimization/references/optimization_techniques.md:199` (`measured_safe_limit`)
- `CO-6`: `skills/context-optimization/references/optimization_techniques.md:164`
