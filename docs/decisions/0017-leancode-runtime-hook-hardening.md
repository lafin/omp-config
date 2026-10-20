# Leancode Runtime Hook Hardening

- **Status:** Completed
- **Date:** not stated (`mode-smoke-production-v3.json` captured 2026-09-11)
- **Source:** [Leancode Improvement Plan §6 Runtime Hook Plan](../leancode-improvement-plan.md#6-runtime-hook-plan) (§6.1–§6.3), [§7 Implementation Sequence](../leancode-improvement-plan.md#7-implementation-sequence) (Phase 3)

## Decision

Shipped as the only accepted production change (see [Leancode Improvement Release Decision](0015-leancode-release-decision.md)): generated reminders have agent attribution, replacement uses a stable marker (`[omp:leancode-state]`) for owned messages, and unattributed migration removes only exact known legacy reminders. Mode state persists for one OMP process; a fresh process defaults to `full`. The §6.2 requirements and the §6.3 report-exception test stay open in the plan. Later hook changes (`HK-1`, `HK-2`) are tracked in the skill content refresh plan.

### §6.1 Test the Real Lifecycle

Run an actual OMP session scenario that covers:

1. default startup in `full`;
2. `/leancode lite`;
3. `/leancode full`;
4. `/leancode ultra`;
5. `/leancode off`;
6. reload and mode query;
7. process restart;
8. a user message that quotes the marker text;
9. replacement of current and legacy reminders.

Record the observed lifecycle before deciding whether mode state should persist only in a module, in a session, or across processes.

### §6.2 Make Reminder Replacement Stable

The pre-release hook removed an exact reminder string. After reproducing lifecycle behavior, prefer a stable machine marker for hook-owned context so wording changes do not leave stale reminders.

### §6.3 Expand Hook Tests

Add focused tests only for reproduced or required behavior: real lifecycle state boundaries; legacy reminder replacement after prompt wording changes; duplicate prevention; user-authored marker-like text preservation; explicit `off` behavior; report and plan exception in injected reminder text (still open).

### Phase 3: Runtime Hardening

Files: `hooks/pre/leancode.ts`; `tests/leancode_hook.test.ts`; lifecycle test or smoke script under existing test conventions.

Work:

1. Observe actual lifecycle behavior.
2. Define the intended persistence boundary.
3. Implement stable hook-owned reminder replacement if the reproduction shows a need.
4. Migrate current and legacy reminders in one clean cutover.
5. Verify all modes and `off` in a real session.

Exit gate: unit and real-session checks agree on every supported transition. Result: `mode-smoke-production-v3.json` passed all 8 checks (`fresh_process_defaults_full`, `lifecycle_process_passed`, `mode_notifications_observed`, `mode_sequence_observed`, `quoted_marker_preserved`, `reload_observation_recorded`, `reload_preserved_off`, `restart_process_passed`) on `openai-codex/gpt-5.6-sol`, profile `skill-eval-isolated`, thinking off; `bun test tests/leancode_hook.test.ts` passed 9 of 9.

## Evidence

- [`hooks/pre/leancode.ts`](../../hooks/pre/leancode.ts) (released as `.omp/hooks/pre/leancode.ts`, sha256 `2c38dd3e105f406ab80d390a8b24ac3d9990ab7e339a60d959f07e4a85ec9b0f`)
- [`tests/leancode_hook.test.ts`](../../tests/leancode_hook.test.ts)
- [`evals/mode_smoke.py`](../../evals/mode_smoke.py); `evals/README.md` § Verify leancode modes
- [`mode-smoke-production-v3.json`](../../evals/results/leancode-improvement/mode-smoke-production-v3.json); earlier runs `mode-smoke-before.json`, `mode-smoke-after.json`, `mode-smoke-final.json`, `mode-smoke-production.json`, `mode-smoke-production-v2.json`
- [`rollback.json`](../../evals/results/leancode-improvement/rollback.json)
