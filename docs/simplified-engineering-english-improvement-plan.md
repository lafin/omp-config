# Simplified Engineering English Improvement Plan

## 1. Purpose

Improve `simplified-engineering-english` without changing technical meaning, obligation force, security properties, or user-visible facts during a rewrite.

The work must answer four questions:

1. Does the skill preserve facts, conditions, qualifiers, numbers, units, versions, identifiers, and obligation force?
2. Does the skill reduce consequential ambiguity and improve actionability across its supported artifact types?
3. Which rules should be hard requirements, review warnings, strict-profile controls, or project-specific choices?
4. Which conformance claims can the repository support with deterministic checks, semantic review, and retained evaluation evidence?

Status: the revision is implemented and evaluated, but the release decision is `INCONCLUSIVE` ([release report](../evals/results/see-improvement/release-report.md)). Open work: §13 Phases 4–6, §14, and the unresolved hypotheses in §3.3.

## 2. Decision Summary

Closed: see [SEE Preservation-First Revision Specification](decisions/0013-see-revision-specification.md).

Do not treat a difference from Google, Microsoft, or another style guide as proof that an SEE rule is wrong. Those guides provide context and alternatives. Retain a strict rule when its selected profile requires it and evaluation supports it.

## 3. Current State

### 3.1 Components

Closed: see [SEE Pre-Revision State and Confirmed Defects](decisions/0012-see-pre-revision-defects.md).

### 3.2 Confirmed High-Risk Defects

Closed: see [SEE Pre-Revision State and Confirmed Defects](decisions/0012-see-pre-revision-defects.md).

### 3.3 Unverified Design Risks

Treat these statements as hypotheses until paired evaluations test them:

- Loading all 82 rules before selecting an artifact mode can reduce instruction salience.
- Fourteen artifact rows can create overlapping or inconsistent behavior.
- Hard sentence caps can improve strict controlled text but reduce clarity in ordinary explanatory text.
- Universal bans on passive voice, contractions, perfect constructions, and future tense can cause unnecessary or meaning-changing rewrites.
- A shorter `SKILL.md` with detailed rules in a reference file can reduce input cost without reducing quality.
- A language model can review semantic SEE rules reliably enough to support a release gate.

Evidence so far (local captures, not a release claim): the combined candidate raised behavior token cost (+232,337 development, +200,547 holdout), so input-cost reduction is unsupported; the independent judge was position-sensitive on 30 of 78 swapped pairs, so model-only semantic review is not yet reliable enough for a release gate.

### 3.4 Strengths to Preserve

Keep these mechanisms unless evaluation finds a regression:

- one concept and one term within a defined context;
- protected identifiers, commands, paths, literal values, versions, and quoted output;
- conditions before consequential instructions;
- explicit actors when responsibility matters;
- one independently reviewable action or obligation per unit;
- prerequisites and observable results for procedures;
- risk information before the governed action;
- measured performance, reliability, security, and scale claims;
- separation of observations from hypotheses;
- human technical review after automated checks.

## 4. Success Criteria

A candidate revision can ship only when all of the following conditions are true:

1. Baseline and treatment runs use the same pinned model, profile, tools, reasoning settings, case inputs, and attempt count.
2. The candidate introduces zero critical changes to facts, conditions, qualifiers, numbers, units, versions, identifiers, commands, quotations, obligation force, or supported uncertainty.
3. The candidate does not invent an actor, cause, date, measurement, recovery action, exception, or requirement.
4. Every development and holdout case passes its deterministic preservation checks.
5. The candidate does not regress on already-compliant no-op cases.
6. The candidate reduces consequential ambiguity on both development and holdout cases.
7. Technical fidelity does not regress in any artifact family.
8. The strict profile enforces its declared controlled-language rules consistently.
9. The engineering-default profile does not enforce house-style choices as universal correctness rules.
10. Every claimed automated rule names the checker and exact rule ID that enforces it.
11. Every semantic rule names the required reviewer and evidence.
12. Routing coverage distinguishes SEE from adjacent prose, evaluation, implementation, and review skills.
13. Any increase in prompt tokens, output tokens, tool calls, questions, or latency has a recorded correctness benefit.
14. Repository validation and focused evaluation tests pass.
15. The retained evaluation artifacts satisfy the contracts in `evals/README.md`.

