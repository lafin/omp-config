# Skill Content Refresh Plan

## 1. Purpose

This plan corrects defects and stale content found in the 2026-10-06 review of all 25 root skills and their four upstream sources. It complements [the skill set improvement plan](skill-set-improvement-plan.md). That plan owns evaluation machinery, routing coverage, anatomy, and new-skill admission. This plan owns the content of existing skills: facts, citations, code examples, scripts, and guidance that recent research or vendor changes made wrong or incomplete.

The work is done when every item in Sections 6–9 is applied, rejected with a recorded reason, or deferred to a named owner decision, and every applied item has passed its verification class in Section 4.

## 2. Baseline

| Field | Value |
|---|---|
| Repository revision | `7529a16` plus the `PD-0` edit (Section 5) |
| Review date | 2026-10-06 |
| Skills reviewed | 25 root skills, `.omp/hooks/pre/leancode.ts`, three staged proposals |
| `python3 scripts/validate_skills.py` | passed |
| Agent Skills spec conformance | All `SKILL.md` files are under 500 lines, all descriptions are 1024 characters or fewer, and all references are one level deep. `tool-design` body is about 5.2k tokens (chars/4 estimate), above the spec's ~5k recommendation. Source: <https://agentskills.io/specification> |

Line numbers below refer to the baseline revision. Re-read each location before editing. Items marked **[INFERENCE]** were not verified against a primary source and need verification before change.

## 3. Upstream Drift

Closed: see [Content Refresh Wave 1: Upstream Sync and Repository Hygiene](decisions/0005-content-refresh-wave-1-hygiene.md).

## 4. Change Classes and Gates

Each item has one class. The class sets the gate.

| Class | Scope | Gate |
|---|---|---|
| **D** — defect | Wrong facts, citations, numbers, model IDs, code examples, scripts, and metadata. Includes corrections inside a `SKILL.md` body when the instruction's intent does not change. | Section 10.1 deterministic checks plus the item's smoke check. No live evaluation. |
| **G** — guidance | Adds, removes, or changes what a skill tells the agent to do. | One development behavior case that observes the new behavior, run baseline versus treatment under the skill set plan §18.2. Holdout follows the same section. Evaluation-case additions land in a separate commit before the skill change (skill set plan §16). |
| **R** — routing | Description text or "Do not activate" lists. | Canonical routing development and holdout pairs under the skill set plan §11, one skill or confusable family per treatment. |

Leancode-family **G** items also follow the candidate gate in [the Leancode improvement plan](leancode-improvement-plan.md). `simplified-engineering-english` **G** items also follow its release governance in the skill set plan §9.1.

Model-neutral rule (from `RP-1`): prose and reference examples use placeholders such as `JUDGE_MODEL`, not vendor model IDs. Executable script defaults may name a current model ID only when the script is a mock or template and the value matches upstream.

## 5. Already Applied

Closed: see [Content Refresh Wave 1: Upstream Sync and Repository Hygiene](decisions/0005-content-refresh-wave-1-hygiene.md).

## 6. Wave 1 — Repository Hygiene

`RP-1` to `RP-5` closed: see [Content Refresh Wave 1: Upstream Sync and Repository Hygiene](decisions/0005-content-refresh-wave-1-hygiene.md).

- **RP-6** · owner decision · upstream contributions
  - Offer `LDC-1` to `ML-SystemDesign/MLSystemDesign`. Offer the shared defects in `EV-1`, `AE-1`, `AE-3`, `MS-1`, `MS-2`, and `MAP-2` to `muratcankoylan/Agent-Skills-for-Context-Engineering`, where the same files exist.

## 7. Wave 2 — Defect Fixes (Class D)

Group commits by skill family. One commit per family keeps review small and revert easy.

### 7.1 Leancode family and hook

Closed (`LC-1`, `LD-1`): see [Content Refresh Wave 2: Leancode Family Defects](decisions/0006-content-refresh-leancode-family.md).

