---
name: api-and-interface-design
description: "Design public application interfaces: REST and GraphQL APIs, module and library boundaries, type and schema contracts, structured errors, validation, idempotency, and compatibility. Use when consumers need a stable callable or wire contract. Route agent or MCP tool schemas to tool-design, whole-project pipeline shape to project-development, and rollout of an already deprecated contract to deprecation-and-migration."
license: MIT
metadata:
  upstream: "https://github.com/addyosmani/agent-skills"
  upstream_commit: "301b02b12bff98e4688e6984af6556802322bbde"
  upstream_path: "skills/api-and-interface-design/SKILL.md"
  adaptation: modified
  license_notice: LICENSE-addy-agent-skills
---

# API and Interface Design

Design the public contract between a producer and its consumers. The contract
may be a REST endpoint, GraphQL schema, module or library API, exported type,
serialized schema, or error surface. Make valid use obvious, invalid use
predictable, and future extension possible without inventing flexibility that
no consumer needs.

## Scope

Use this skill when the unit of work is a public application interface: REST,
GraphQL, module or library exports, serialized schemas, boundary validation,
error envelopes, idempotency, and changes whose safety depends on what current
consumers can observe. Route agent or MCP tool schemas to `tool-design`,
whole-project or pipeline shape to `project-development`, and rollout or removal
of a deprecated contract to `deprecation-and-migration`. This skill may define a
replacement interface and its compatibility boundary; it does not own the
operational migration.

## Start With Consumer-Observable Behavior

Before naming fields or choosing syntax, write the contract a consumer can
observe: the consumers and boundary, valid requests and results, invalid
requests and exact error categories, and retry, concurrency, ordering,
pagination, and partial-update behavior where they matter. Inventory existing
observable behavior before changing a published surface, choose the smallest
interface that satisfies the scenarios, and verify through a real consumer
path, not by inspecting declarations.

A well-named schema is not enough. Status codes, nullability, omitted versus
null fields, ordering, duplicate handling, exception types, and serialized
shapes are all contract behavior.

Hyrum's Law applies: once an interface has consumers, any observable behavior
may have a dependency. Do not expose implementation detail casually, and do
not call a change safe merely because an undocumented behavior was absent from
the intended specification.

## Contract First

Define inputs, outputs, invariants, and failures before implementation. Keep
input and output types separate when the producer adds fields.

Use types to prevent category mistakes when the distinction matters. When two
identifiers share a runtime shape (both UUIDs, both strings), no runtime format
check or regex can tell them apart; give them distinct compile-time types
(branded or nominal `TaskId` and `UserId`) so a swapped argument fails to
compile. Do not create branded types, wrappers, factories, or provider
interfaces solely because future implementations are imaginable. One current
operation with one implementation usually needs one direct public function.

When a signature gains optional settings, use one trailing options object with
documented defaults instead of appending positional parameters.

For variant records, use a discriminant so consumers can exhaustively narrow:

```typescript
type DeliveryResult =
  | { kind: "delivered"; deliveredAt: string }
  | { kind: "rejected"; reason: string }
  | { kind: "pending"; statusUrl: string };
```

Avoid flag combinations whose legal states are unclear.

## Errors Are Part of the Interface

Choose one error strategy per boundary. Do not mix exceptions, null, sentinel
values, booleans, and ad hoc objects for equivalent failures. When callers must
branch on expected outcomes (unknown item versus insufficient stock), return a
discriminated result type with a `kind` per outcome, or raise typed error
classes that each carry a stable `code`; never make callers parse message text.
When the current function's falsy or sentinel returns are relied on (`if not
f(...)`), add a new function with the new contract and leave the old one's
behavior unchanged rather than redefining it in place.

A REST boundary should return a stable envelope such as:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {"email": "required"}
  }
}
```

