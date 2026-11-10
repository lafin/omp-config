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

# Plateaued rounds before verdict gives up (fork-and-flush schedules two per run).
FORK_ROUNDS_BEFORE_PLATEAU = 2

W = r"(?<![a-z0-9_])"  # keyword starts a word: "prefix" is not "fix", "address" is not "add"
_BUILD = rf"{W}((re)?(build|implement)|add(s|ed|ing)?(?![a-z0-9_]))"
CLASSIFY_ORDER = (  # higher-stakes archetypes first: "fix and add" -> fix-broken
    ("harden", rf"{W}(secure|insecure|harden|vuln)"),
    ("fix-broken", rf"{W}(fix|bug|broken|hotfix|bugfix)|^\s*debug"),
    ("fix-broken", rf"^(?!.*{_BUILD})(?=.*{W}debug)"),  # debug with no build verb is a bug hunt
    ("ship-ready", rf"{W}(re)?(ship|release|deploy)"),
    # needs a "what ..." question so "build the next-gen parser" stays build-feature
    ("what-to-build", rf"{W}(what.*build|what.*next)"),
    ("build-feature", _BUILD),
    ("optimize-metric", rf"{W}(faster|smaller|reduce|optimize|coverage)"),
    ("document", rf"{W}(document|docs)"),
    ("decide-design", rf"{W}(should we|decide|approach)"),
)

_INTERP = r"(sh|bash|zsh|dash|fish|ksh|python[0-9.]*|perl|ruby|node|php)"
_XINTERP = r"(sh|bash|zsh|dash|ksh|python[0-9.]*|perl|ruby|node|php)"
_BLOCKDEV = r"(sd|hd|vd|nvme|disk|mapper|loop|xvd|mmcblk|md|dm-)"
_END = r"([\s;&|()<>]|$)"
_LAUNCHERS = {"sudo", "doas", "env", "exec", "command", "builtin", "nohup", "time", "nice", "ionice",
              "timeout", "xargs", "stdbuf", "chrt", "taskset", "eval"}


def _cmd_re(name):  # command name after any shell separator, optionally path-qualified
    return rf"(^|[\s;&|(){{`\\$<>])([^\s;&|(){{`<>]*/)?{name}{_END}"


# (patterns that must ALL match somewhere in the command) -> refuse. Read from the
# shell's view of the command (quotes, backslashes, $IFS and brace lists removed).
REFUSE_RULES = (
    (_cmd_re("rm"), r"(^|\s)-[a-zA-Z]*[rR]|(^|\s)--r(e(c(u(r(s(i(ve?)?)?)?)?)?)?)?([^\w-]|$)",
     r"(^|\s)-[a-zA-Z]*[fF]|(^|\s)--f(o(r(ce?)?)?)?([^\w-]|$)"),
    (rf"(curl|wget)[^|]*\|\s*([^\s]*/)?{_INTERP}{_END}",),
    (rf"(curl|wget)[^|]*\|\s*(sudo|doas|env|exec|command|nohup|time)(\s+[^\s|]+)*\s+([^\s]*/)?{_INTERP}{_END}",),
    (rf"({_INTERP}|source|\.)\s+(<\s*)?<\(\s*(curl|wget)",),
    (rf"(curl|wget)[^|]*\|.*xargs.*\s([^\s]*/)?{_XINTERP}{_END}",),
    (rf"\|\s*([^\s]*/)?(nc|ncat|netcat){_END}",),
    (rf"(of=|>\s*)/dev/{_BLOCKDEV}",),
    (r"(^|[\s;&|(){`\\$<>])([^\s;&|(){`<>]*/)?(mkfs|mke2fs)",),
    (_cmd_re("find"), rf"\s-delete{_END}"),
    (_cmd_re("shred"),),
    (_cmd_re("truncate"), rf"(-s\s*0|--size\s*=?\s*0){_END}"),
    (_cmd_re("chmod"), rf"(-R|--recursive){_END}", rf"(^|\s)(000|00|0){_END}"),
    (rf"(^|[\s;&|(){{`<>])([^\s;&|(){{`<>]*/)?env(\s+[^\s;&|()<>]+)*\s+(-[a-zA-Z]*S|--split-string)",),
)
SECRET_RULES = (r":\(\)\{", r"AKIA[0-9A-Z]{16}", r"PASSWORD\s*=", r"BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY")
RULES = tuple(tuple(re.compile(p, re.M) for p in rule) for rule in REFUSE_RULES)
NESTED = re.compile(r"(^|[\s;&|(){`<>])([^\s;&|(){`<>]*/)?(eval|sh|bash|zsh|dash|ksh|fish|source|su)"
                    rf"{_END}|(^|[;&|(){{`])\s*\.\s", re.M)
PG = r"postgres(?:ql)?://"


def classify(goal):
    g = goal.lower()
    for label, pat in CLASSIFY_ORDER:
        if re.search(pat, g, re.S):
            return label
    return "explore"