Do not set an aggregate quality threshold before baseline measurement. Record critical floors and per-dimension thresholds before the first treatment run.

## 5. Rule Authority and Precedence

### 5.1 Authority Categories

Every rule must use one category:

| Category | Meaning | Example |
| --- | --- | --- |
| `adopted` | The rule retains the source requirement within the source's declared scope. | BCP 14 uppercase keyword meaning in a document that declares BCP 14. |
| `adapted` | The rule changes the source mechanism for a software context. | Software-focused risk labels derived from STE safety instructions. |
| `SEE-policy` | The rule is a local controlled-language decision. | One obligation keyword per atomic normative statement. |
| `house-style` | The project can replace the rule without losing SEE semantics. | American English spelling or contraction policy. |
| `heuristic` | The rule identifies text for review and does not prove a defect. | Sentence length or possible passive voice outside the strict profile. |

### 5.2 Precedence

Apply rules in this order:

1. Safety, security, privacy, legal, and regulatory constraints.
2. Technical meaning, including facts, scope, conditions, qualifiers, units, versions, uncertainty, and obligation force.
3. Verbatim identifiers, commands, literal values, and required quotations, except when an authorized security rule requires redaction.
4. Authoritative language, protocol, platform, and product terminology.
5. The project glossary and artifact contract.
6. The selected SEE profile and artifact card.
7. General SEE defaults.
8. Concision and stylistic preference.

A lower-precedence rule must not alter a higher-precedence property.

### 5.3 Rule Record

Each retained or new rule must state: stable rule ID; concise rule text; applicable profile and artifact card; severity (error, warning, or suggestion); enforcement class (deterministic, parser-assisted, semantic review, or technical review); source URL and source section when applicable; source relationship from Section 5.1; exceptions; compliant example; counterexample; rationale or measured failure class.

Store the full records in `simplified-engineering-english/references/rules.md`. Keep only the workflow, universal invariants, and profile-selection table in `SKILL.md`.

Do not create a separate machine-readable registry until an implemented checker needs one. If tooling needs structured rule data, make that data canonical and generate duplicate documentation from it rather than maintaining two manual copies.

## 6. Target Skill Structure

Closed: see [SEE Preservation-First Revision Specification](decisions/0013-see-revision-specification.md).

## 7. Correctness Changes

Closed: see [SEE Preservation-First Revision Specification](decisions/0013-see-revision-specification.md).

## 8. Language Policy Changes to Evaluate

Closed: see [SEE Preservation-First Revision Specification](decisions/0013-see-revision-specification.md).

## 9. Dictionary Plan

Closed: see [SEE Preservation-First Revision Specification](decisions/0013-see-revision-specification.md).

## 10. Accessibility and Internationalization

Closed: see [SEE Preservation-First Revision Specification](decisions/0013-see-revision-specification.md).

## 11. Enforcement Plan

Status: `references/rules.md` "Coverage Declaration" lists the implemented deterministic evaluation checks (`SEE-SPAN-01`, `SEE-QUOTE-01`, `SEE-BCP14-02`, and case-specific predicates in `evals/grade.py`). No general production checker, Vale configuration, or parser-assisted checker exists. The remaining checks below are Phase 4 work.

### 11.1 Deterministic Lexical Checks

Suitable checks include: prohibited rewrite terms outside exempt scopes; approved product spelling and casing; rejected glossary alternatives; uppercase BCP 14 keywords in a declared BCP 14 profile; forbidden literal patterns; exact protected-span preservation between source and rewrite; required headings or labels in a structured artifact; sentence and paragraph counts under a documented tokenizer.

### 11.2 Parser-Assisted Structural Checks

Suitable checks include: warning placement before a destructive step; numbered sequential procedure steps; prerequisites before the first step; requirement IDs and rationale placement; artifact-specific required sections; code and quotation exemptions; document- or section-level version metadata.

Use Vale scopes when they express the rule correctly. Use the existing evaluation grader or a small project script when cross-block ordering or source-to-rewrite preservation is required.

### 11.3 Semantic Review

Require human or calibrated model review for: word sense; ambiguous reference; technical accuracy; appropriate actor omission; atomicity; EARS suitability; measurable verification; safe disclosure; completeness; preserved uncertainty and causal status.

A model review must return evidence before a verdict and must identify the source span that supports each finding.

### 11.4 Technical-Authority Review

