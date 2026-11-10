"""Port of upstream tests/test-regression.sh (kept sections).

One test method per upstream section; every upstream assertion is a subTest.
The rubric and spec checks read the real references/regression.md.
"""
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCORE = HERE.parent / "scripts" / "score_regression.py"
FIX = HERE / "fixtures" / "regression"
SPEC = HERE.parent / "references" / "regression.md"
RUBRIC_TARGET = int(os.environ.get("REG_RUBRIC_TARGET", "32"))
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def run(*args):
    p = subprocess.run([sys.executable, str(SCORE), *args], capture_output=True, text=True, env=ENV)
    return p.stdout, p.returncode


def verdict(name):
    out, code = run("verdict", str(FIX / name))
    m = re.search(r"^VERDICT: (.*)$", out, re.M)
    s = re.search(r"^score=(.*)$", out, re.M)
    return out, code, m and m.group(1), s and s.group(1)


class RegressionTests(unittest.TestCase):
    def expect(self, name, verd=None, code=None, score=None, contains=(), label=None):
        out, got_code, got_verd, got_score = verdict(name)
        label = label or name
        for what, want, got in (("verdict", verd, got_verd), ("exit", code, got_code), ("score", score, got_score)):
            if want is not None:
                with self.subTest(f"{label} {what}"):
                    self.assertEqual(want, got)
        for pat in contains:
            with self.subTest(f"{label} contains {pat}"):
                self.assertRegex(out, pat)

    def test_classification_invariants(self):  # 21
        self.expect("green-to-red.tsv", "UNSTABLE", 1, contains=["blocking=functional"])
        self.expect("invalid-classification.tsv", "ERROR", 2, contains=["blocking=invalid-classification"])
        self.expect("invalid-tier.tsv", "ERROR", 2, contains=["blocking=invalid-schema"])
        self.expect("invalid-regressed.tsv", "ERROR", 2, contains=["blocking=invalid-schema"])
        self.expect("truncated-hard.tsv", "ERROR", 2, contains=["blocking=invalid-schema"])
        self.expect("red-to-red.tsv", "STABLE", 0)
        self.expect("absent-to-red.tsv", "STABLE", 0)
        self.expect("flake-to-red.tsv", "STABLE", 0)

    def test_score_tier(self):  # 8
        self.expect("perf-in-band.tsv", "STABLE")
        self.expect("perf-over-band.tsv", "UNSTABLE", 1, "88.00")
        self.expect("score-boundary-95.tsv", "STABLE", score="95.00")
        self.expect("score-boundary-94.tsv", "UNSTABLE", score="94.00")

    def test_dimension_availability(self):  # 6
        self.expect("unavailable-dim.tsv", "STABLE",
                    contains=["dims_unavailable=.*resource", "dims_unavailable=.*visual-ui"])
        self.expect("all-unavailable.tsv", "BASELINE_UNAVAILABLE", 2, contains=["blocking=no-dims-ran"])

    def test_empty_and_error_paths(self):  # 5
        self.expect("empty.tsv", "BASELINE_UNAVAILABLE", 2, contains=["blocking=no-dims-ran"])
        out, code = run("verdict", str(FIX / "does-not-exist.tsv"))
        with self.subTest("missing TSV => VERDICT: ERROR"):
            self.assertIn("VERDICT: ERROR", out)
        with self.subTest("missing TSV exit 2"):
            self.assertEqual(2, code)

    def test_determinism(self):  # 1
        args = ("verdict", str(FIX / "perf-over-band.tsv"))
        self.assertEqual(run(*args), run(*args))

    def test_rubric_spec_quality_gate(self):  # 1
        self.assertTrue(SPEC.is_file(), f"missing {SPEC}")
        m = re.search(r"^SCORE: (\d+)$", run("rubric", str(SPEC))[0], re.M)
        self.assertGreaterEqual(int(m.group(1)) if m else 0, RUBRIC_TARGET)

    def test_rubric_default_spec(self):  # new: default resolves next to the script
        self.assertEqual(run("rubric", str(SPEC)), run("rubric"))

    def test_spec_invariants_present(self):  # 13
        text = SPEC.read_text(encoding="utf-8")
        for label, pat in (
            ("green->red invariant", r"green.{0,3}red transition only|green.{0,3}red"),
            ("classification phase", r"classification"),
            ("baseline-unavailable state", r"baseline-unavailable|BASELINE_UNAVAILABLE"),
            ("worktree --detach", r"git worktree add --detach"),
            ("submodule init", r"submodule update --init"),
            ("migration forward-only default", r"forward-only"),
            ("perf Mann-Whitney", r"Mann.?Whitney"),
            ("perf independent-process samples", r"independent.process"),
            ("visual pixel-ratio default", r"maxDiffPixelRatio|pixel.ratio"),
            ("--max-runs ceiling", r"--max-runs"),
            ("fix-cycle bound", r"fix-cycles|3 cycles"),
            ("verdict field", r"verdict.*STABLE|STABLE.*UNSTABLE"),
            ("handoff status enum (inline or via contracts)", r"COMPLETE.*CONVERGED.*SATURATED|family enum|common enum"),
        ):
            with self.subTest(label):
                self.assertRegex(text, re.compile(pat, re.I))


if __name__ == "__main__":
    unittest.main()
