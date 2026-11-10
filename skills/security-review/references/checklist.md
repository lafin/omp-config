# Application Security Checklist

Provenance: adapted (modified) from `https://github.com/affaan-m/ECC` at commit
`4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2`, path
`skills/security-review/SKILL.md`, MIT License; see `LICENSE-ecc`. Vendor- and
framework-specific examples (Supabase, Next.js, Solana, npm) were removed;
checks are stated per sink.

Read this when a review needs per-area checks. Each item names the unsafe form
and the safe primitive.

## Secrets

- No credentials, tokens, or keys in source, tests, fixtures, or history; read
  them from the environment or a secret store and fail fast when missing.
- Secret files are ignored by version control.
- A leaked secret is rotated; deleting it from the latest commit is not enough.

## Input to sinks

| Sink | Unsafe | Safe |
|---|---|---|
| SQL | string concatenation or formatting with request data | driver placeholders with a parameter array; ORM query builders without raw fragments |
| Shell | `shell=True`, `exec(string)` with request data | argument arrays; no shell; allowlisted commands |
| File path | joining a request value onto a base directory | resolve, then verify the result is inside the base; allowlist file names |
| HTML | inserting user HTML or unescaped values | framework auto-escaping; a maintained sanitizer with a tag allowlist for rich text |
| Outbound URL (SSRF) | fetching a request-supplied URL | allowlist hosts; block private, loopback, and metadata addresses after DNS resolution |
| Deserializer | `pickle`, `yaml.load`, Java/PHP native deserialization of untrusted bytes | JSON or `yaml.safe_load` into a validated schema |
| Upload | trusting client file name and MIME type | size limit, content sniffing, server-generated names, storage outside the web root |

Validate at the boundary with an allowlist schema (type, length, range,
format). Error messages to clients carry no internal detail.

## Authentication

- Passwords hashed with a slow adaptive function (argon2, bcrypt, scrypt).
- Session tokens in `HttpOnly; Secure; SameSite` cookies, not script-readable
  storage; rotated on login and privilege change.
- Reset and verification tokens: single-use, short-lived, compared in constant
  time.
- Login, reset, and signup are rate-limited per account and per source.

## Authorization

- Every operation on an object checks that the caller owns or may act on that
  object or tenant, using an ID from the session, not only from the request.
- Role checks happen on the server for each operation, not only in the UI or
  route list.
- List and search endpoints filter by tenant before pagination.

## Cross-site request forgery

- State-changing requests authenticated by cookies require a CSRF token or a
  `SameSite=Strict`/`Lax` session cookie plus an origin check.

## Sensitive data

- Logs and analytics omit passwords, tokens, full card numbers, CVV, and
  secrets; personal data is minimized.
- Stack traces and internal errors stay server-side.
- Responses return only the fields the caller may see.

## Money and irreversible actions

- Amounts, currency, and recipient are computed or verified on the server.
- Requests are idempotent by key; retries cannot double-charge.
- Balance checks and debits happen atomically.

## Abuse limits

- Rate limits on authentication and on endpoints whose cost grows with input.
- Request body, upload, and page-size limits.

## Dependencies

- Lockfiles are committed and used in CI.
- Known-vulnerable versions are reported by the ecosystem's audit tool; record
  the command run and its output instead of claiming a clean result.

## Regression checks

For each fixed finding, add one test that sends the exploit input and expects
rejection: unauthenticated → 401, other tenant's object → 403 or 404, injection
payload → treated as data, over-limit requests → 429.
