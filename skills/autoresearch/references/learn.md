# learn: scout codebase, generate docs or wiki

Scout the codebase and generate documentation, or a navigable wiki knowledge base, then run a validation-fix loop. Default 10 iterations. Shared blocks: `skill://autoresearch/references/contracts.md`.

## Arguments

- `Mode:` or `--mode` — `init` (create from scratch), `update` (refresh existing), `check` (validate), `summarize` (brief overview), `wiki` (navigable knowledge base).
- `Scope:` or `--scope` — file globs to document.
- `Depth:` or `--depth` — overview, standard, comprehensive.
- `--file <path>` — specific file to document.
- `--scan` — force a fresh codebase scout.
- `--topics` — comma-separated focus topics.
- `--modules <list>` — wiki mode: module names or paths overriding auto-detection.
- `--force` — wiki mode: regenerate all pages, ignore the existing manifest.
- `--no-fix` — validate only; do not auto-fix issues.
- `--format` — markdown (default), json, rst.
- `Iterations:` or `--iterations` — default 10, or `unlimited`.
- `--evals`, `--evals-interval N`, `--chain`, `--<subcommand>`.

## Setup (if Mode or Scope is missing)

Ask the user once, batching:

1. Mode: init (generate docs), update (refresh), check (validate), summarize (overview), wiki (knowledge base).
2. Scope: which files? Suggested globs plus the entire codebase.
3. Depth: overview only, standard, comprehensive.
4. Topics: architecture, API, database, testing, all.

If all are provided, skip setup.

## Baseline

1. Scout the codebase: file tree, imports and exports, existing docs.
2. Identify documentation gaps (undocumented files, outdated docs, missing READMEs).
3. Create `autoresearch/learn-<YYMMDD>-<HHMM>/`; write the active marker (contracts).
4. TSV: `# metric_direction: higher_is_better`, then the common columns plus `timestamp`, `file_documented`, `validation_status`, `issues_found`, `issues_fixed`. `metric` = files with valid documentation (higher is better); `status` is `pass` or `fail`.

## Summarize mode (no loop)

One shot: scan the codebase, produce a structured summary, write `summary.md` to the run directory. Skip the iteration loop.

## Wiki mode (no per-file loop)

Reuse the scout and analysis output, then generate a navigable `wiki/` knowledge base. Skip the init, update, and check loop. Metric = `pages_generated / pages_planned × 100` (from the manifest); size target 300 lines per page.

### Module discovery (priority order)

1. `--modules` flag (explicit override, always wins; every path must resolve inside the project root, reject escapes).
2. Monorepo workspaces (`workspaces` in `package.json`, Cargo workspace members, `pnpm-workspace.yaml`).
3. Per-directory project files (`pyproject.toml`, `Cargo.toml`, `go.mod`, `*.csproj`).
4. Heuristic: directories with 3 or more source files (code extensions only: .ts .py .go .rs .java .rb .swift .kt .c .cpp .cs; tests count, config and markdown do not); nested directories roll up to the nearest module ancestor.

Cap at 10 modules. If more than 10, group by top-level directory; if a group has more than 5 sub-modules, expand it and take the 10 largest by file count.

### Plan (write-ahead)

1. `mkdir -p wiki/modules/`; append `wiki-manifest.json` to `.gitignore` if absent.
2. Write `wiki-manifest.json` BEFORE generating: `{version:"1", generated_at, generation_status:"in_progress", modules_detected:[…], pages_planned:N, pages:{ "wiki/architecture.md":{status:"pending",type:"architecture"}, "wiki/modules/<name>.md":{…"module"}, "wiki/glossary.md":{…}, "wiki/onboarding.md":{…}, "wiki/index.md":{…} }}`.
3. Write a stub `wiki/index.md` listing every planned page as `[pending]` (navigation survives interruption).
4. Resume: if a valid manifest exists, `--force` deletes it and regenerates all; otherwise skip `generated` pages and do only `pending` ones. A corrupted manifest (invalid JSON, or missing `version` or `pages`) without `--force` is an error directing the user to `--force`.

### Generate (priority-first, one generation per page, bounded context)

1. `architecture.md` — system overview from scout context. Up to 5 Mermaid diagrams of 3 types only (`graph TD`, `sequenceDiagram`, `classDiagram`); include one canonical example of each in the prompt; pick by signal.
2. Module pages (alphabetical) — each module's generation gets: (a) the file listing, (b) the first 50 lines of up to 10 key files (entry points, then largest, then alphabetical), (c) the architecture overview. Required sections: Overview, Key Files; optional: Patterns, API, Dependencies, Getting Started.
3. `glossary.md` — domain terms from class names, exports, types, comments; filter language keywords and stdlib; soft cap about 60-80; prioritize terms found in 3 or more files.
4. `onboarding.md` — reading order, environment setup, first-contribution workflow, gotchas. Sources: directory structure, README and docs, manifests, entry-point sampling, `git log --since='6 months ago'` directory frequency (skip with a note if not a git repo or if it takes over 10 seconds).
5. `index.md` — final pass: replace the stub with real page descriptions and a reading order.

### Per-page contract

- `generated_by: autoresearch` in the YAML frontmatter.
- About 300 lines per page (soft); Mermaid diagrams of at most 15 nodes; forward-only cross-links, at most 10 per page.

### Safety

- **Secrets (two layers):** (1) the generation prompt instructs "summarize config, never include verbatim values from .env or credentials or strings matching key, secret, token, password; extract env var *names*, not *values*"; (2) after generation, run `grep -rlE '(AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|password\s*[:=]\s*\S+|mongodb(\+srv)?://\S+|postgres(ql)?://\S+)' wiki/` and warn (non-blocking) in the report.
- **Name collision:** before overwriting a page, check for `generated_by: autoresearch` frontmatter; if absent (user-created), skip with a warning. `--force` overrides.

### Finish wiki

After each page is written, flip its manifest entry `pending` → `generated` (interrupt-safe). When all are done, set `generation_status:"complete"`. Then run the iteration loop's Validate phase with the doc path swapped from `docs/` to `wiki/` (`ls wiki/*.md wiki/modules/*.md 2>/dev/null`), maximum 300 lines. Print `✓ Wiki: [N] modules, [M] pages generated`.

## Iteration loop (init, update, check modes)

1. **Scout.** Scan for documentation gaps. Prioritize: no docs, outdated docs, incomplete docs. If no gaps remain, stop early (SUCCESS).
2. **Generate or update.** Pick the highest-priority gap; write or update documentation for ONE file or module, following project conventions for doc format and location.
3. **Validate.** Check generated docs against the code: descriptions accurate, examples valid, links working. Run doc linters if available. Record `validation_status` (pass or fail) and issues found.
4. **Fix** (unless `--no-fix`). If validation finds issues, fix the doc. Commit the clean doc: `docs: document {file/module}`.
5. **Log.** Append the TSV row.
6. **Eval checkpoint.** Stats line `Docs written: {n} | Validation: {pass}/{total} | Gaps remaining: {m}`; early-stop recommendation after 3 or more checkpoints with no new docs.
7. **Bounded check.** At the bound, exit the loop.

## Output

- `learn-results.tsv`
- `summary.md` — documentation overview.
- `validation-report.md` — issues found and fixed.

## Summary

Print: files documented, validation pass rate, issues found and fixed, remaining gaps.

## Finish

Write `handoff.json`: `source: "learn"`, `findings` = documentation gaps remaining, `config` = mode, scope, depth. Delete the active marker, then follow `--chain` (contracts).
