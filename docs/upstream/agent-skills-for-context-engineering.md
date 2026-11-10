# Draft issue: muratcankoylan/Agent-Skills-for-Context-Engineering

Target: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering, observed at commit `58b55a8921758d13453b440704fb1b5b208c0b0e` (v2.6.0). Not filed; the owner files it (RP-6, `docs/skill-content-refresh-plan.md` §11).

**Title:** Small correctness fixes in evaluation, advanced-evaluation, memory-systems, multi-agent-patterns

**Body:**

1. **evaluation/scripts/evaluator.py: missing evidence passes.** Each dimension without evidence falls back to a default (0.7/0.8/0.8/0.5/0.8). The defaults average 0.74, above the 0.7 pass threshold, so empty output and the wrong answer `"London"` both pass. `expected["answer"]` is never read. Fix: score missing evidence as `unknown` and exclude it, fail when no dimension is scored, read `expected["answer"]`; the demo then shows at least one failure.
2. **advanced-evaluation/references/metrics-guide.md: `await` in a plain `def`** is a SyntaxError. Fix: `async def`.
3. **advanced-evaluation/references/bias-mitigation.md: "~55% first-position preference"** does not match MT-Bench Table 2 (Claude-v1 75.0%, GPT-3.5 50.0%, GPT-4 30.0%; https://arxiv.org/abs/2306.05685). Fix: drop per-vendor numbers; state that position bias varies by judge and prompt and is measured by swapping order on the target judge.
4. **memory-systems: Mem0 v3 API.** Entity IDs go in `filters=` for `search`, and `add` takes a messages list; `add` is add-only, so "returns only the current preference" is unsupported. Fix: `m.add(messages, user_id=...)`, `m.search(q, filters={"user_id": ...})`, remove the supersession claim. Sources: https://docs.mem0.ai/core-concepts/memory-operations/add, https://docs.mem0.ai/core-concepts/memory-operations/search.
5. **memory-systems/references/implementation.md: Graphiti `add_episode`** requires `reference_time`. Fix: pass `reference_time=datetime.now(timezone.utc)`.
6. **multi-agent-patterns/references/frameworks.md: LangGraph examples.** The supervisor example has no `END` and loops; the swarm example uses static edges and an undefined `State`; `langgraph-supervisor` is unmaintained. Fix: rewrite with `Command(goto=..., graph=Command.PARENT)` or reduce to labeled pseudocode. Source: https://docs.langchain.com/oss/python/migrate/langgraph-supervisor.

Our applied versions: `skills/evaluation/scripts/evaluator.py`, `skills/advanced-evaluation/references/{metrics-guide,bias-mitigation}.md`, `skills/memory-systems/`, `skills/multi-agent-patterns/references/frameworks.md` in https://github.com/lafin/skills.
