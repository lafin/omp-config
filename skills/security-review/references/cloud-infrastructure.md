# Cloud and Infrastructure Checks

Provenance: adapted (modified) from `https://github.com/affaan-m/ECC` at commit
`4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2`, path
`skills/security-review/cloud-infrastructure-security.md`, MIT License; see
`LICENSE-ecc`. Provider CLI commands and vendor product names were reduced to
provider-neutral checks.

Read this only when the change touches IAM, network exposure, CI/CD
credentials, storage buckets, databases, or backups.

## Identity and access

- Policies grant named actions on named resources; no `*` action or resource
  without a recorded reason.
- Workloads use roles or workload identity, not long-lived access keys.
- CI/CD authenticates with short-lived federated credentials (OIDC), and job
  tokens default to read-only.
- Root or owner accounts are unused for operations and protected by MFA.

## Secrets

- Secrets live in a secret manager with access logging; rotation is defined for
  database and API credentials.
- No secrets in infrastructure code, container images, build logs, or plan
  output.

## Network exposure

- Databases, caches, and admin interfaces are not publicly reachable.
- Inbound rules allow only required ports from required sources; SSH/RDP only
  through a bastion or VPN.
- Instance metadata endpoints require session tokens where the provider
  supports them (SSRF defense).

## Storage

- Buckets are private by default; public access is blocked at the account
  level unless a reviewed exception exists.
- Encryption at rest and TLS in transit are enabled.

## Pipeline and supply chain

- Third-party actions or images are pinned by digest or commit.
- Secret scanning and dependency audit run in CI; record the command and its
  output instead of claiming a clean result.
- Protected branches require review before deploy.

## Logging and recovery

- Authentication failures and administrative actions are logged without
  secrets; retention meets the stated requirement.
- Backups are automated, deletion-protected, and restored in a test at a
  defined interval; recovery point and time objectives are stated.

## Reporting

An infrastructure finding names the resource, the exposure (who can reach or
assume what), the evidence (file and line or observed configuration), and the
narrowest change that removes it.