A qualified technical reviewer remains responsible for: correctness; safety; security; completeness; feasible requirements; operational validity; product-specific terminology; approval to publish.

### 11.5 Coverage Declaration

Replace broad conformance levels with a generated or explicit coverage statement:

```text
Deterministic checks: SEE-TERM-01, SEE-SPAN-01, SEE-BCP14-01
Parser-assisted checks: SEE-PROC-02, SEE-RISK-03
Semantic review: SEE-REQ-04, SEE-EVID-02
Technical approval: required
```

Do not describe a document as SEE-conforming unless every applicable rule has an enforcement result and the required technical review is complete.

## 12. Evaluation Design

### 12.1 Freeze the Baseline

Before changing `SKILL.md` or `dictionary.md`:

1. Record the repository commit and skill hashes.
2. Pin the exact model snapshot.
3. Use an isolated profile with no unrelated MCP servers, hooks, rules, extensions, or sessions.
4. Record the reasoning settings and tool policy.
5. Freeze development and holdout cases.
6. Run at least three attempts per stochastic case.
7. Retain raw requests, responses, usage, runtime data, and grader evidence.
8. Do not reconstruct a baseline from a treatment run.

A comparison is invalid when baseline and treatment differ in model, prompt inputs, tools, profile, reasoning settings, timeout policy, case data, or grading logic.

### 12.2 Behavior Corpus

Closed: see [SEE Baseline, Evaluation Corpus, and Implementation Phases 0–3](decisions/0014-see-baseline-corpus-and-phases-0-3.md).

### 12.3 Routing Corpus

Closed: see [SEE Baseline, Evaluation Corpus, and Implementation Phases 0–3](decisions/0014-see-baseline-corpus-and-phases-0-3.md).

### 12.4 Adversarial Coverage

The complete corpus must include:

- a `MUST NOT` security requirement;
- correct simultaneous use of authentication and authorization;
- correct simultaneous use of parameter and argument;
- quoted output containing `and/or`;
- a protected identifier such as `legacyFlag`;
- an actionable local path and a sensitive server path;
- an unknown deprecation-removal version;
- legitimate asynchronous future tense;
- passive voice with an unknown actor;
- a 20/21-word procedural boundary;
- a 25/26-word descriptive boundary;
- a warning before a destructive operation;
- correct use of fault, error, and failure;
- a mean latency and a tail-latency claim with distinct purposes;
- a requirement verified by analysis or inspection;
- an ambiguous source that the agent must report rather than silently resolve.

Status: the 20/21-word and 25/26-word boundary cases exist only in historical suites (`evals/cases/see-behavior-holdout.jsonl`, `evals/cases/see-behavior-development-v2.jsonl`), not in the active development, independent-holdout, or release-holdout suites.

### 12.5 Case Manifest

Each case must record: artifact family; selected profile; source facts; protected spans; quoted spans; conditions and exceptions; numbers, units, versions, and status codes; expected obligation force; permitted rewrites; required structure; known ambiguity traps; prohibited inventions; deterministic checks; judge criteria when necessary.

### 12.6 Deterministic Gates

Fail a candidate on any of these outcomes:

- changed protected identifier, command, path, literal, or quotation without an authorized redaction rule;
- changed number, unit, version, status code, condition, exception, or obligation force;
- invented actor, fact, cause, date, measurement, recovery, or commitment;
- deleted material qualification or uncertainty;
- leaked secret or unauthorized internal detail;
- risk information placed after the destructive action;
- missing required artifact structure;
- changes to a no-op case without an identified defect.

### 12.7 Quality Dimensions

Score each dimension separately on a defined 0 through 4 rubric:

1. Technical fidelity.
2. Residual consequential ambiguity.
3. Actionability or objective verifiability.
4. Readability and scanability.
5. Selected-profile compliance.
6. Unnecessary-edit rate.
7. Source traceability of reviewer findings.

Do not allow an aggregate score to hide a technical-fidelity failure.

Set critical floors before treatment evaluation. Initial proposed floors are:

- technical fidelity: at least 3 in every case and no critical mutation;
- ambiguity: at least 3 for operational and normative artifacts;
- profile compliance: at least 3;
- readability: at least 2;
- protected-span preservation: exact unless authorized redaction applies.

