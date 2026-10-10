---
name: security-review
description: >
  Use when writing or reviewing application code at a trust boundary:
  authentication, authorization, user input reaching queries, commands, files,
  templates, or deserializers, secrets and sensitive data in logs or errors,
  payments, uploads, and abuse limits on endpoints. Returns evidence-backed
  findings with exploit path and fix. Route agent prompt-injection, tool
  permissions, and sandbox boundaries to hosted-agents, harness-engineering, or
  tool-design, and multi-topic repository review loops to /review-and-fix.
license: MIT
metadata:
  upstream: "https://github.com/affaan-m/ECC"
  upstream_commit: "4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2"
  upstream_path: "skills/security-review/SKILL.md"
  adaptation: modified
  license_notice: LICENSE-ecc
---

# Security Review

Find and fix exploitable defects where untrusted data or an untrusted caller
crosses into a privileged operation. A finding is a reachable exploit path, not
a missing best practice.

## Scope

Use for application code that handles:

- identity: login, sessions, tokens, password reset, MFA;
- authorization: ownership checks, roles, tenant isolation, object IDs from the
  request;
- untrusted input reaching SQL, shell, file paths, templates, HTML, URLs fetched
  by the server, or deserializers;
- secrets and sensitive data: credentials, tokens, card data, personal data in
  code, logs, errors, or responses;
- money and irreversible actions: payments, refunds, transfers, deletion;
- abuse: authentication and expensive endpoints without rate or size limits.

Route elsewhere:

- prompt injection, agent tool authority, sandbox and credential boundaries of
  an agent system: `hosted-agents`, `harness-engineering`, or `tool-design`;
- a multi-topic review of a whole diff or repository with fix iterations:
  `/review-and-fix` with the `security-reviewer` agent;
- choosing or upgrading a dependency version: `source-driven-development`.

## Procedure

1. **Map trust boundaries.** List each entry point in scope (HTTP handler, job,
   CLI, message consumer) and the privileged operations it reaches. Name the
   caller's identity source and the data the caller controls.
2. **Trace untrusted data to sinks.** For each controlled value, follow it to
   queries, commands, paths, templates, outbound requests, deserializers, and
   logs. Note every validation, encoding, or parameterization on the way.
3. **Check authorization at the operation, not the route.** Confirm the code
   verifies that this caller may act on this object or tenant. A logged-in
   check is not an ownership check.
4. **Check secrets and sensitive output.** Hard-coded credentials, secrets or
   card data in logs, stack traces or internal errors returned to clients.
5. **Check abuse limits** on login, reset, signup, search, upload, and any
   endpoint whose cost grows with input.
6. **Report only reachable defects.** For each, give the exact location, the
   attacker-controlled input, the exploit path, the impact, why existing guards
   do not stop it, and the smallest fix. If a guard upstream prevents the
   exploit, it is not a finding.
7. **Fix with the platform's safe primitive**: parameterized queries, argument
   arrays instead of shell strings, allowlists, framework authorization hooks,
   safe serializers, existing rate limiters. Add a regression check that fails
   on the exploit input.

Load [the checklist](references/checklist.md) for per-area checks and safe
patterns. Load [cloud and infrastructure checks](references/cloud-infrastructure.md)
only when the change touches IAM, network exposure, CI/CD secrets, storage
buckets, or backups.

## Severity

- `HIGH`: reachable by an unauthenticated or low-privilege caller and causes
  data exposure, account or tenant takeover, code execution, or money loss.
- `MEDIUM`: reachable with a precondition (authenticated, specific config) or
  bounded impact.
- `LOW`: hardening with no demonstrated exploit path.

## Failure Modes

- **Checklist dumping:** listing every OWASP category instead of tracing this
  code. Report only what the code shows.
- **Manufactured findings:** reporting a sink that an upstream guard already
  protects. Read the callers and guards first.
- **Authentication as authorization:** accepting "requires login" for an
  object the caller does not own.
- **Escaping at the wrong layer:** HTML-escaping SQL input or validating after
  use. Fix at the sink with its own primitive.
- **Denylist validation:** filtering `../` or `<script>` instead of allowlisting
  or using the safe API.
- **Unverified claims:** stating that a fix is safe or a scanner is clean
  without running it.

## Output

Per finding: `SEVERITY`, location, input, exploit path, impact, why guards
fail, fix, regression check. When nothing in scope is exploitable, say so and
list the boundaries checked. An empty finding list is a valid result.
