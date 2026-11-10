# Content Refresh Wave 2: Leancode Family Defects

- **Status:** Completed
- **Date:** 2026-10-06
- **Source:** [Skill Content Refresh Plan §7.1 Leancode family and hook](../skill-content-refresh-plan.md#71-leancode-family-and-hook)

## Decision

Applied as Class D (gate: deterministic checks plus the item's smoke check; no live evaluation). Wave 2 grouped commits by skill family, one commit per family, to keep review small and revert easy. Paths and line numbers below are the review baseline `7529a16`; skill directories now live under `skills/`. `HK-2` (same section) stays open in the plan: its smoke assertion has not passed.

- **LC-1** · `leancode/SKILL.md:183` — "a PCA9685 runs a few percent fast" is wrong. The oscillator lands anywhere from about 23 to 27 MHz around the nominal 25 MHz, in either direction. **Change:** state that range. Keep the paragraph. Source: <https://raw.githubusercontent.com/adafruit/Adafruit-PWM-Servo-Driver-Library/master/examples/servo/servo.ino> lines 49–64.
- **LD-1** · see `RP-3`.

## Evidence

- `LC-1`: `skills/leancode/SKILL.md:183-184` (23 to 27 MHz around nominal 25 MHz)
- `LD-1`: see `RP-3` evidence in [Wave 1 record](0005-content-refresh-wave-1-hygiene.md)