Calibrate or replace these numeric floors from the frozen baseline before using them as a release claim. (`evals/see-rubric.json` records these floors; calibration depends on the human review in §12.8.)

### 12.8 Model and Human Judgment

Use deterministic grading first.

For residual semantic or preference judgments:

1. Use a judge model from a different model family when available.
2. Hide condition labels.
3. Compare baseline and treatment in both A/B orders.
4. Require evidence before the verdict.
5. Report position-sensitive disagreements.
6. Calibrate the rubric on a human-reviewed sample.
7. Route low-confidence and safety-sensitive results to a human reviewer.
8. Retain per-dimension results and confidence.

Human review must cover at least a representative sample from each artifact family and every candidate critical regression.

### 12.9 Cost and Attention Metrics

Record: skill input tokens; cache-read tokens; output tokens; total tokens; tool calls; questions; runtime; invalid or incomplete responses.

Treat reduced prompt cost from progressive disclosure as a hypothesis. A shorter prompt cannot ship when it reduces technical fidelity, ambiguity detection, or profile compliance.

## 13. Implementation Sequence

Test small changes independently. Do not combine all revisions into one treatment because a combined result cannot identify which change caused an improvement or regression.

### Phase 0: Baseline and Rule Inventory

Closed: see [SEE Baseline, Evaluation Corpus, and Implementation Phases 0–3](decisions/0014-see-baseline-corpus-and-phases-0-3.md).

### Phase 1: Correctness and Precedence

Closed: see [SEE Baseline, Evaluation Corpus, and Implementation Phases 0–3](decisions/0014-see-baseline-corpus-and-phases-0-3.md).

### Phase 2: Profiles and Progressive Disclosure

Closed: see [SEE Baseline, Evaluation Corpus, and Implementation Phases 0–3](decisions/0014-see-baseline-corpus-and-phases-0-3.md).

### Phase 3: Dictionary and Glossary Governance

Closed: see [SEE Baseline, Evaluation Corpus, and Implementation Phases 0–3](decisions/0014-see-baseline-corpus-and-phases-0-3.md).

### Phase 4: Enforcement

Status: partial. Source-to-rewrite preservation checks exist in the evaluation layer (`evals/grade.py`) with focused tests in `tests/test_evaluation_harness.py`; `SEE-COVERAGE-01` removed broad conformance claims. Lexical checks with existing tools, Vale scopes, document-tree checks, and a checker that emits exact rule IDs are not implemented.

Files:

- existing evaluation code where reusable;
- `simplified-engineering-english/scripts/check_see.py` only if Vale and the existing grader cannot implement a required deterministic check;
- focused checker tests only for implemented behavior.

Work:

1. Implement lexical checks with existing tools before adding code.
2. Use Vale scopes only where they match the rule's actual semantics.
3. Implement source-to-rewrite preservation checks in the evaluation layer.
4. Add document-tree checks only for cross-block artifact structure.
5. Emit exact checked rule IDs.
6. Separate deterministic failures from semantic review findings.
7. Remove broad conformance claims that no checker supports.

Check:

- each automatic rule has positive, negative, exemption, and boundary examples;
- each check reports the correct source location;
- false positives do not force technical changes;
- the checker cannot report full conformance without required semantic and technical reviews.

Exit criteria:

- all implemented checks have focused tests;
- no checker claim exceeds observed behavior;
- custom code exists only for behavior unavailable from Vale or the existing grader.

### Phase 5: Development and Holdout Evaluation

Status: steps 1–5 and 8 done for candidate V24 (development 29/42 → 42/42, holdout 24/36 → 36/36, routing 30/30 and 36/36; 156 blinded judge payloads). Step 6 (human calibration) is open; step 7 (merge gate) is `inconclusive` in `evals/results/see-improvement/release-gate-final.json`. Per-rule false-positive behavior is not reported separately.

Files:

- frozen case files;
- new immutable result directories under `evals/results/`.

Work:

1. Capture treatment runs for the accepted candidate.
2. Grade development runs.
3. Freeze the candidate before opening holdout results.
4. Capture and grade holdout runs.
5. Run blinded, position-swapped judgment for residual semantic dimensions.
6. Conduct the human calibration review.
7. Run the repository merge gate.
8. Record quality, false-positive, and cost results separately.

Exit criteria:

- zero critical regressions;
- no holdout loss on baseline-passing critical cases;
- measured ambiguity improvement;
- non-inferior technical fidelity;
- acceptable per-rule false-positive behavior;
- explained cost changes;
- a passing gate before any efficacy claim.

### Phase 6: Release and Documentation

Status: open. Production `SKILL.md` (SHA-256 `c11e5ef33c3f…`) differs from the evaluated candidate (`256976f959ac…`) after commit `8fcec98` (2026-10-06) added STE rule-number citations, `SEE-NOTE-01`, and further strict-profile controls.

Files:

- `simplified-engineering-english/SKILL.md`
- `simplified-engineering-english/references/rules.md`
- `simplified-engineering-english/references/dictionary.md`
- `README.md` only if the public skill summary or repository instructions change
- compact evaluation reports and manifests

Work:

1. Apply only the candidate supported by the gate.
2. Update source links and version dates.
3. Record checker coverage and review requirements.
4. Remove obsolete rules, examples, aliases, and duplicated guidance.
5. Validate repository contracts.
6. Publish the retained evidence required by `evals/README.md`.

Exit criteria:

- the production files match the evaluated candidate;
- no stale rule or contradictory example remains;
- the release report states supported and unsupported claims;
- rollback inputs are retained.

## 14. Release and Rollback