- **HK-2** · `hooks/pre/leancode.ts:15-20,36-57` (was `.omp/hooks/pre/leancode.ts`) — **[INFERENCE]** The reminder filter and legacy-migration code may be dead. Reason: the hook uses the `context` event, which changes the LLM context for one call and does not write reminders to session history. The first hook version (`8d25b71`) also used `context`. **Change:** add one `evals/mode_smoke.py` assertion that `event.messages` never contains a prior hook reminder. If it holds across all four modes, delete `LEGACY_REMINDERS`, `isLeancodeStateMessage`, the filter, and their tests (`tests/leancode_hook.test.ts:5-8,122-189`). If it fails, generate `LEGACY_REMINDERS` from `leancodeReminder()` so the reminder text exists in one place. Check: `bun test tests/leancode_hook.test.ts` and `mode_smoke.py`.

### 7.2 Context core

Closed: see [Content Refresh Wave 2: Context Core Defects](decisions/0007-content-refresh-context-core.md).

### 7.3 Systems

Closed: see [Content Refresh Wave 2: Systems Defects](decisions/0008-content-refresh-systems.md).

### 7.4 Workflows

Closed: see [Content Refresh Wave 2: Workflow Defects](decisions/0009-content-refresh-workflows.md).

### 7.5 Evaluation, writing, and review

Closed: see [Content Refresh Wave 2: Evaluation, Writing, and Review Defects](decisions/0010-content-refresh-evaluation-writing-review.md).

## 8. Wave 3 — Guidance Changes (Class G)

Order by risk: security and false-pass defects first, then factual guidance, then style. Each bullet is one treatment unless it says it is grouped.

### 8.1 Security and correctness