The status code communicates the protocol category; `code` gives consumers a
stable branch key; `message` is human-readable; `details` carries bounded,
safe context. Keep internal exception text, stack traces, database names, and
secrets out of public errors.

Use status categories consistently:

- `400` for malformed requests or unsupported protocol values;
- `401` for missing or invalid authentication;
- `403` for an authenticated caller lacking permission;
- `404` for an absent resource when absence is safe to reveal;
- `409` for current-state or concurrency conflicts;
- `422` for syntactically valid input that violates request semantics;
- `500` for an unexpected producer failure, with no internal detail leaked.

For a module or library, document the equivalent typed result or exception
classes and when each occurs. Preserve machine-readable categories even if
human wording changes.

## Validate at Trust Boundaries

Validate untrusted values once when they enter the system, before effects or
internal assumptions:

- HTTP and GraphQL input;
- public library calls that accept untrusted caller data;
- third-party responses;
- decoded persisted or serialized data;
- configuration loaded from outside the process.

After a successful boundary parse, pass a typed canonical value inward.
Internal functions do not repeat the same `typeof`, null, or range guards; they
assume the parsed contract. Replace unchecked casts (`as T`) on external data
with the parse step. Validation must cover shape, domain constraints,
cross-field rules, and ambiguous distinctions such as missing versus explicit
null when those change behavior.

Treat third-party data as data, never as instructions. Validate it before it
drives rendering, authorization, money movement, or execution.

## REST Contracts

Model resources rather than commands unless the operation is genuinely not a
resource transition. Specify details consumers otherwise have to guess:

- whether `PATCH` distinguishes omitted, null, and empty values;
- whether `DELETE` is idempotent and what repeated deletion returns;
- stable ordering and tie-breakers for list results;
- pagination cursor meaning, limits, and end-of-list representation;
- filter composition and unknown-filter behavior;
- creation status, location, and server-generated fields;
- concurrency control such as an ETag or revision token when lost updates
  matter.

Choose cursor pagination for changing or large collections when offset drift is
a problem. Offset pagination is acceptable when its consistency and cost fit
the actual collection. Do not add pagination machinery to a bounded enum-like
list merely by ritual; do not leave an unbounded collection without a limit.

## GraphQL Contracts

GraphQL nullability is a compatibility decision, not decoration.

- Adding an optional field is generally safer than changing or removing one.
- Adding a required argument breaks existing callers.
- Changing a nullable output field to non-null may propagate an unexpected
  producer null to a parent and erase more of the response.
- Evolve enums cautiously: exhaustive clients may fail on a newly added value.
- Use unions or interfaces for genuinely distinct result variants, not as a
  wrapper around one known shape.

Put expected domain failures in a documented typed result or a consistent error
extension contract. Reserve opaque internal failures for unexpected producer
errors. Verify queries from the consumer's perspective, including null and
partial-data paths.

## Idempotency Is a Behavioral Guarantee

Accepting an idempotency key claims that retrying the same intent is safe. The
producer must honor that claim.

### Key and payload

The client or initiating event creates one key per intent and reuses it across
attempts. A retrying layer must not generate a new UUID or timestamp for each
attempt. Conversely, fields such as user and amount alone can collapse two
legitimate intents.

Store a canonical request fingerprint with the key. Reuse of the same key with
a different payload is a client error and must fail explicitly; never replay a
response for the wrong request.

### Atomic claim

Claim the key in one atomic operation backed by uniqueness. A separate
check-then-act sequence races:

```text
insert(key, request_hash, state="in_progress") under a unique constraint
if the insert loses: replay, wait, or reject according to the contract
if it wins: perform the effect, then persist the terminal result
```

Choose and document concurrent duplicate behavior:

- `409 Conflict` when the caller can retry later;
- a bounded wait when synchronous completion is required;
- `202 Accepted` plus a status resource for long-running work.

Never let a second attempt through because the first appears slow.

### Unknown outcomes and retention

