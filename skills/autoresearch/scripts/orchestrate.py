#!/usr/bin/env python3
"""Deterministic seam for the autoresearch orchestrator loop (stdlib only).

Status: Production helper

Ported from upstream orchestrate.sh. Every subcommand is pure and CI-usable via
exit codes. Usage errors exit 64.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

CLASSIFY_ORDER = (  # higher-stakes archetypes first: "fix and add" -> fix-broken
    ("harden", r"(secure|harden|vuln)"),
    ("fix-broken", r"(fix|bug|broken)"),
    ("ship-ready", r"(ship|release|deploy)"),
    # needs a "what ..." question so "build the next-gen parser" stays build-feature
    ("what-to-build", r"(what.*build|what.*next)"),
    ("build-feature", r"(build|implement|add)"),
    ("optimize-metric", r"(faster|smaller|reduce|optimize|coverage)"),
    ("document", r"(document|docs)"),
    ("decide-design", r"(should we|decide|approach)"),
)

_INTERP = r"(sh|bash|zsh|dash|fish|ksh|python[0-9.]*|perl|ruby|node|php)"
_XINTERP = r"(sh|bash|zsh|dash|ksh|python[0-9.]*|perl|ruby|node|php)"
_BLOCKDEV = r"(sd|hd|vd|nvme|disk|mapper|loop|xvd|mmcblk|md|dm-)"


def _cmd_re(name):
    return rf"(^|\s)([^\s]*/)?{name}(\s|$)"


# (patterns that must ALL match somewhere in the command) -> refuse
REFUSE_RULES = (
    (_cmd_re("rm"), r"(^|\s)-[a-zA-Z]*[rR]|--recursive", r"(^|\s)-[a-zA-Z]*[fF]|--force"),
    (rf"(curl|wget)[^|]*\|\s*([^\s]*/)?{_INTERP}(\s|$)",),
    (rf"(curl|wget)[^|]*\|.*xargs.*\s([^\s]*/)?{_XINTERP}(\s|$)",),
    (r"\|\s*([^\s]*/)?(nc|ncat|netcat)(\s|$)",),
    (rf"(of=|>\s*)/dev/{_BLOCKDEV}",),
    (r"(^|\s)([^\s]*/)?(mkfs|mke2fs)",),
    (_cmd_re("find"), r"\s-delete(\s|$)"),
    (_cmd_re("shred"),),
    (_cmd_re("truncate"), r"(-s\s*0|--size\s*=?\s*0)(\s|$)"),
    (_cmd_re("chmod"), r"(-R|--recursive)(\s|$)", r"(^|\s)(000|00|0)(\s|$)"),
    (r":\(\)\{",),
    (r"AKIA[0-9A-Z]{16}",),
    (r"PASSWORD\s*=",),
    (r"BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY",),
)
RULES = tuple(tuple(re.compile(p, re.M) for p in rule) for rule in REFUSE_RULES)
PG_URL = re.compile(r"postgres(?:ql)?://\S+")
PG_HOST = re.compile(r"postgres(?:ql)?://(?:[^@/]+@)?([^/:]+)[:/]")
PG_NAME = re.compile(r"postgres(?:ql)?://[^/]*/([^?\s]+)")


def classify(goal):
    g = goal.lower()
    for label, pat in CLASSIFY_ORDER:
        if re.search(pat, g):
            return label
    return "explore"


def screen(cmd):
    """True = ok, False = refuse."""
    if any(all(r.search(cmd) for r in rule) for rule in RULES):
        return False
    # Anchored DB allowlist: localhost, 127.0.0.1, dotless host, or _test/_ci dbname suffix.
    for m in PG_URL.finditer(cmd):
        url = m.group(0)
        hm = PG_HOST.match(url)
        host = hm.group(1) if hm else url
        if host in ("localhost", "127.0.0.1") or "." not in host:
            continue
        nm = PG_NAME.match(url)
        name = nm.group(1) if nm else url
        if not re.search(r"_test$|_ci$", name):
            return False
    return True


def _load(path):
    """Parsed JSON or None when unreadable/malformed."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _isint(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _err(msg):
    print(msg, file=sys.stderr)


def cmd_classify(a):
    print(classify(a.goal))
    return 0


def cmd_next_hop(a):
    if not Path(a.state).is_file():
        _err("ERROR: missing state file")
        return 2
    s = _load(a.state)
    if not isinstance(s, dict):
        _err("ERROR: malformed state file")
        return 2
    errors, regression, gaps = s.get("errors_remaining"), s.get("regression_verdict"), s.get("untested_gaps")
    if not (_isint(errors) and errors >= 0 and isinstance(regression, str) and regression
            and _isint(gaps) and gaps >= 0):
        _err("ERROR: malformed state file")
        return 2
    if errors > 0:
        hop = "fix"
    elif regression == "UNSTABLE":
        hop = "regression"
    elif gaps > 0:
        hop = "debug"
    elif s.get("pending_verify") is True:
        hop = "verify"  # independent acceptance check precedes DONE/ship
    elif s.get("archetype") == "ship-ready":
        hop = "ship"
    else:
        hop = "DONE"
    print(hop)
    return 0