- **HA-4** · `hosted-agents/SKILL.md:61-65,168-173`, `references/infrastructure-patterns.md:43,97,658-662`, `scripts/sandbox_manager.py:191` — The skill puts an `x-access-token` clone URL and `GITHUB_APP_TOKEN`/`NPM_TOKEN` inside the sandbox. The token persists in `.git/config` and from there in images and snapshots, and it expires after one hour. **Change:** never place credentials in sandbox images or snapshots. Inject credentials through a proxy outside the sandbox, scoped to the session branch. Sources: <https://www.anthropic.com/engineering/claude-code-sandboxing>, <https://modal.com/docs/sdk/py/latest/Sandbox>, <https://developers.cloudflare.com/sandbox/>, <https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app>. Behavior case: a sandbox setup request that tempts token injection.
- **HA-6** · `hosted-agents/SKILL.md:55-59,271`, `references/infrastructure-patterns.md:644-669` — **Change:** add a gotcha about snapshot expiry (Modal: filesystem snapshots 30 days, memory snapshots 7 days, `NotFoundError` on expiry; sandboxes default to 5 minutes with a 24-hour cap). Replace the `blocked_commands` denylist with platform egress allowlists. Sources: <https://modal.com/docs/guide/sandbox-snapshots>, <https://modal.com/docs/guide/sandbox-networking>, <https://developers.openai.com/codex/cloud/internet-access>. Group with `HA-4`.
- **FC-2** · `filesystem-context/SKILL.md:149-161,264-273` — **Change:** add a gotcha: confine agent writes to a rooted directory, reject path traversal, and treat persisted instructions as untrusted input. Source: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool>.
- **CC-4 + CD-5** · `context-compression/SKILL.md:233-247`, `context-degradation/SKILL.md:57` — OpenAI reported a model that wrote jailbreak-style instructions into its own compaction summaries, and a successor that obeyed them. **Change:** treat summary text as data. A summary must not add constraints that do not appear in user or task messages. Flag imperatives that cannot be traced to the user or the task. Source: <https://alignment.openai.com/misalignment-reports/self-generated-prompt-injections-in-compaction-summaries/>. One grouped treatment across both skills.
- **TD-1** · `tool-design/SKILL.md:110-125,264` — "Always use fully qualified `ServerName:tool_name`" conflicts with MCP: since 2025-11-25, tool names SHOULD use only `A-Za-z0-9_-.`, and disambiguation is the client's job. **Change:** server authors choose names that are unique within the server and use the allowed charset (dots allowed for namespaces). Prompts refer to tools by the qualified form the host exposes. Sources: <https://modelcontextprotocol.io/specification/2026-07-28/server/tools>, <https://modelcontextprotocol.io/specification/2025-11-25/changelog>.
- **TD-2** · `tool-design/SKILL.md:94-104,180-191`, `references/best_practices.md:41-70` — **Change:** add checklist items: `outputSchema` with `structuredContent` for structured results; honest `annotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), which clients treat as untrusted; input-validation failures returned as `isError: true` tool results, not protocol errors; stateful tools that take explicit server-minted handles (the 2026-07-28 revision is stateless); deterministic `tools/list` order. Pin the spec revision. Source: <https://modelcontextprotocol.io/specification/2026-07-28/changelog>. Group with `TD-1`.
- **TD-6** · `tool-design/SKILL.md:133-161,245-256` — The body is over ~5k tokens. The `optimize_tool_description` template calls an undefined `get_agent_response`, and the Guidelines repeat Core Concepts. **Change:** delete both blocks to make room for `TD-2`. Group with `TD-1`.
- **EV-3** · `evaluation/SKILL.md:47-55,101-116,238-251` — **Change:** add "Trials and reliability": k trials per task in isolated environments, reporting pass@1 and pass^k (0.75 per trial → about 42% at k=3). Add capability and regression suites, a reference solution per task, transcript review, and "0% pass@100 means the task or grader is broken". Replace Gotcha 6. Source: <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>.
- **EV-4** · `evaluation/SKILL.md:37,51` — **Change:** grade outcomes by default, and add tool-call or process assertions only for steps that safety or policy requires. Same source. Group with `EV-3`.
- **AE-4** · `advanced-evaluation/SKILL.md:42-44,190-203,348` — Pairwise protocols are more exploitable by distractor features (about 35% preference flips versus 9% for absolute scores). **Change:** when a system is optimized against the judge, prefer absolute or rubric scoring, or add distractor-controlled pairs. Keep pairwise for one-off comparisons. Source: <https://arxiv.org/abs/2504.14716>.
- **AE-5** · `advanced-evaluation/SKILL.md:56`, `references/bias-mitigation.md:126-164` — **Change:** the judge must not share a model, lineage, or family with the generator, or with synthetic data used to train it (preference leakage). Source: <https://arxiv.org/abs/2502.01534>. Group with `AE-4`.
- **AE-6** · `advanced-evaluation/SKILL.md:83-108` — **Change:** use one criterion per judge call when criteria interact, and add an `UNKNOWN` score. Source: the Anthropic evals guide above. Group with `AE-4`.
- **SIL-5** · `self-improvement-loops/SKILL.md:74-76,128-139` — The gate compares only against the previous harness. Under matched budgets, harness evolution fails to beat test-time-scaling baselines. **Change:** add a matched-budget best-of-N or retry baseline, and an untouched final test split separate from the reused gate split. Source: <https://arxiv.org/abs/2607.12227>.

### 8.2 Factual guidance

- **MAP-3** · `multi-agent-patterns/SKILL.md:153-163,222,232` — Majority voting accounts for most of debate's gains. More discussion rounds hurt. **Change:** make independent sampling plus a weighted vote the baseline. Use debate only when it shows a measured gain over the vote. Sources: <https://arxiv.org/abs/2508.17536>, <https://arxiv.org/abs/2502.19130>.
- **MAP-4** · `multi-agent-patterns/SKILL.md:17-25,37-43,68,108-123,195-202` — **Change:** add a "stay single-agent" gate. Split work by context boundary, not by role. Add a single-writer rule and the generator-verifier pattern. Demote swarm. Replace "parallel time approaches the longest subtask" with "parallelism buys thoroughness, not speed". Fix Example 1. Sources: <https://arxiv.org/abs/2512.08296>, <https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them>, <https://claude.com/blog/multi-agent-coordination-patterns>. Group with `MAP-3`.
- **CO-1** · `context-optimization/SKILL.md:37,71-84,187` — **Change:** add a short list of provider cache rules, with links and no price table: tool changes invalidate everything downstream; restrict tools with `allowed_tools` or `tool_choice` instead of removing them; the TTL sets the idle budget between agent turns; minimum cacheable sizes exist. Sources: <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>, <https://developers.openai.com/api/docs/guides/prompt-caching>, <https://ai.google.dev/gemini-api/docs/caching>.
- **CO-2** · `context-optimization/SKILL.md:76-77` — Both Anthropic and OpenAI render tools before the system prompt. **Change:** list tools first. Group with `CO-1`.
- **CO-3** · `context-optimization/SKILL.md:61-69` — **Change:** name native tool-result clearing (`clear_tool_uses_20250919`), and state the rule "clear in large batches, because each clear invalidates the cache". Source: <https://platform.claude.com/docs/en/build-with-claude/context-editing>. Group with `CO-1`.
- **CO-4** · `context-optimization/SKILL.md:94-101` — Some current models get no injected token-budget updates. **Change:** the harness supplies a deterministic token readout (usage fields or token counting) on those models. Source: <https://platform.claude.com/docs/en/build-with-claude/context-windows>. Group with `CO-1`.
- **CO-8** · `context-optimization/SKILL.md` KV-cache section — Adopt the upstream sentence: an edit to earlier history costs the text that follows it, so batch such edits and place them near the end. Group with `CO-1`.
- **CO-7** · `context-optimization/SKILL.md:49-59,181,189` — The compaction content repeats `context-compression`. **Change:** keep only the trigger and budget policy, and link `context-compression` for summary content.
- **CC-3** · `context-compression/SKILL.md:35-41,153-168` — **Change:** add "native options first", which maps each strategy to provider compaction features. Mark opaque provider compaction as uninspectable, so probe evaluation is the only check. Sources: <https://platform.claude.com/docs/en/build-with-claude/compaction>, <https://developers.openai.com/api/docs/guides/compaction>.
- **CD-3 + CD-4** · `context-degradation/SKILL.md:15,59,194,238` — **Change:** add premature termination as a length-related symptom (<https://arxiv.org/abs/2606.29718>). Add Classifier Context Rot (<https://arxiv.org/abs/2605.12366>) and LOCA-bench (<https://arxiv.org/abs/2602.07962>) as evidence, and periodic reminders as a measured partial mitigation.
- **MS-6** · `memory-systems/SKILL.md:25,58-66,181,230-231` — **Change:** in memory benchmarks, fix the LLM and embedding model across arms, include a verbatim-RAG or filesystem baseline, report write-path cost, and stratify by question type. Sources: <https://www.letta.com/blog/benchmarking-ai-agent-memory>, <https://arxiv.org/abs/2606.29914>.
- **MS-8** · `memory-systems/SKILL.md:103` — Optional. Name Anthropic's client-side memory tool as a vendor implementation of file-system memory. Source: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool>.
- **TD-3** · `tool-design/SKILL.md:53,61,106-108`, `references/best_practices.md:23-27` — **Change:** for large catalogs, consider deferred loading or tool search before merging tools that do different things. Treat the reported numbers as vendor-scoped. Source: <https://www.anthropic.com/engineering/advanced-tool-use>.
- **LB-3** · `latent-briefing/SKILL.md:104,128,133-138` — **Change:** add token eviction to the strong baselines. Add a gotcha about the choice of proxy query and compaction timing (<https://arxiv.org/abs/2608.00902>). Require a mismatched-cache audit before claiming latent transfer (<https://arxiv.org/abs/2608.04893>). Treat KV state that crosses a process or trust boundary as security-sensitive (<https://arxiv.org/abs/2606.28958>).
- **HE-2** · `harness-engineering/SKILL.md:49-57,221-227` — **Change:** add "locked-surface mechanics": a feature list in which the agent may only flip `passes`, an `init.sh` smoke test, an initializer/coder split, and linters whose messages include the fix. Sources: <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>, <https://openai.com/index/harness-engineering/>.
- **HE-3** · `harness-engineering/SKILL.md:72,150,196,204` — In the skill's own source, the novelty-gated run could not improve the baseline, and prompt text did not stop the agent from halting. **Change:** recast the novelty gate as dedup against the registry. Handle stopped loops with external re-arm or a monitor. Source: <https://www.primeintellect.ai/auto-nanogpt>.
- **LH-2** · `long-horizon-prompting/SKILL.md:91,237`, `references/research-evidence.md:10,51` — BudgetThinker is a training method, not prompt evidence. Anthropic advises against token countdowns because they cause premature handoff. **Change:** split Gotcha 8: re-inject verified progress, and enforce budgets in the harness without showing token countdowns. Sources: <https://arxiv.org/abs/2508.17196>, <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5>.
- **LH-4b** · `long-horizon-prompting/SKILL.md:95,107,239`, `references/vendor-guidance.md` — **Change:** add a GPT-6 entry (it asks more questions and under-delegates, so state the autonomy grant and delegation intent explicitly), and qualify Gotcha 10. Source: <https://developers.openai.com/api/docs/guides/prompt-guidance>.
- **PD-3** · `project-development/SKILL.md:134-144,213-217` — **Change:** add batch APIs and cached prefixes as cost levers (they stack). Move parallelism out of the cost list, because it cuts latency, not cost. Source: <https://platform.claude.com/docs/en/about-claude/pricing>.
- **SIL-6** · `self-improvement-loops/SKILL.md:56-61,149,204` — Harness-update quality is flat across proposer capability. **Change:** measure proposer usefulness and executor uptake separately; a cheap proposer can be enough. Source: <https://arxiv.org/abs/2605.30621>.
- **SIL-7** · `self-improvement-loops/SKILL.md:78-80,120,146` — In WikiSkill, a consolidated knowledge layer on the proposer side improved skill evolution, and the paper reports that evolved skills transfer across models. **Change:** allow a consolidated proposer-side layer linked to raw traces. Validate each evolved skill on the target model before reuse. Name skill-library evolution at rung 3. Source: <https://arxiv.org/abs/2608.27454>. The reviewing agent reported a negative-transfer figure (50.5% → 18.1%) and an executor-side drop to 60.9%. Verify both against the paper before citing them, because the abstract reports positive transfer.
- **MSD-1** · `ml-system-design-review/references/rubrics.md:30,35` — **Change:** add history depth, seasonality coverage, and schema stability to the Data B/A cells. Add label delay and business KPIs linked to model metrics to the Monitoring B/A cells.
- **MSD-2** · `ml-system-design-review/references/rubrics.md:34` — Optional. Name the serving levers (batching, caching, model routing, quantization) in the A cell. Group with `MSD-1`.
- **MSD-3** · `ml-system-design-review/references/modern-ai-systems.md:92,103` — **Change:** "report pass^k for user-facing agents". Group with `MSD-1`.
- **LDC-3** · `lossless-doc-compress/references/compression-workflow.md:38-44`, `references/output-templates.md:54-56` — "lossless ✓" has no mechanical check. **Change:** before claiming lossless, require that numbers, identifiers, code blocks, and table cells appear byte-exact in the output. Reuse the gate wording from `simplified-engineering-english/SKILL.md:83`.

### 8.3 Leancode family

These items use the Leancode candidate gate.

- **LC-2** · `leancode/SKILL.md:64` — "If something is unclear, stop. Name what's confusing. Ask." conflicts with lines 58–60 and 67–70. **Change:** delete line 64.
- **LC-3** · `leancode/SKILL.md` after line 141 — **Change:** add "The check verifies the logic; it does not define it. Never special-case test inputs to make a check pass." Source: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md>.
- **LC-4** · existing Candidate 4 — Add an async variant to its fixtures: `@lru_cache` on an `async def` raises `RuntimeError: cannot reuse already awaited coroutine` on the second call.
- **LR-1** · `leancode-review/SKILL.md:58-61` — **Change:** never flag smoke tests or `assert` self-checks, validation at trust boundaries, error handling that prevents data loss, security or accessibility code, or anything the request required.
- **LR-2** · `leancode-review/SKILL.md:52` — **Change:** delete "the only metric that matters". Group with `LR-1`.
- **LA-1** · `leancode-audit/SKILL.md` Output, after line 42 — **Change:** each finding names the exact cut and its evidence; file size alone is not a finding. State which paths were scanned. This matches the existing eval oracles in `evals/cases/catalog-behavior-*.jsonl:13`.
- **LA-2** · `leancode-audit/SKILL.md:20,27` — The `scope:` tag has no request to compare against in a whole-repo audit. **Change:** delete the tag. Group with `LA-1`.
- **LA-3** · `leancode-audit/SKILL.md` Scan scope — **Change:** if the repository already has a dead-code analyzer (for example knip or vulture), run it and cite its output. Do not install one without asking. Confirm each `delete:` with a reference search. Group with `LA-1`.
- **LA-4** · `leancode-audit/SKILL.md:36-38` — **Change:** replace "files exporting one thing" with "modules whose single export has a single caller". Add "fallbacks for states internal code cannot reach" and "comments that restate the code". Group with `LA-1`.
- **LD-2** · `leancode-debt/SKILL.md:44` — **Change:** end with `<N> markers, <M> no-trigger, <K> no-ceiling.`
- **LD-3** · `leancode-debt/SKILL.md:22-26` — **Change:** start from `git grep -nI -F "lean-debt:"`, then keep hits inside comments. Group with `LD-2`.
- **HK-1** · `hooks/pre/leancode.ts:28` (was `.omp/hooks/pre/leancode.ts`) — The reminder reached report-only subagents during this review. **Change:** re-run Candidate 3 as a hook-only candidate that appends "an explicitly requested report or format wins". Candidate 3's development grade passed 21/21 critical; only the combined gate failed.

### 8.4 Simplified Engineering English

These items follow the SEE release governance.

- **SEE-1** · `references/rules.md:46` — STE Rule 4.2 bans all contractions. **Change:** strict prohibits all contractions. Engineering-default is unchanged.
- **SEE-2** · `references/rules.md:44,49-56` — The strict word count omits STE Rules 8.4 (a vertical-list colon ends a sentence) and 8.5 (a parenthetical counts as one word). **Change:** add both rules, or relabel the counting as "adapted".
- **SEE-3** · `references/rules.md:42`, `SKILL.md:50` — **Change:** in strict, list the Rule 3.2 tense set and apply Rules 3.4 and 3.5. Limit the perfect and progressive allowance to engineering-default.
- **SEE-5** · `SKILL.md:58-60`, `references/rules.md` procedure section — **Change:** add Rule 5.5 (notes give information, not instructions) to the procedure card as an error in both profiles. Add Rules 9.3 (no phrasal verbs) and 6.6 (at most six sentences per paragraph) as strict-only controls.

## 9. Wave 4 — Routing Changes (Class R)

Run these inside the description-density experiment (skill set plan §11), one family per treatment.

- **CF-2** · `context-fundamentals/SKILL.md:3` — Replace "U-shaped attention curve" with "position sensitivity and context rot". Chroma found no position effect across 11 needle positions on its task. Family: context core.
- **HE-1 + SIL-8** · `harness-engineering/SKILL.md:28-32` — Add exclusions: self-modified harnesses and prompts → `self-improvement-loops`; launch-brief wording → `long-horizon-prompting`. Both siblings already route loop governance here. Family: workflows.
- **PD-6** · `project-development/SKILL.md:3,26,148-158` versus `multi-agent-patterns/SKILL.md:3` — Both claim the single-versus-multi-agent decision. **Decision:** `project-development` owns "whether to build and pipeline shape". `multi-agent-patterns` owns "single versus multiple agents and topology". Add a routing pair for this boundary before the treatment.
- **LDC-4** · `lossless-doc-compress/SKILL.md:39-45` — Add exclusions: clarity rewrites → `simplified-engineering-english`; session handoffs → `context-compression`.
- **LD-4** · `leancode-debt/SKILL.md:8` — Replace "changes nothing" with "changes no source"; the skill writes `LEANCODE-DEBT.md` on request.

## 10. Verification

### 10.1 Deterministic checks (every wave)

```sh
python3 scripts/validate_skills.py
python3 evals/validate.py
python3 -m unittest discover -s tests
python3 -m unittest discover -s context-compression/tests
bun test tests/leancode_hook.test.ts
```

### 10.2 Script smoke checks (Wave 2)

Run each script that a Wave 2 commit touches, and check the stated result:

| Script | Expected result after the fix |
|---|---|
| `python3 evaluation/scripts/evaluator.py` | At least one case fails. |
| `python3 multi-agent-patterns/scripts/coordination.py` | Consensus strength 0.74 for the demo votes. |
| `python3 hosted-agents/scripts/sandbox_manager.py` | Exits 0. A follow-up with a snapshot restores the snapshot when the pool is warm. |
| `python3 context-fundamentals/scripts/context_manager.py` | Exits 0 and uses the supplied counter. |
| `python3 context-optimization/scripts/compaction.py` | Exits 0. One threshold parameter. |
| `python3 memory-systems/scripts/memory_store.py` | Exits 0. `query_at_time` takes a dict. |
| `python3 project-development/scripts/pipeline_template.py all --batch-id smoke` (in a temporary directory) | Exits 0. |

### 10.3 Reference code syntax check (Wave 2)

For each changed reference file, parse every fenced `python` block. A block labeled as pseudocode is exempt. Run this as a throwaway command; it is not a permanent test:

````sh
python3 - memory-systems/references/implementation.md <<'EOF'
import re, sys
for path in sys.argv[1:]:
    for i, block in enumerate(re.findall(r"```python\n(.*?)```", open(path).read(), re.S)):
        try:
            compile(block, f"{path}#{i}", "exec")
        except SyntaxError as e:
            print(f"{path} block {i}: {e}")
EOF
````

Replace the example path with the changed reference files. No output means every block compiles. Compiling does not catch missing imports or undefined names (`FC-1`, `MS-3`), so run those blocks after fixing them.

### 10.4 Live evaluation (Waves 3 and 4)

Use the commands, locked configuration, and gates in [the evaluation guide](../evals/README.md) and skill set plan §18.2. Each **G** treatment needs one development behavior case that observes the changed behavior. Add the case, with its `suites.json` hash update, in a commit before the skill change.

## 11. Owner Decisions

These items change policy or legal framing. Do not apply them without an explicit decision.

| ID | Question | Decision (2026-10-10) |
|---|---|---|
| LC-5 | `leancode` metadata says `adaptation: inspired` and that the copying direction is unverified. The review found that §1 and most of §3–§4 match upstream `CLAUDE.md` almost word for word, and that the upstream snapshot is six months older. Change to `adaptation: derived`? | **Keep `inspired`.** Copying direction stays unverified; `ATTRIBUTION.md` unchanged. |
| HE-5 | `harness-engineering/SKILL.md:82-84,206` forbid merge or push without human approval. OpenAI documents agents that merge their own changes when rollback is cheap. Add a standing-grant exception? | **No exception.** Approval per merge/push stays. |
| RP-6 | Send fixes upstream? | **Draft only.** Issue drafts in [upstream/](upstream/); the owner files them. |

## 12. Rejected

Closed: see [Content Refresh: Rejected Proposals](decisions/0011-content-refresh-rejected-proposals.md).

## 13. Definition of Done

- [x] Wave 1 items `RP-1` to `RP-5` are merged, and the deterministic checks pass.
- [x] Every Wave 2 item is merged or rejected with a reason, and its smoke check passed.
- [ ] Every Wave 3 item has a development behavior result, and every merged item has a holdout result under skill set plan §18.2.
- [ ] Every Wave 4 item ran inside the description-density experiment.
- [x] Every Section 11 decision is recorded.
- [x] `ATTRIBUTION.md` and the skill metadata match the synced upstream commits.

## 14. Implementation Status (2026-10-06)

- **Applied in the working tree:** every item in Sections 6–9 except the Section 11 owner decisions. No item was rejected. `ATTRIBUTION.md` records `LDC-1` and `MSD-1` as modifications.
- **Proposed evaluation cases:** `evals/cases/refresh-behavior-development.jsonl` (36 behavior cases, one per **G** treatment group) and `evals/cases/refresh-routing-development.jsonl` (12 routing cases covering both directions of every **R** pair). Both are registered as canonical development suites `refresh-behavior` and `refresh-routing`. Holdout files for these suites do not exist yet; write them after the development runs, without tuning against them.
- **HK-2:** fallback branch applied. `LEGACY_REMINDERS` is now derived from `leancodeReminder()`. `evals/mode_smoke.py` asserts that no prior reminder reaches `context` (probe: `evals/leancode_context_probe.ts`), but its only run (`evals/results/content-refresh/mode-smoke-hk2.json`) failed before any model turn, so the filter stays until the assertion passes.
- **Blocked:** every live gate (Section 10.4, `HK-1` Candidate 3 rerun, `HK-2` smoke). The pinned evaluation profile `skill-eval-isolated` has no valid `openai-codex` credential (`No API key found for openai-codex`; refresh token rejected). Unblock: run `omp --profile skill-eval-isolated` and `/login`, then run `refresh-behavior` and `refresh-routing` baseline and treatment per `evals/README.md`.
- **Owner decisions:** recorded in Section 11 (2026-10-10).