Status: the authoritative blocker list is the [release report](../evals/results/see-improvement/release-report.md); resolution is tracked in [skill set plan §9.1](skill-set-improvement-plan.md#91-resolve-the-existing-simplified-engineering-english-release-blockers). Missing: immutable evaluated catalog revisions and roots; frozen comparison-contract path and SHA-256; effective overall timeouts and an equality result; human calibration and adjudication of the 26-pair packet (30 position-sensitive and 6 critical-flagged pairs); a named qualified technical attestation; durable artifact storage with immutable URI, hash, access policy, retention period, and owner.

### 14.1 Release Checklist

- Baseline and treatment metadata match.
- Production content matches the evaluated candidate hash.
- Deterministic preservation checks pass.
- Development and holdout gates pass.
- Position-sensitive judge results are resolved or reported.
- Human calibration covers every artifact family.
- Critical technical-fidelity regressions are zero.
- No-op preservation passes.
- Rule sources and relationships are present.
- Checker coverage names exact rule IDs.
- Repository validation passes.
- Raw and compact evaluation evidence is retained according to repository policy.

### 14.2 Rollback Triggers

Rollback the candidate if post-release evidence finds any of these conditions:

- changed obligation force;
- changed fact, number, unit, version, condition, or exception;
- altered protected or quoted text without authorized redaction;
- invented technical content;
- unsafe error disclosure;
- strict-profile regression;
- systematic false positives that force incorrect terminology;
- routing regression that activates SEE for implementation work or bypasses SEE for consequential prose;
- production content that differs from the evaluated candidate.

### 14.3 Rollback Method

Retain: the prior skill and dictionary hashes; baseline and treatment manifests; case snapshots; deterministic grades; judge summaries; the accepted release report.

Restore the last passing skill and dictionary together. Do not keep partial compatibility aliases for removed rule IDs unless retained evaluation artifacts require them for interpretation.

## 15. Risks and Controls

| Risk | Control |
| --- | --- |
| Style compliance changes technical meaning. | Apply the preservation invariant before every other language rule and fail deterministically on critical fields. |
| A source guide is treated as universal law. | Record source scope and relationship for every rule. |
| Relaxing rules removes the value of controlled language. | Retain a strict profile and test it independently. |
| The strict profile leaks into ordinary artifacts. | Require explicit profile selection and test engineering-default counterexamples. |
| EARS is treated as complete requirements engineering. | Limit it to suitable syntax and route lifecycle governance to a companion review. |
| A checker reports semantic conformance. | Declare exact check coverage and require semantic and technical review. |
| The dictionary overrides authoritative ecosystem terminology. | Apply source and glossary precedence. |
| Error detail leaks internal information. | Separate user and operator channels and test authorized versus unauthorized paths. |
| Accessibility scope expands into implementation guidance. | Keep prose controls in SEE and route rendered-surface checks elsewhere. |
| Progressive disclosure loses a critical rule. | Compare technical fidelity and ambiguity before and after the split. |
| Evals reward fluent rewrites. | Score technical fidelity and unnecessary edits independently; deterministic failures override judges. |
| The corpus overfits known examples. | Freeze holdouts and add production-derived cases after release without rewriting historical results. |
| One model-specific result becomes a universal claim. | Pin the evaluated model and repeat evaluation for materially different models. |
| Rule metadata becomes duplicate maintenance work. | Keep one canonical record when machine-readable tooling is introduced. |

## 16. Non-goals

- Do not reproduce the ASD-STE100 dictionary.
- Do not claim official ASD or STEMG certification.
- Do not turn SEE into a complete requirements-management process.
- Do not turn SEE into an accessibility implementation standard.
- Do not govern source-code identifiers or architecture decisions.
- Do not require one house style for every software organization.
- Do not add a checker before a rule has a defined scope, severity, and acceptance case.
- Do not add every NASA, Google, Microsoft, Red Hat, IBM, W3C, or ISO recommendation to the core skill.
- Do not claim prompt-density, comprehension, translation, or reviewer benefits without paired evidence.
- Do not use holdout results to tune the candidate.
- Do not preserve deprecated compatibility paths after a clean rule cutover unless retained evidence requires interpretability.

## 17. Supporting Sources

### Controlled and Plain Language

- ASD-STE100 Issue 9: <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>
- ASD-STE100 overview: <https://www.asd-ste100.org/about_STE.html>
- ASD-STE100 tooling guidance: <https://asd-ste100.org/STEsoftware.html>
- ISO 24495-1:2023 overview: <https://www.iso.org/standard/78907.html>
- Kuhn, “A Survey and Classification of Controlled Natural Languages”: <https://aclanthology.org/J14-1005/>

### Obligation and Requirements

- RFC 2119: <https://www.rfc-editor.org/rfc/rfc2119>
- RFC 8174: <https://www.rfc-editor.org/rfc/rfc8174>
- Official EARS guide: <https://alistairmavin.com/ears/>
- Original EARS paper: <https://doi.org/10.1109/RE.2009.9>
- “Ten Years of EARS”: <https://doi.org/10.1109/MS.2019.2921164>
- NASA requirements checklist: <https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/>
- Gentili and Falessi, “Characterizing Requirements Smells”: <https://arxiv.org/abs/2404.11106>

### Documentation, Accessibility, and Errors

- Google developer documentation style guide: <https://developers.google.com/style>
- Google active-voice guidance: <https://developers.google.com/style/voice>
- Google contractions guidance: <https://developers.google.com/style/contractions>
- Google tense guidance: <https://developers.google.com/style/tense>
- Google accessibility guidance: <https://developers.google.com/style/accessibility>
- Microsoft verb guidance: <https://learn.microsoft.com/en-us/style-guide/grammar/verbs>
- Diátaxis: <https://diataxis.fr/>
- WCAG error identification: <https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html>
- WCAG error suggestion: <https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html>
- OWASP error-handling guidance: <https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html>

### Enforcement

- Vale `occurrence`: <https://docs.vale.sh/checks/occurrence>
- Vale `metric`: <https://docs.vale.sh/checks/metric>
- Vale `conditional`: <https://docs.vale.sh/checks/conditional>
- Vale vocabularies: <https://docs.vale.sh/keys/vocabularies>
- Vale scopes: <https://docs.vale.sh/topics/scopes>

## 18. Final Deliverables

The improvement project is complete only when it produces (status in brackets):

1. a frozen and retained baseline [done locally; durable storage open];
2. a rule inventory with authority, profile, severity, enforcement, and source fields [done];
3. a preservation-first `SKILL.md` [done];
4. corrected BCP 14 and EARS guidance [done];
5. strict and engineering-default profiles [done];
6. compact artifact cards [done];
7. a sourced detailed-rules reference [done];
8. a corrected, override-aware dictionary [done];
9. deterministic preservation checks [done];
10. semantic and technical review rubrics [rubric `evals/see-rubric.json` and attestation template exist; reviews open];
11. development and holdout behavior cases [done];
12. expanded routing cases [done];
13. focused checker tests for every implemented automatic rule [done for evaluation-layer checks; Phase 4 checkers open];
14. paired quality and cost results [done locally];
15. a passing release gate [open: `inconclusive`];
16. retained evidence sufficient to reproduce the decision [open];
17. a release report that states supported claims, unsupported claims, and rollback triggers [report exists; final `GO`/`NO-GO` open].
