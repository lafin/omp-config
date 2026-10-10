# Content Refresh: Rejected Proposals

- **Status:** Rejected
- **Date:** 2026-10-06
- **Source:** [Skill Content Refresh Plan §12 Rejected](../skill-content-refresh-plan.md#12-rejected)

## Decision

The 2026-10-06 content review rejected these proposals:

| Proposal | Reason |
|---|---|
| Import `self-managed-context` | See `RP-4` in the [Wave 1 record](0005-content-refresh-wave-1-hygiene.md). |
| Add upstream routing lines that point to `self-managed-context` | The skill is not in the catalog. |
| Import `EXAMPLES.md` from `andrej-karpathy-skills` | ~520 lines, one broken example, no new rules. |
| Add price or context-window tables to skills | They go stale quickly. Link provider docs instead. |
| Add a validator denylist of retired model IDs | Brittle. The model-neutral rule (`RP-1`) removes most IDs instead. |
| Add a validator check for drift between the shared blocks in `ai-stage-gate` and `ml-system-design-review` | Low value for two copies. Review them manually during `RP-5`. |
| Hard-code EU AI Act dates in `ai-stage-gate` | Not verified, and they go stale. |
| Edit `leancode/SKILL.md:108` to absorb "don't annotate unchanged code" | The gap is small; line 119 already covers type hints. Revisit only inside Leancode Candidate 5. |

## Evidence

- [Conditional skill decisions: Self-managed context](../conditional-skill-decisions.md#self-managed-context) records the `self-managed-context` deferral.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) lines 53-58 hold the `RP-5` drift check under which the shared blocks are reviewed manually.
- Leancode Candidate 5 lives in the [Leancode improvement plan](../leancode-improvement-plan.md#candidate-5-reduce-prompt-density).