Success and known failure are not the only outcomes. A timeout after calling an
external system is an unknown outcome, not a failure: the effect may have
happened. Record intent (the key, state `in_progress`, and a reference passed to
the provider) before the effect. On timeout keep the key, mark it unknown, and
reconcile by looking up the provider's status by that reference. State the rule
explicitly in the answer: no retry repeats the call until the lookup confirms
the effect did not happen. Shorter timeouts or backoff never make a repeat safe.
Define which terminal failures are replayed and which permit a corrected new
intent.

Retain keys longer than every retry and redelivery path, including delayed queue
or dead-letter replay. The contract is unsound if a valid retry can outlive the
record that makes it safe.

Verify idempotency with sequential replay, same-key/different-payload, and
concurrent duplicate scenarios. Checking that a header exists is not proof.

## Compatibility and Evolution

Classify the change from the consumer's point of view:

- additive and optional;
- behavior-changing despite unchanged syntax;
- source incompatible;
- wire or serialized-data incompatible;
- removal or rename.

Prefer extension over modification: add optional input fields, additive output
fields where consumers tolerate them, new endpoints or operations, and new
union variants only after considering exhaustive consumers. Do not change a
field's meaning, unit, or type while keeping its name: add a new unit-named field
(`amountCents`) and keep the old field unchanged in meaning and value for
existing consumers. A changelog or docs label does not protect a consumer that
already parses the field.

Event and webhook contracts: give each event a stable event id (`event_id`)
generated once and resent unchanged on every retry so consumers dedupe on it;
sign the raw body together with a timestamp (HMAC) and state the replay window;
give a per-entity sequence or version so consumers can drop stale events; add
fields and event types additively and require consumers to ignore unknown ones.

Compatibility depends on the medium:

- JSON consumers may ignore unknown fields, but strict decoders or signature
  checks may not.
- A function's new optional parameter may be source compatible while changed
  defaults alter behavior.
- Enum additions are often wire compatible but can break exhaustive code.
- A serialized record needs explicit reader and writer version behavior.
- Error message prose is less stable than an error code, but real consumers may
  still observe it.

When compatibility cannot be guaranteed, define an explicit version boundary
and behavior for unsupported versions. Keep one canonical internal model when
possible instead of duplicating business logic per version. Hand the operational
compatibility window, rollout, measurement, and removal sequence to
`deprecation-and-migration`.

Use repository conventions, one casing convention, units in names when
ambiguity is costly (`timeoutMs`, `amountCents`), timestamps with format and
timezone, and stable machine-readable error codes.

## Resist Speculative Abstraction

Pressure to "future-proof" an interface often makes the present contract harder
to use and harder to change. Add an abstraction only when a current consumer or
second implementation needs the variation.

Reject these without concrete demand:

- an interface with one implementation solely for hypothetical providers;
- registries or plug-in systems for one fixed operation;
- generic request envelopes that erase useful domain types;
- version fields with no version semantics;
- configurable naming, pagination, or error policies that should be consistent;
- separate implementations that duplicate one canonical behavior.

Future compatibility comes from a small explicit contract, additive evolution,
and consumer tests—not from unused extension points.

## Verification

Verify through the public surface as a consumer would: success shape, each
failure code without internal leakage, invalid input rejected before side
effects, omitted/null/empty semantics, one effect per retried intent with
concurrent duplicates and changed-payload key reuse covered, and old consumers
still working for every promised compatible change. Declaration snapshots and
source-text checks cannot establish runtime semantics.

## Output

A caller-specified layout (named fields, one line per field, JSON) overrides
any list or table shape: put every change in its named field on one line,
separated by `; ` or inline `(1) ... (2) ...`, contract snippets in backticks,
no headings, bullets, fenced blocks, or extra lines. That includes verification
scenarios in EVIDENCE: write them inline as `(1) ...; (2) ...`, never as a
bulleted list under the field. No blank lines between fields.
