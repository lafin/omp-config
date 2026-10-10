# Content Refresh Wave 2: Systems Defects

- **Status:** Completed
- **Date:** 2026-10-06
- **Source:** [Skill Content Refresh Plan §7.3 Systems](../skill-content-refresh-plan.md#73-systems)

## Decision

Applied as Class D (gate: deterministic checks plus the item's smoke check; no live evaluation). Wave 2 grouped commits by skill family, one commit per family, to keep review small and revert easy. Paths and line numbers below are the review baseline `7529a16`; skill directories now live under `skills/`.

- **MS-1** · `memory-systems/SKILL.md:127-132`, `references/implementation.md:492-505` — The Mem0 v3 API puts entity IDs inside `filters=`, and `add` takes a messages list. The claim that Mem0 returns only the current preference is unsupported: `add` is add-only. **Change:** use `m.add(messages, user_id=...)` and `m.search(q, filters={"user_id": ...})`, remove the supersession claim, and record the SDK version. Sources: <https://docs.mem0.ai/core-concepts/memory-operations/search>, <https://docs.mem0.ai/core-concepts/memory-operations/add>.
- **MS-2** · `memory-systems/references/implementation.md:515-523` — Graphiti `add_episode` requires `reference_time`. **Change:** add `reference_time=datetime.now(timezone.utc)`. Source: <https://raw.githubusercontent.com/getzep/graphiti/main/graphiti_core/graphiti.py>.
- **MS-3** · `memory-systems/SKILL.md:95`, `references/implementation.md:234-237,303,361-374,390-402` — The "working consolidation code" calls undefined methods (`update_validity_periods`, `rebuild_indexes`, `_get_edge`, `_extract_label`, `_extract_type`, `_extract_where`) and deletes edges. Deleting edges breaks the skill's "invalidate, do not discard" rule (`SKILL.md:95,178`). **Change:** set `valid_until` instead of deleting, and either define the methods or label the block as pseudocode.
- **MS-4** · `memory-systems/SKILL.md:137-150`, `references/implementation.md:309`, `scripts/memory_store.py:383` — `query_at_time` has two signatures. **Change:** use the script's dict form everywhere.
- **MS-5** · `memory-systems/SKILL.md:156,164,168`, `references/implementation.md:533-541` — Cognee v1.0 lists `memify()` as a legacy operation (replaced by `improve()`), and the default `query_type` is `HYBRID_COMPLETION`. **Change:** update and date the examples. Sources: <https://docs.cognee.ai/core-concepts/main-operations/legacy-operations/memify.md>, <https://docs.cognee.ai/python-api/search.md>.
- **MS-7** · `memory-systems/SKILL.md:21,106` — The Letta Filesystem API is deprecated and disabled. **Change:** date the Letta guidance and name its replacement. Source: <https://docs.letta.com/v1-sdk/concepts/filesystem>. Also correct the MemBench venue to Findings of ACL 2025 (<https://aclanthology.org/2025.findings-acl.989/>).
- **FC-1** · `filesystem-context/references/implementation-patterns.md:243-253` — The `SkillLoader` block uses `@dataclass` and `field` without importing them. **Change:** add `from dataclasses import dataclass, field`.
- **FC-3** · `filesystem-context/references/implementation-patterns.md:545-548` — The targets (<20%, >50%, >70%) have no source. **Change:** label them as illustrative or delete them.
- **FC-4** · `filesystem-context/SKILL.md:135` — "O(n) static token cost into O(1)" is wrong; the index stays O(n). **Change:** "O(n) one-line index plus O(k) loaded bodies".
- **FC-5** · `filesystem-context/SKILL.md:102,305-308` — The external resources have no URLs, and the "recitation" quote has no attribution. **Change:** add URLs (<https://agentskills.io/specification>, <https://www.letta.com/blog/benchmarking-ai-agent-memory>). Verify and attribute the quote (**[INFERENCE]**: likely the Manus context-engineering post).
- **TD-4** · `tool-design/references/architectural_reduction.md:11-48` — The block wraps the TypeScript-only AI SDK in Python syntax and uses the invalid model ID `"claude-opus-4.5"`. **Change:** replace it with model-neutral pseudocode, or quote the TypeScript source labeled "as published December 2025". Source: <https://vercel.com/blog/we-removed-80-percent-of-our-agents-tools>.
- **TD-5** · `tool-design/SKILL.md:53`, `references/best_practices.md:117` — Two research claims have no citation. **Change:** cite <https://www.anthropic.com/engineering/advanced-tool-use> or soften.
- **LB-1** · `latent-briefing/SKILL.md:160`, `references/attention-matching-formulation.md:7` — The primary source is an X post. **Change:** cite Ramp Labs, "Latent Briefing", Ben Geist, 2026-04-10: <https://labs.ramp.com/research/latent-briefing-kv-cache/index.md>.
- **LB-2** · `latent-briefing/SKILL.md:27,89-97,136` — The skill tells readers to interpret results it never states. **Change:** add a dated evidence block in `references/`, in the style of `tool-design/references/d0-evidence.md`: Claude Sonnet 4 orchestrator, Qwen3-14B worker, LongBench v2, n=42 per condition, ~65% fewer worker tokens, +3 pp at the best threshold, uniform head weights. State that the orchestrator model is retired, so exact reproduction is not possible.
- **LB-4** · `latent-briefing/SKILL.md:45,70`, reference line 59 — The threshold is called `tau` in one file and `k` in the other. **Change:** use one name, and state that negative thresholds keep more than the median.
- **BDI-1** · `bdi-mental-states/SKILL.md:161-179`, `references/rdf-examples.md:166-176`, `references/framework-integration.md:480-498`, `references/sparql-competency.md:206-210` — `hasStartTime` and `hasEndTime` are object properties with range `:TimeInstant`. Queries compare them directly to `xsd:dateTime` literals and return nothing. **Change:** use `?interval bdi:hasStartTime/bdi:time ?s`, and model instants as IRIs that carry `bdi:time`. Source: <https://w3id.org/fossr/ontology/bdi/>.
- **BDI-2** · `bdi-mental-states/references/bdi-ontology-core.md:107-112` — `owl:maxCardinality 1` on `hasValidity` is not in the published ontology, which uses an existential restriction. **Change:** use the existential form or label the restriction a local extension.
- **BDI-3** · `bdi-mental-states/SKILL.md:295-299`, `references/sparql-competency.md:163-170` — CQ4 orders by IRI, and the transitive `precedes` returns every successor. **Change:** walk from `bdi:beginsWith` with non-transitive adjacency.
- **BDI-4** · `bdi-mental-states/SKILL.md:23,369` — **Change:** cite Journal of Web Semantics 2026, DOI `10.1016/j.websem.2026.100885`, arXiv `2511.17162`. Mark the JADE/JADEX mappings as illustrative.
- **BDI-5** · `bdi-mental-states/SKILL.md:217-221` — There is an empty `### Integration Patterns` heading, and `## Detailed Topics` is out of order. **Change:** delete the heading and move the section.

## Evidence

- `MS-1`: `skills/memory-systems/SKILL.md:136-143` (Mem0 OSS v3 API, `mem0ai` 2.x, `filters=`); `skills/memory-systems/references/implementation.md:457`
- `MS-2`: `skills/memory-systems/references/implementation.md:480-486`
- `MS-3`: `skills/memory-systems/references/implementation.md:263-333` (`valid_until`; edges stay in place)
- `MS-4`: `skills/memory-systems/SKILL.md:158`; `skills/memory-systems/references/implementation.md:284`; `skills/memory-systems/scripts/memory_store.py:383`
- `MS-5`: `skills/memory-systems/SKILL.md:170-180`; `skills/memory-systems/references/implementation.md:507`
- `MS-7`: `skills/memory-systems/SKILL.md:115` (Letta Filesystem deprecated as of 2026-10-06), `:242` (MemBench, Findings of ACL 2025)
- `FC-1`: `skills/filesystem-context/references/implementation-patterns.md:248`
- `FC-3`: `skills/filesystem-context/references/implementation-patterns.md:550` (labeled illustrative)
- `FC-4`: `skills/filesystem-context/SKILL.md:140`
- `FC-5`: `skills/filesystem-context/SKILL.md:107` (Manus recitation attribution), `:314-315`
- `TD-4`: `skills/tool-design/references/architectural_reduction.md:11-14` (model-neutral pseudocode, December 2025 source)
- `TD-5`: `skills/tool-design/SKILL.md:53,108`; `skills/tool-design/references/best_practices.md:29,130` (cite advanced-tool-use)
- `LB-1`: `skills/latent-briefing/SKILL.md:164`; `skills/latent-briefing/references/attention-matching-formulation.md:7`
- `LB-2`: `skills/latent-briefing/references/ramp-evidence.md:3-9` (n=42, Sonnet 4 retired 2026-06-15, no exact reproduction)
- `LB-4`: `skills/latent-briefing/SKILL.md:45,70,135`; `skills/latent-briefing/references/attention-matching-formulation.md:59-62` (`tau` throughout)
- `BDI-1`: `skills/bdi-mental-states/SKILL.md:181`; `references/sparql-competency.md:217,245`; `references/framework-integration.md:324-325,503` (`hasStartTime/bdi:time`)
- `BDI-2`: `skills/bdi-mental-states/references/bdi-ontology-core.md:113` (`owl:someValuesFrom bdi:TimeInterval`)
- `BDI-3`: `skills/bdi-mental-states/SKILL.md:301-304`; `references/sparql-competency.md:166-170`
- `BDI-4`: `skills/bdi-mental-states/SKILL.md:23,382`
- `BDI-5`: `skills/bdi-mental-states/SKILL.md:35,202` (no `### Integration Patterns` heading; `## Detailed Topics` follows Core Concepts)
