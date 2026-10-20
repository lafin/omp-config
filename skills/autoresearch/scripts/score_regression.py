#!/usr/bin/env python3
"""Scoring backend for `/autoresearch regression` (stdlib only).

Status: Production helper

  rubric [file]         grep-rubric quality score of regression.md -> "SCORE: N"
  verdict <results.tsv> tiered stability verdict from a results TSV

verdict: any HARD green->red row (classification regression-eligible, regressed=true)
-> UNSTABLE; else weighted per-dimension worst subscore (weights renormalized over
dims that ran) must reach the threshold. Classifications pre-existing, new-coverage,
baseline-unavailable, flaky never gate. Exit 0 STABLE, 1 UNSTABLE, 2 ERROR/no data.
Score math goes to stderr. Overridable env: REG_THRESHOLD, REG_W_FLAKINESS,
REG_W_PERFORMANCE, REG_W_RESOURCE, REG_W_VISUAL.
"""
import argparse
import math
import os
import re
import sys
from pathlib import Path

DEFAULT_SPEC = Path(__file__).resolve().parent.parent / "references" / "regression.md"

RUBRIC = (
    "classification", "green.{0,3}red", "regression.eligible|[^a-z]eligible", "pre-existing",
    "new-coverage", "baseline.unavailable|BASELINE_UNAVAILABLE", "functional", "api-contract",
    "data-migration", "integration-e2e", "flakiness", "performance", "resource", "visual",
    "HARD", "SCORE", "worktree", "--detach|detach", "submodule", "baseline.cache|--baseline-cache",
    "--select", "findRelatedTests|nx affected|affected", "Mann.?Whitney", "independent.process",
    "effect.size|median delta", "SSIM|maxDiffPixelRatio|pixel.ratio", "samples", "noise-band",
    "forward-only", "allowlist", "fix-cycle|--fix-cycles", "probe", "auto-skip", "--max-runs",
    "handoff", "verdict", "STABLE", "UNSTABLE",
)

DIMS = ("functional", "api-contract", "data-migration", "integration-e2e",
        "flakiness", "performance", "resource", "visual-ui")
HARD_DIMS = DIMS[:4]
CLASSES = ("regression-eligible", "pre-existing", "new-coverage", "baseline-unavailable", "flaky")
SUBSCORE = re.compile(r"([0-9]+(\.[0-9]+)?|\.[0-9]+)")
NCOLS = 15


def rubric(path):
    p = Path(path) if path else DEFAULT_SPEC
    if not p.is_file():
        print("SCORE: 0")
        return 0
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    n = sum(1 for pat in RUBRIC if any(re.search(pat, ln, re.I) for ln in lines))
    print(f"SCORE: {n}")
    return 0


def _error(blocking, score="0.00"):
    print(f"VERDICT: ERROR\nscore={score}\nblocking={blocking}")
    return 2


def verdict(path):
    if not Path(path).is_file():
        return _error("missing-tsv", "0.0")
    weights = {
        "flakiness": os.environ.get("REG_W_FLAKINESS", "0.30"),
        "performance": os.environ.get("REG_W_PERFORMANCE", "0.30"),
        "resource": os.environ.get("REG_W_RESOURCE", "0.20"),
        "visual-ui": os.environ.get("REG_W_VISUAL", "0.20"),
    }
    thr_s = os.environ.get("REG_THRESHOLD", "95")
    thr = float(thr_s)

    invalid_schema = bad_class = False
    nrows, present, hardset, dmin = 0, set(), set(), {}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        f = line.split("\t")
        if line.startswith("#") or f[0] == "iteration":
            continue
        if len(f) != NCOLS:
            invalid_schema = True
            continue
        dim, tier, cls, regressed, raw = f[2], f[4], f[5], f[9], f[10]
        expected = "HARD" if dim in HARD_DIMS else "SCORE"
        if (dim not in DIMS or tier != expected or regressed not in ("true", "false")
                or not SUBSCORE.fullmatch(raw) or float(raw) > 100):
            invalid_schema = True
            continue
        if cls not in CLASSES:
            bad_class = True
            continue
        subv = float(raw)
        if cls != "baseline-unavailable":
            nrows += 1
            present.add(dim)
        if tier == "HARD" and regressed == "true" and cls == "regression-eligible":
            hardset.add(dim)
        if tier == "SCORE" and cls != "baseline-unavailable":
            dmin[dim] = min(subv, dmin.get(dim, subv))  # per-dim worst case

    if invalid_schema:
        return _error("invalid-schema")
    if bad_class:
        return _error("invalid-classification")
    if nrows == 0:  # nothing measurable ran: advisory, never a green ship signal
        print("VERDICT: BASELINE_UNAVAILABLE\nscore=0.00\nblocking=no-dims-ran\ndims_ran=none\n"
              f"dims_unavailable={','.join(DIMS)}")
        return 2

    hb = [d for d in DIMS if d in hardset]
    num = den = 0.0
    for d in DIMS:
        w = float(weights.get(d, 0))
        if d in dmin and w > 0:
            num += w * dmin[d]
            den += w
    score = num / den if den > 0 else 100.0
    unstable = bool(hb) or score < thr
    blocking = ",".join(hb + (["score"] if score < thr else [])) or "none"
    # Floor to 2 decimals: a true 94.9999 must not display as 95.00 while UNSTABLE.
    disp = math.floor(score * 100) / 100
    ran = [d for d in DIMS if d in present]
    unavail = [d for d in DIMS if d not in present]

    print(f"VERDICT: {'UNSTABLE' if unstable else 'STABLE'}\nscore={disp:.2f}\nblocking={blocking}\n"
          f"dims_ran={','.join(ran) or 'none'}\ndims_unavailable={','.join(unavail) or 'none'}")
    for d in DIMS:
        if d in dmin:
            print(f"  {d:<12} subscore={math.floor(dmin[d] * 100) / 100:.2f} weight={weights.get(d, '0')}",
                  file=sys.stderr)
    print(f"  stability_score={disp:.2f} threshold={thr_s}", file=sys.stderr)
    return 1 if unstable else 0


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        sys.exit(64)


def main(argv=None):
    p = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="{rubric,verdict}")
    r = sub.add_parser("rubric", help="grep-rubric score of the regression spec")
    r.add_argument("file", nargs="?", help="default: ../references/regression.md next to this script")
    v = sub.add_parser("verdict", help="STABLE|UNSTABLE verdict from a results TSV")
    v.add_argument("tsv")
    a = p.parse_args(argv)
    return rubric(a.file) if a.cmd == "rubric" else verdict(a.tsv)


if __name__ == "__main__":
    sys.exit(main())
