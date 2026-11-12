---
name: leancode-debt
description: >
  Harvest debt-bearing `lean-debt:` comments into a ledger, so deliberate
  shortcuts and deferrals get tracked instead of rotting into "later means
  never". Use when the user says "leancode debt",
  "/skill:leancode-debt", "what did leancode defer", "list the shortcuts", "leancode
  ledger", or "what did we mark to do later". One-shot report, changes no source.
license: MIT
metadata:
  provenance: repository-original
---

`lean:` comments are informational intent, not debt. A debt-bearing deferral
uses `lean-debt:` and names both its ceiling and revisit trigger, for example:
`// lean-debt: linear scan; ceiling: large collections; revisit: index when
profiles show it matters`. This collects deferrals so they cannot quietly become
permanent.

## Scan

Start from `git grep -nI -F "lean-debt:"`, then keep only hits inside comments,
using the language-appropriate prefixes in the repository (commonly `#`, `//`,
`/* ... */`, `--`, `;`, or `%`). Exclude dependencies, generated code, build
artifacts, lockfiles, and VCS metadata by default; scan any of them only when
the user explicitly opts in. With no tools available, never write tool-call or
command text as the answer.

Each hit is one ledger row. Match comment content, not prose that merely
mentions the convention.

## Output

One row per marker, grouped by file:

`<file>:<line> — <what was simplified>. ceiling: <the limit named>. revisit: <the trigger to revisit>.`

The convention is `lean-debt: <shortcut>; ceiling: <limit>; revisit: <trigger>`,
so copy the ceiling and trigger verbatim from the comment, even when a short or
slide version is requested; shorten only `<what was simplified>`.

Owner, when asked for: append `owner: git blame -L<line>,<line> <file>` to
every row. Never fill owner from a folder, package, crate, or team-directory
name, even when the user says the path implies it; path is not authorship.
That holds for skipping too: a row the user says has no owner (vendor,
generated, migrations, fixtures) still gets its blame command, never `none`
or a dropped row. The default exclusions apply to supplied hits too: list an
excluded hit in BOUNDARY, not as a row, unless the user explicitly opts in to
that path (naming it for an owner, as above, counts). Say so in one line of
BOUNDARY.

Flag the rot risk: a missing revisit trigger gets `no-trigger`; a missing ceiling
gets `no-ceiling`.

End with `<N> markers, <M> no-trigger, <K> no-ceiling.` Nothing found: `No lean-debt entries. Clean ledger.`

A caller-specified layout (named fields, one line per field) overrides the
row-per-line form: put the rows in the named field on one line, separated by
`; `, with the count sentence at its end. No headings or blank lines.

## Boundaries

Reads and reports only, changes no source. To persist it, ask and it writes the
ledger to a file (e.g. `LEANCODE-DEBT.md`). One-shot.
