# Draft issue: ML-SystemDesign/MLSystemDesign

Target: https://github.com/ML-SystemDesign/MLSystemDesign, `skills/lossless-doc-compress` at commit `61b9bcdb971e7424cdc4d400085338dc35da910e`. Not filed; the owner files it (RP-6, `docs/skill-content-refresh-plan.md` §11).

**Title:** lossless-doc-compress: two "removable hedge" examples change meaning

**Body:**

`references/slop-and-hedging.md` and `references/removal-taxonomy.md` list "essentially identical" → "identical" as a safe removal. That turns approximate equality into exact equality, which `references/fidelity-rules.md` (lines 44–48) forbids. "quite" is also listed as removable, but it often changes degree ("quite slow" ≠ "slow").

Fix: move the "essentially identical" example to the KEEP or FLAG list, and remove "quite" from the removable hedges.

Our applied version: `skills/lossless-doc-compress/references/{slop-and-hedging,removal-taxonomy}.md` in https://github.com/lafin/skills.
