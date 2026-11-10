# Content Refresh Wave 2: Evaluation, Writing, and Review Defects

- **Status:** Completed
- **Date:** 2026-10-06
- **Source:** [Skill Content Refresh Plan §7.5 Evaluation, writing, and review](../skill-content-refresh-plan.md#75-evaluation-writing-and-review)

## Decision

Applied as Class D (gate: deterministic checks plus the item's smoke check; no live evaluation). Wave 2 grouped commits by skill family, one commit per family, to keep review small and revert easy. Paths and line numbers below are the review baseline `7529a16`; skill directories now live under `skills/`. `RP-6` (offer `EV-1`, `AE-3`, `LDC-1` and other shared fixes upstream) stays open in the plan as an owner decision.

- **EV-1** · `evaluation/scripts/evaluator.py:202-245,257-259,437`, `SKILL.md:285-289` — Each dimension without evidence falls back to a default (0.7/0.8/0.8/0.5/0.8). The defaults sum to 0.74, above the 0.7 pass threshold. Empty output and the wrong answer `"London"` both pass. `expected["answer"]` is never read. **Change:** score missing evidence as 0 or `unknown`, read `expected["answer"]`, and make the demo show at least one failure. Check: `python3 evaluation/scripts/evaluator.py` reports at least one failure.
- **EV-2** · `evaluation/SKILL.md:164-170` — `config["weights"]` reads the loop variable after the loop ends. **Change:** `{d: c["weight"] for d, c in rubric.items()}`.
- **EV-5** · `evaluation/SKILL.md:276-279,287-295` — The external resources have no links, and the version footer does not change behavior. **Change:** link <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents> and delete the footer.
- **AE-1** · `advanced-evaluation/references/bias-mitigation.md:9-12` — "~55% first-position preference" does not match MT-Bench Table 2, which shows Claude-v1 at 75.0% first, GPT-3.5 at 50.0%, and GPT-4 at 30.0%, all 2023 models. **Change:** delete the per-vendor numbers. Say that bias varies by judge and prompt, and that swaps on the target judge measure it. Source: <https://arxiv.org/abs/2306.05685>.
- **AE-2** · `advanced-evaluation/references/bias-mitigation.md:139-144`, `references/implementation-patterns.md:116,130` — `claude-4-5-sonnet` was never a valid ID. `gpt-5.2` is labeled both "cheaper" and "more capable". **Change:** use `JUDGE_MODEL` and `SCREEN_MODEL` placeholders.
- **AE-3** · `advanced-evaluation/references/metrics-guide.md:233-236` — `await` inside a plain `def` is a SyntaxError. **Change:** `async def`.
- **AE-7** · `advanced-evaluation/references/bias-mitigation.md:97-112`, `SKILL.md:133-135`, `references/implementation-patterns.md:178-193` — The 500-word length target and the confidence formulas have no source. **Change:** label them as illustrative. State that confidence needs calibration against human labels.
- **AE-8** · `advanced-evaluation/SKILL.md:414-417` — The section repeats the Integration section at lines 380–388. **Change:** delete it.
- **SEE-4** · `simplified-engineering-english/references/rules.md` source columns (lines 21, 32, 35, 44–46, 58, 62) — STE-derived rules cite topics, not rule numbers. Issue 9 renamed "noun clusters" to "multi-word nouns". **Change:** cite exact rule numbers (2.1/2.2, 3.2/3.4/3.6, 4.2, 5.1/5.4/5.5, 6.3, 7.1–7.3, 8.1, 8.4–8.7), and rename the SEE-NOUN-01 source. Source: <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>.
- **LDC-1** · `lossless-doc-compress/references/slop-and-hedging.md:18`, `references/removal-taxonomy.md:13-14` — "essentially identical" → "identical" changes approximate equality into exact equality, which `fidelity-rules.md:44-48` forbids. "quite" often changes degree. **Change:** move the example to the KEEP or FLAG list, and remove "quite" from the removable hedges. Set `metadata.adaptation: modified` and update `ATTRIBUTION.md`, because the skill is currently recorded as imported.
- **LDC-2** · `lossless-doc-compress/references/compression-workflow.md:41-42`, `references/output-templates.md:21-35` — The self-check needs words removed per category, and the log template does not record them. **Change:** add a words-removed column to the log template.

## Evidence

- `EV-1`: `skills/evaluation/scripts/evaluator.py:171-185` (unknown dimensions excluded; pass needs scored evidence), `:203-213` (returns `None`), `:263-265` (reads `answer`); `python3 skills/evaluation/scripts/evaluator.py` reports `Passed: 0 / Failed: 3` (run 2026-10-10)
- `EV-2`: `skills/evaluation/SKILL.md:180`
- `EV-5`: `skills/evaluation/SKILL.md:296`; no version footer
- `AE-1`: `skills/advanced-evaluation/references/bias-mitigation.md:9`
- `AE-2`: `skills/advanced-evaluation/references/implementation-patterns.md:116,130`; `references/bias-mitigation.md:143`
- `AE-3`: `skills/advanced-evaluation/references/metrics-guide.md:233`
- `AE-7`: `skills/advanced-evaluation/references/bias-mitigation.md:98`; `references/implementation-patterns.md:176-180`; `SKILL.md:160`
- `AE-8`: `skills/advanced-evaluation/SKILL.md:381` (single `## Integration` section)
- `SEE-4`: `skills/simplified-engineering-english/references/rules.md:45` (multi-word nouns), `:140,157` (STE rule-number mapping)
- `LDC-1`: `skills/lossless-doc-compress/references/removal-taxonomy.md:16`; `references/slop-and-hedging.md:59-62`; `SKILL.md:9` (`adaptation: modified`); `ATTRIBUTION.md:39`
- `LDC-2`: `skills/lossless-doc-compress/references/output-templates.md:22,38`