def cmd_units(a):
    r = _load(a.results) if Path(a.results).is_file() else None
    keys = ("failing_tests", "open_hard_regressions", "metric_delta", "metric_target")
    vals = [r.get(k) for k in keys] if isinstance(r, dict) else []
    if len(vals) != 4 or not all(_isnum(v) and v >= 0 for v in vals) or vals[3] == 0:
        print("unknown")
        return 2
    ft, reg, delta, target = vals
    val = ft + reg + delta / target
    print(int(val) if val == int(val) else f"{val:g}")
    return 0


def _plateau_tokens(path):
    """List of floats / None (unknown) from a state JSON or a newline history file; None if unusable."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    try:
        state = json.loads(text)
    except ValueError:
        state = None
    if isinstance(state, dict):
        units = state.get("units_remaining")
        if not isinstance(units, list):
            return None
        return [None if u == "unknown" else float(u) for u in units if u == "unknown" or _isnum(u)]
    toks = []
    for line in text.splitlines():
        line = line.strip()
        if line == "unknown":
            toks.append(None)
        else:
            m = re.match(r"\d+(?:\.\d*)?(?:[eE][+-]?\d+)?", line)
            if m:
                toks.append(float(m.group(0)))
    return toks


def cmd_plateau(a):
    toks = _plateau_tokens(a.source) if Path(a.source).is_file() else None
    n = a.window
    vals, trailing = [], 0
    for t in toks or ():
        if t is None:
            trailing += 1
        else:
            vals.append(t)
            trailing = 0
    # A runner stuck emitting "unknown" must not read as progress.
    if toks is None or trailing >= n or not vals:
        print("BLOCKED")
        return 3
    if len(vals) < n or vals[-1] < vals[-n]:  # too short, or net improvement over the window
        return 1
    print("PLATEAU")
    return 0


def cmd_screen_cmd(a):
    ok = screen(a.command)
    print("ok" if ok else "refuse")
    return 0 if ok else 1


def cmd_verdict(a):
    s = _load(a.state) if Path(a.state).is_file() else None
    units = None
    if isinstance(s, dict) and isinstance(s.get("units_remaining"), list):
        nums = [u for u in s["units_remaining"] if _isnum(u)]
        units = nums[-1] if nums else None
    if units is None:
        print("BLOCKED\nship=no")
        return 2
    if s.get("plateau") is True:
        print("PLATEAU\nship=no")
        return 1
    if s.get("ceiling") is True:
        print("CEILING\nship=no")
        return 1
    if units == 0:
        print("CONVERGED\nship=yes")
        return 0
    print("BLOCKED\nship=no")
    return 1


def _valid_state(s):
    if not isinstance(s, dict):
        return False
    if not all(isinstance(s.get(k), str) and s[k] for k in ("goal", "archetype", "predicate", "terminal_choice")):
        return False
    if not _isint(s.get("cycle")) or s["cycle"] < 0:
        return False
    units = s.get("units_remaining")
    if not isinstance(units, list) or not all(_isnum(u) or u == "unknown" for u in units):
        return False
    return isinstance(s.get("pipeline_log"), list)


def cmd_validate_state(a):
    ok = Path(a.state).is_file() and _valid_state(_load(a.state))
    print("valid" if ok else "invalid")
    return 0 if ok else 2


def cmd_screen_state_predicate(a):
    s = _load(a.state) if Path(a.state).is_file() else None
    pred = s.get("predicate") if isinstance(s, dict) else None
    if not isinstance(pred, str) or not pred or "\0" in pred:
        print("invalid")
        return 2
    return cmd_screen_cmd(argparse.Namespace(command=pred))


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        _err(f"{self.prog}: error: {message}")
        sys.exit(64)


def _window(v):
    n = int(v)
    if n < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return n


def build_parser():
    p = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="SUBCOMMAND")
    for name, fn, arg, doc in (
        ("classify", cmd_classify, "goal", "goal string -> archetype label"),
        ("next-hop", cmd_next_hop, "state", "state.json -> fix|regression|debug|verify|ship|DONE (exit 2 on bad state)"),
        ("units", cmd_units, "results", "results.json -> Units-remaining scalar, or 'unknown' exit 2"),
        ("plateau", cmd_plateau, "source", "state.json (units_remaining) or newline history file; exit 0 PLATEAU, 1 improving, 3 BLOCKED"),
        ("screen-cmd", cmd_screen_cmd, "command", "shell string -> ok exit 0 | refuse exit 1"),
        ("verdict", cmd_verdict, "state", "state.json -> CONVERGED|PLATEAU|CEILING|BLOCKED + ship=yes|no"),
        ("validate-state", cmd_validate_state, "state", "state.json schema gate -> valid exit 0 | invalid exit 2"),
        ("screen-state-predicate", cmd_screen_state_predicate, "state", "re-screen the pinned predicate in state.json"),
    ):
        sp = sub.add_parser(name, help=doc, description=doc)
        sp.add_argument(arg)
        if name == "plateau":
            sp.add_argument("--window", type=_window, default=5, help="trailing computed values compared (default 5)")
        sp.set_defaults(func=fn)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
