# SEE Preservation-First Revision Specification

- **Status:** Completed (implemented; release decision `INCONCLUSIVE`)
- **Date:** not stated (implemented in commit `50cf61c`, 2026-09-12)
- **Source:** [Simplified Engineering English Improvement Plan §2 and §6–§10](../simplified-engineering-english-improvement-plan.md#2-decision-summary)

## Decision

Use a preservation-first revision rather than adding more rules. The specification below is implemented in `SKILL.md`, `references/rules.md`, and `references/dictionary.md`. The evaluated candidate passed the V24 automated gate, but the release decision is `INCONCLUSIVE`; release and rollback work stays in the plan (§13 Phases 4–6, §14).

### §2 Target design

One explicit technical-preservation invariant; one rule-precedence order; a small set of rules that apply to every supported artifact; a strict controlled-language profile for safety, regulatory, maintenance, and translation-sensitive work; an engineering-default profile for ordinary software documentation; compact artifact cards for procedures, requirements, explanations and references, errors, incidents, and diagnostic records; rule-level source and adaptation labels; enforcement claims limited to the checks that actually run; paired baseline and treatment evaluations with separate technical-fidelity, ambiguity, actionability, readability, and compliance results.

### §6 Target skill structure

**6.1 `SKILL.md`** focuses on execution: (1) scope and non-scope; (2) audience and artifact identification; (3) technical-preservation invariant; (4) rule precedence; (5) base-profile selection; (6) artifact-card selection; (7) rewrite workflow; (8) ambiguity and conflict handling; (9) verification and reporting; (10) links to detailed rules and dictionary guidance.

**6.2 Detailed rules.** Create `references/rules.md` only after the baseline is frozen. Move detailed grammar, procedure, requirement, risk, time, and evidence rules into it. Organize by the decision an agent must make, not by source-standard numbering alone: preserve meaning; choose terminology; identify actors, actions, conditions, and results; select obligation force; structure the artifact; state risk and recovery; scope time, version, and evidence; verify the result. Retain source mappings so a reviewer can trace each rule to ASD-STE100, BCP 14, EARS, ISO, another guide, or an SEE-specific decision.

**6.3 Dictionary** in three groups: (1) cross-domain distinctions with material engineering consequences; (2) default software terms that authoritative ecosystem or project terminology can override; (3) project glossary governance and checker integration. The project glossary overrides an SEE default when the project term is authoritative and unambiguous. A language, protocol, or platform specification overrides both.

**6.4 Base profiles.**

- *Strict controlled* — use for safety-critical procedures; regulated documentation; aircraft or equipment maintenance material; translation-sensitive source text; projects that explicitly require STE-like constraints. Candidate controls: maximum 20 words for procedural sentences; maximum 25 words for descriptive sentences; restricted voice and tense; no contractions; controlled multi-word nouns; controlled word counting; stricter approved vocabulary. These controls are hard requirements only when this profile is selected.
- *Engineering-default* — use for design documents, ADRs, PR descriptions, issues, ordinary developer documentation, code comments, and explanatory API documentation. Keeps semantic safeguards as errors. Treats voice, tense, sentence length, contractions, and similar style signals as warnings or project choices.

**6.5 Artifact cards** — compact cards rather than one independent rule system per artifact.

- *Procedure and runbook* — require prerequisites; imperative steps; one consequential action per step; condition before action when acting early can cause an error; observable result when success is not self-evident; rollback or irreversibility information for state-changing, destructive, costly, security-sensitive, or availability-affecting work; risk information before the governed action. Do not require rollback text for read-only or diagnostic procedures.
- *Requirement and contract* — require declared obligation profile; one independently verifiable obligation per statement; explicit subject and response; conditions, thresholds, tolerances, units, and timing where applicable; an objective verification method; rationale outside the normative statement; a handoff to requirements governance for traceability, completeness, feasibility, assumptions, and unresolved values. Use EARS when its temporal clauses fit the intended behavior. Do not force EARS onto every constraint, interface rule, or quality attribute.
- *Explanation and reference* — require the reader's need and scope near the start; information in dependency order; stable terminology; a clear distinction between behavior, rationale, recommendation, and implementation detail; document- or section-level version scope; meaningful headings and links. Use the Diátaxis user need to distinguish tutorial, how-to, reference, and explanation content. Do not infer sentence caps from Diátaxis.
- *Error, incident, and diagnostic record* — require what failed or what was observed; a safe cause when the cause is known and suitable for the audience; a recovery action when one exists; the affected input or resource when disclosure is safe; separate user-facing and operator-facing detail; observation, report, inference, assumption, and unknown markers where evidence provenance matters; separation of timeline facts from causal hypotheses.

### §7 Correctness changes

**7.1 Technical preservation.** Add near the start of `SKILL.md`:

> A rewrite MUST preserve facts, conditions, qualifiers, numbers, units, versions, identifiers, commands, quotations, obligation force, uncertainty, and supported causal claims. If the source is ambiguous, identify the ambiguity instead of selecting an interpretation.

Add deterministic preservation fields to evaluation cases before changing any production text.

**7.2 BCP 14.** BCP 14 applies when the artifact declares RFC 2119 and RFC 8174 semantics. Only uppercase forms have the special BCP 14 meanings. Lowercase forms retain normal English meaning. Normative text does not require a BCP 14 keyword merely because RFC 8174 exists. `NOT RECOMMENDED` belongs to the declared keyword set. `SHOULD` and `SHOULD NOT` permit justified deviation after the implications are understood and weighed. A sentence does not need an exhaustive exception condition to use `SHOULD` correctly. Exactly one keyword per atomic normative statement is an SEE policy, not an RFC requirement. Each requirements or protocol project chooses one preferred absolute keyword; do not switch between `MUST` and `SHALL` for stylistic variety.

**7.3 EARS.** Zero or more preconditions; zero or one trigger; one system name; one or more system responses; complex forms can include unwanted-behavior `If` and `Then` clauses; an optional feature is "included" unless the requirement intentionally describes runtime enablement. If SEE retains one response per requirement, label that restriction as an atomicity policy layered on EARS.

**7.4 Verification.** Replace "name the test that would fail" with objective verification: test, demonstration, inspection, analysis. A requirement must provide or support measurable pass/fail evidence. Naming a test is neither necessary nor sufficient.

**7.5 Risk and error messages.** Separate (1) the consequence and avoidance structure, (2) the project's severity taxonomy, (3) information disclosure for the intended audience. Invariant: (1) place risk information before the governed action; (2) state the consequence; (3) state the prevention or recovery action; (4) state the affected scope when consequential. Permit project-specific labels. Identify the WARNING, CAUTION, and NOTE model as an SEE software adaptation rather than an official STE severity mapping. For errors: include an actionable local path when the user can inspect it safely; exclude server paths, stack traces, dependency details, secrets, and internal queries from unauthorized responses; log diagnostic detail in an authorized operator channel; provide a correction only when it is known and does not compromise security or the content's purpose.

**7.6 Time, version, and evidence.** Declare the applicable product and version at document or section level; qualify an individual claim only when its version differs from the surrounding scope; prohibit floating time references when they can become stale; permit ordinary time words when they describe an immediate procedure or observation unambiguously; permit future tense for a genuinely delayed or asynchronous result; continue to prohibit presenting an unshipped plan as current behavior. Require evidence markers primarily in incidents, debugging records, investigations, research, and agent handoffs; not for every non-obvious sentence in a tutorial, ADR, or API reference. A deprecation record should state the deprecated item; the deprecation version; the replacement; the planned removal version, or an explicit statement that no removal version is scheduled; an owner or tracking reference when removal remains unresolved.

**7.7 Revision and release scope.** Replace "same commit" with "same reviewed change set or coordinated release"; some projects store code and documentation in separate repositories or publish them through separate pipelines. Do not call every terminology change breaking. Classify by consumer effect: editorial-only; search or discoverability impact; user-interface terminology change; API or schema change; migration-requiring breaking change.

### §8 Language policy

**8.1 Hard rule, warning, or house style**

| Topic | Strict profile | Engineering-default profile |
| --- | --- | --- |
| Technical fact preservation | Error | Error |
| Protected-span preservation | Error | Error |
| Project terminology | Error | Error |
| Obligation-force preservation | Error | Error |
| Ambiguous consequential actor | Error | Error |
| Sentence cap | Error | Warning |
| Passive voice | Restricted | Warning when responsibility becomes unclear |
| Perfect or progressive tense | Restricted | Warning only when sequence or state becomes unclear |
| Contractions | Prohibited | Project or artifact choice |
| American English | Project choice | Project choice |
| Semicolon | Prohibited | Suggestion unless accessibility or parsing requires stricter treatment |
| Three-word multi-word noun | Error with declared exceptions | Warning |
| Evidence markers | Artifact-specific | Artifact-specific |

**8.2 Voice.** Use active voice when the actor or responsible party matters. Permit passive voice when the actor is unknown, irrelevant, or intentionally omitted for a valid reason, or the affected object is the relevant subject. Do not invent an actor to eliminate passive voice.

**8.3 Sentence length.** Retain the ASD-STE100 20-word procedural and 25-word descriptive limits in the strict profile. In engineering-default: flag a long sentence for review; split it only when the split preserves logical relationships; do not trade a precise condition, exception, or qualifier for a lower word count. Document the counting algorithm. The protected-span convention is an SEE adaptation and requires custom tokenization if it remains part of conformance.

**8.4 Contractions** (profile split to evaluate): strict or normative text — no contractions; conversational documentation and user-interface text — common contractions permitted; unusual or ambiguous contractions — prohibited.

**8.5 Tense and aspect.** Prefer simple present for general behavior. Permit simple past for completed events; future tense for actual delayed or asynchronous outcomes; perfect or progressive constructions when they preserve a material state or temporal relationship that a simple tense would lose. Continue to reject dangling participles and unclear event ordering.

### §9 Dictionary

**9.1 Keep material distinctions** where conflation can change engineering meaning: authentication and authorization; parameter and argument; fault, error, and failure; concurrency, parallelism, and asynchrony; deprecated and removed; release, deploy, rollout, rollback, and revert. Add verb forms such as `authenticate` and `authorize` when the main rules use them.

**9.2 Make context-dependent terms overridable** — mark as defaults rather than universal senses: module, package, library, framework, service, component, repository, API, endpoint, route, latency, response time, capacity, cache, record, entity, and similar. Remove false absolutes: a mean latency is a measurement claim, although it can be insufficient for a tail-latency decision. Require the statistic, workload, sample, interval, and measurement point that the decision needs.

**9.3 Glossary contract** fields: `term`, `definition`, `part_of_speech`, `domain`, `source`, `approved_variants`, `rejected_alternatives`, `replacement` when deprecated, `status`, `owner`, `since`. Do not claim that a Vale vocabulary enforces the definition or part of speech. Compile only accepted spellings, casing, and rejected alternatives into Vale data.

**9.4 Exemption precedence:** (1) authorized security redaction can replace sensitive text; (2) quoted external text remains verbatim unless the task requests a quotation edit; (3) tool output and logs remain verbatim, with secrets redacted when authorized; (4) code spans remain verbatim; (5) product and protocol names remain verbatim; (6) surrounding prose remains subject to the selected profile. An exemption from rewriting does not make the exempt content technically correct or safe to publish.

### §10 Accessibility and internationalization

Prose-facing controls inside SEE: descriptive headings; meaningful link text; text equivalents for meaningful images and diagrams; no meaning conveyed only by color, position, punctuation, or a symbol; simple tables with an introduced purpose; references to UI elements by accessible label rather than visual location; errors identified in text; declared document language where the format supports it; no idioms or locale-dependent examples in translation-sensitive content.

Route to a companion accessibility or localization review: keyboard behavior; focus management; ARIA relationships; screen-reader runtime testing; right-to-left layout; text expansion; locale-sensitive formatting code; translatable-string concatenation.

Use the ISO 24495-1 outcomes as the top-level document check: relevant, findable, understandable, usable.

### Post-evaluation drift

Commit `8fcec98` (2026-10-06) changed `SKILL.md` and `references/rules.md` after the V24 evaluation: strict-profile STE Rule 3.2 verb forms, no auxiliary-verb constructions (Rule 3.4), no `-ing` verb forms (Rule 3.5), no phrasal verbs, a six-sentence paragraph limit, `SEE-NOTE-01`, and STE rule-number source citations. Production `SKILL.md` SHA-256 is now `c11e5ef33c3f5a6d18f064ad557c4d57c71036d10645eec442a9132356311747`; the evaluated candidate is `256976f959ac379e0080835f7b6f5201908b722dbab4384d0e32cc12e31e20a8`. The plan tracks this under §13 Phase 6 and §14.

## Evidence

- [skills/simplified-engineering-english/SKILL.md](../../skills/simplified-engineering-english/SKILL.md) — Preservation Invariant, Precedence, Select a Profile, Select an Artifact Card
- [skills/simplified-engineering-english/references/rules.md](../../skills/simplified-engineering-english/references/rules.md) — `SEE-BCP14-01`, `SEE-BCP14-02`, `SEE-EARS-01`, `SEE-VERIFY-01`, `SEE-DISCLOSE-01`, `SEE-DEPREC-01`, `SEE-ACCESS-01`, `SEE-SENT-01`, Strict Word Count
- [skills/simplified-engineering-english/references/dictionary.md](../../skills/simplified-engineering-english/references/dictionary.md) — Material Cross-Domain Distinctions, Override-Aware Software Defaults, Project Glossary Contract, Exemption and Redaction Precedence
- [evals/results/see-improvement/release-report.md](../../evals/results/see-improvement/release-report.md)