def _scan(cmd):
    """Read quotes the way bash does. Returns (live, unquoted, quoted parts): `live` keeps
    double-quoted text (expansions still run there), `unquoted` keeps only bare text."""
    q, live, bare, part, parts, i = "", [], [], [], [], 0
    while i < len(cmd):
        c = cmd[i]
        if q == "'":
            if c == "'":
                q = ""; live.append(c); bare.append(c); parts.append("".join(part)); part = []
            else:
                part.append(c)
        elif c == "\\":
            live.append("_")
            if q:
                part.append(cmd[i:i + 2])
            else:
                bare.append("_")
            i += 1
        elif q == '"':
            live.append(c)
            if c == '"':
                q = ""; bare.append(c); parts.append("".join(part)); part = []
            else:
                part.append(c)
        else:
            if c == "$" and cmd[i + 1:i + 2] == '"':
                live.append("`")  # $"..." is a string bash may translate: refuse like a backtick
            if c in "'\"":
                q = c
            live.append(c); bare.append(c)
        i += 1
    parts.append("".join(part))
    return "".join(live), "".join(bare), parts


def _glob_command_name(unquoted):
    """A glob as a command name (r?, /bin/r[m], sudo r*) can run any program."""
    for line in unquoted.split("\n"):
        line = re.sub(r"[0-9]*[<>]+[&|]?\s*[^\s;&|(){}<>]*", " ", line)  # drop redirect targets
        for seg in re.split(r"[;&|(){}<>]", line):
            launched = False
            for x in seg.split():
                if re.match(r"[A-Za-z_][A-Za-z0-9_]*=|-|[0-9]+$", x) or x in (
                        "if", "then", "else", "elif", "do", "while", "until", "!"):
                    continue
                if re.sub(r"^\S*/", "", x) in _LAUNCHERS:
                    launched = True  # an option value may precede the name: check every later word
                    continue
                if x in ("[", "[["):
                    break
                if re.search(r"[*?[]", x):
                    return True
                if not launched:
                    break
    return False


def _pg_ok(cmd, bare):
    """Every postgres URL must be local, a container name, or a _test/_ci database."""
    if len(re.findall(PG, bare)) != len(re.findall(PG, cmd)):
        return False  # quotes or backslashes inside the scheme hide a URL
    if not re.search(PG, cmd):
        return True
    if (re.search(PG + r"[^\s;|<>()]*[%,#\\]", cmd)  # encoded text, multi-host, fragment, backslash
            or re.search(PG + r"[^\s;|<>()]*[?&](host|hostaddr|dbname|service)=", cmd, re.I)
            or re.search(PG + r"""([\s;&|<>()"'`]|$)""", cmd)  # no host: PGHOST or -h decides
            or re.search(r"""["']""" + PG + r"""[^"']*\s""", cmd)  # quoted URL with a space
            or re.search(PG + r"""[^\s;&|<>()]*["'`][^\s;&|<>()"'`]""", cmd)):  # quote inside the URL
        return False
    # Each URL read twice: cut at punctuation, and with user:pass kept whole.
    urls = [m.group(0) for p in (r"""[^\s;&|<>()"'`]+""", r"""([^\s/@]*@)?[^\s;&|<>()"'`]+""")
            for m in re.finditer(PG + p, cmd)]
    for url in urls:
        rest = url.split("://", 1)[1]
        authority = rest.split("/", 1)[0]
        if authority.count("@") > 1 or re.search(r"[?#].*@", authority):
            return False
        host = authority.rsplit("@", 1)[-1]
        path = "" if "?" in host else rest[len(authority):]
        host = re.split(r"[:?]", host)[0]
        name = path.split("?")[0].removeprefix("/")
        if re.search(r"[$\{\}*\[~]", name):
            return False
        # Numbers (2130706433, 0x7f000001) and IPv6 are remote addresses, not container names.
        local = host in ("localhost", "127.0.0.1") or re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", host)
        if not local and not re.search(r"_test$|_ci$", name):
            return False
    return True


def screen(cmd):
    """True = ok, False = refuse. Refuses whole kinds it cannot read: control bytes,
    line continuations, expansions that can build a name, globbed command names."""
    if re.search(r"[\x00-\x08\x0b-\x1f\x7f]", cmd) or "\\\n" in cmd:
        return False
    bare = re.sub(r"[{},]", " ", re.sub(r"\$\{IFS\}|\$IFS", " ", re.sub(r"[\"'\\]", "", cmd)))
    live, unquoted, parts = _scan(cmd)
    if (re.search(r"`|\$[^\"\s]", live) or re.search(r"\{[^\s{}]*(,|\.\.)[^\s{}]*\}", unquoted)
            or _glob_command_name(unquoted)):
        return False
    if NESTED.search(bare):  # a nested shell or eval runs each quoted part as a new command
        if "\\$" in cmd or "\\`" in cmd or not all(screen(p) for p in parts if p.strip()):
            return False
    if any(all(r.search(bare) for r in rule) for rule in RULES):
        return False
    if any(re.search(p, cmd) for p in SECRET_RULES):
        return False
    return _pg_ok(cmd, bare)


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
        if not isinstance(units, list) or not all(u == "unknown" or (_isnum(u) and u >= 0) for u in units):
            return None  # a malformed history is BLOCKED, never silently filtered
        return [None if u == "unknown" else float(u) for u in units]
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
    if s.get("ceiling") is True:  # checked first: fork rounds never extend a reached ceiling
        print("CEILING\nship=no")
        return 1
    if s.get("plateau") is True:
        forks = s.get("fork_rounds_since_progress", 0)
        forks = int(forks) if isinstance(forks, str) and forks.isdigit() else forks
        word = "FORK" if _isint(forks) and forks < FORK_ROUNDS_BEFORE_PLATEAU else "PLATEAU"
        print(f"{word}\nship=no")
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
