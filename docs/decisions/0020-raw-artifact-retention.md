# Raw Artifact Retention

- **Status:** Accepted
- **Date:** 2026-11-21
- **Source:** owner decision after `evals/` reached 235 GB on disk (`evals/results/**/artifacts/`, 233.7 GB, Git-ignored)

## Context

Raw captures grow quadratically: each streamed `message_update` event repeats the whole partial message, and every artifact stores the stream twice (`events` and `raw_stdout`). One 59 MB artifact compresses to 59 KB with zstd. `autoresearch.sh` and pooling read only tracked `manifest.json` and `grades.jsonl`; raw artifacts are needed only to re-grade or build judge payloads, and `grade.py` refuses runs whose recorded grader hash differs from the active one.

## Decision

1. Raw artifacts are kept only for runs that the active `grade.py` can re-grade: every case file canonical with its frozen hash, and the recorded grader hash equal to the active one (`2182af327ea0…`). They are stored as `<run>/artifacts.tar.zst` (Python `tarfile`, zstd level 10), Git-ignored.
2. Raw artifacts of historical, unregistered, hash-drifted, stale-grader, and manifest-less runs were deleted (669 directories, ~192 GB). Their tracked manifests, case snapshots, grades, summaries, and gate reports remain the historical evidence for invariant 10.
3. `evals/run.py` packs `artifacts/` into `artifacts.tar.zst` after each capture. `grade.py` is unchanged so existing grader-hash pins stay valid; unpack before grading or judging (`evals/README.md`).

## Result

430 runs packed, 41.8 GB → 235 MB; `evals/` 235 GB → 542 MB. Each archive's file hashes matched the source tree before deletion. A packed run unpacked and re-graded to its stored grades (`require_grades`, 18/18).

## Limits

Deleted runs cannot be re-graded or judged. A claim that needs them needs a fresh capture.
