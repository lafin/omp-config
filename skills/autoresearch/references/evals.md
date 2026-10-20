# evals: analyze iteration results

Analyze a results TSV: trends, plateaus, regressions, recommendations. Read-only analysis; no loop, no active marker. The checkpoint protocol that looping commands embed (`--evals`) is defined in `skill://autoresearch/references/contracts.md`; this file defines the analysis both the checkpoint and this command use.

## Arguments

- Positional path to a specific results TSV.
- `--format` — `text` (default, console), `json`, `md` (markdown file).
- `--compare <path>` — placeholder, not implemented.

## Input discovery

1. If a path is given, use that TSV directly.
2. Otherwise scan the current directory and `autoresearch/*/` for `*-results.tsv` files.
3. If several are found, ask the user which to analyze (list the files).
4. If none are found, ask for a path.
5. Also scan the project root for legacy TSV files (older layout without `timestamp`).

## Parse the TSV

1. Read line 1: extract the `# metric_direction: higher_is_better|lower_is_better` comment. If missing, infer from column names (`metric`, `error_count`) or ask the user.
2. Read the header row and detect the available columns.
3. Read the data rows. Handle a missing `timestamp` column gracefully (legacy files).

## Column detection and analysis

Activate analysis based on the columns present in the header:

| Column | Analysis |
|---|---|
| `metric` | Trend direction, plateau detection (3+ flat iterations), diminishing returns, biggest single-iteration jumps |
| `delta` | Per-iteration efficiency, cumulative improvement, effort-to-gain ratio |
| `status` | Keep and discard rate, crash frequency, success streaks, failure clusters, longest winning streak |
| `guard` and `guard_metric` | Guard failure rate, metric-improved-but-guard-failed analysis |
| `severity` | Severity distribution (critical, high, medium, low, info), critical discovery rate per iteration |
| `hypothesis` and `status` | Confirmation rate, investigation efficiency, most productive techniques |
| `commit` | File hotspot analysis (cross-reference `git diff` for kept commits), change size correlation |
| `technique` | Technique effectiveness ranking |
| `dimension` | Dimension coverage completeness (X/12) |
| `candidate_label` and `judge_verdict` | Convergence speed, oscillation count |
| `error_type` | Error category distribution, fix rate per category |
| `classification` | New versus extension versus duplicate ratio, saturation curve |
| `convergence_count` | Convergence trajectory |

Unknown columns: report their presence but skip analysis (forward compatible with new subcommands). Accept fuzzy column names (`metric_value`, `error_count` → `metric`; `guard-metric` → `guard_metric`). Status values from any family in the contracts are valid, plus legacy `baseline`, `keep`, `keep (reworked)`, `discard`, `crash`, `no-op`, `hook-blocked`, `metric-error`.

## Report structure

```
## Evals Summary — {subcommand} ({N} iterations)

### Key Metrics
- Total iterations: N | Kept: X | Reverted: Y | Revert rate: Z%
- Starting metric: A | Final metric: B | Improvement: C%

### Trend Analysis
- Metric progression: [description of trajectory]
- Plateau detected at iteration N (metric stable for M iterations)
- Biggest win: iteration X (+delta, description)
- Biggest loss: iteration Y (-delta, description)
- Diminishing returns: [after iteration N, average delta dropped below threshold]

### Patterns
- What types of changes succeeded: [extracted from descriptions of kept iterations]
- What types of changes failed: [extracted from descriptions of discarded iterations]
- File hotspots: [files changed most in kept iterations, if commit data available]
- Technique effectiveness: [ranked by confirmation rate, if technique column present]

### Recommendation
- [continue / stop / change strategy — based on trend, plateau, revert rate]
- [specific actionable suggestion based on pattern analysis]
```

## Output

- Console: structured report (30-50 lines).
- `--format md`: write `evals-summary.md` in the same directory as the input TSV.
- `--format json`: write `evals-summary.json` with the structured data.
