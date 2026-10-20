// autoresearch guard — while a loop run is active, block irreversible shell
// commands and keep run state alive across compaction.
//
// Active means the file `autoresearch/.active` exists under the project root;
// its single line is the run directory (e.g. `autoresearch/fix-261020-1405`).
// The skill's setup writes it after the baseline; completion and abort delete it.
//
// Blocked while active (bash `command`, eval `code`): `git push` in any form,
// `git reset --hard`, `git clean` with a force flag, and `rm` with recursive+force
// flags in any arrangement. `bash` input is parsed (quotes, `&&`/`;`/`|`, `git -C dir`,
// `sh -c '...'`). `eval` code is matched best-effort as flattened text: any `git`/`rm`
// token followed by the same arguments blocks, so a string literal mentioning
// `git push` can false-positive and dynamically built commands can slip through.
// The hook only blocks, never allows; it overlaps harmlessly with `bash.gitGuard`.

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { basename, join, resolve } from "node:path";

import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

const MARKER = join("autoresearch", ".active");
const TSV_ROWS = 10;
const STATE_CHARS = 4000;
const SHELLS: Record<string, true> = { sh: true, bash: true, zsh: true, dash: true, ksh: true };
// Words that precede the real command without changing what it does.
const PREFIXES: Record<string, true> = {
  sudo: true, env: true, command: true, exec: true, time: true, nohup: true, nice: true, builtin: true,
  "!": true, "{": true, do: true, then: true, else: true, if: true, while: true,
};
// git global options that consume the next token as their value.
const GIT_VALUE_OPTS: Record<string, true> = {
  "-C": true, "-c": true, "--git-dir": true, "--work-tree": true, "--namespace": true,
  "--exec-path": true, "--super-prefix": true, "--config-env": true,
};

// Splits shell text into command segments of unquoted words. `flatten` (eval code)
// also treats quotes, brackets, and commas as whitespace so `["git", "push"]` yields `git push`.
function segments(text: string, flatten: boolean): string[][] {
  const out: string[][] = [];
  let words: string[] = [];
  let word = "";
  let quote = "";
  let has = false;
  const endWord = () => {
    if (has) words.push(word);
    word = "";
    has = false;
  };
  const endSegment = () => {
    endWord();
    if (words.length) out.push(words);
    words = [];
  };
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quote) {
      if (c === quote) quote = "";
      else if (c === "\\" && quote === '"' && i + 1 < text.length) word += text[++i];
      else word += c;
      continue;
    }
    if (flatten && /["'`\[\],!]/.test(c)) endWord();
    else if (c === "'" || c === '"') {
      quote = c;
      has = true;
    } else if (c === "\\" && i + 1 < text.length) {
      word += text[++i];
      has = true;
    } else if (/\s/.test(c) && c !== "\n") endWord();
    else if (c === "\n" || c === ";" || c === "&" || c === "|" || (!flatten && /[()`]/.test(c))) endSegment();
    else {
      word += c;
      has = true;
    }
  }
  endSegment();
  return out;
}

function hasShortFlag(args: string[], letters: string): boolean {
  return args.some(a => new RegExp(`^-(?!-)[a-zA-Z]*[${letters}]`).test(a));
}

// Returns a description when `args` (the words after `cmd`) form a blocked command.
function blockedCommand(cmd: string, args: string[]): string | undefined {
  if (cmd === "rm") {
    const flags = args.slice(0, args.indexOf("--") < 0 ? undefined : args.indexOf("--"));
    const recursive = hasShortFlag(flags, "rR") || flags.includes("--recursive");
    const force = hasShortFlag(flags, "f") || flags.includes("--force");
    return recursive && force ? "recursive forced rm" : undefined;
  }
  if (cmd !== "git") return undefined;
  let i = 0;
  while (i < args.length && args[i].startsWith("-")) i += Object.hasOwn(GIT_VALUE_OPTS, args[i]) ? 2 : 1;
  const rest = args.slice(i + 1);
  switch (args[i]) {
    case "push":
      return "git push";
    case "reset":
      return rest.includes("--hard") ? "git reset --hard" : undefined;
    case "clean":
      return hasShortFlag(rest, "f") || rest.includes("--force") ? "forced git clean" : undefined;
  }
  return undefined;
}

function findBlocked(text: string, flatten: boolean): string | undefined {
  for (const words of segments(text, flatten)) {
    for (let i = 0; i < words.length; i++) {
      const cmd = basename(words[i]);
      if (!flatten && Object.hasOwn(PREFIXES, cmd)) continue;
      if (!flatten && /^[A-Za-z_][A-Za-z0-9_]*=/.test(words[i])) continue;
      const hit = blockedCommand(cmd, words.slice(i + 1));
      if (hit) return hit;
      if (!flatten && Object.hasOwn(SHELLS, cmd)) {
        const c = words.findIndex((w, j) => j > i && /^-[a-zA-Z]*c$/.test(w));
        const nested = c < 0 ? undefined : findBlocked(words[c + 1] ?? "", false);
        if (nested) return nested;
      }
      if (!flatten) break; // bash: only the head word is a command
    }
  }
  return undefined;
}

function readText(path: string): string | undefined {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return undefined;
  }
}

function activeRun(cwd: string): string | undefined {
  const marker = join(cwd, MARKER);
  if (!existsSync(marker)) return undefined;
  return readText(marker)?.split("\n")[0].trim() || "";
}

function summary(runDir: string, runPath: string): string {
  const parts = [`Autoresearch run ${runPath} is active (marker ${MARKER}).`];
  for (const name of ["handoff.json", "orchestrator-state.json"]) {
    const text = readText(join(runDir, name));
    if (text) parts.push(`${name}:\n${text.length > STATE_CHARS ? `${text.slice(0, STATE_CHARS)}\n…(truncated)` : text}`);
  }
  return parts.join("\n\n");
}

function tsvTail(runDir: string): string | undefined {
  let file: string | undefined;
  try {
    file = readdirSync(runDir).filter(f => f.endsWith("-results.tsv")).sort().pop();
  } catch {
    return undefined;
  }
  const lines = file ? readText(join(runDir, file))?.split("\n").filter(l => l.trim() && !l.startsWith("#")) : undefined;
  if (!file || !lines?.length) return undefined;
  return `${file} (header + last ${TSV_ROWS} rows):\n${[lines[0], ...lines.slice(1).slice(-TSV_ROWS)].join("\n")}`;
}

export default function autoresearch(pi: ExtensionAPI): void {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash" && event.toolName !== "eval") return;
    const run = activeRun(ctx.cwd);
    if (run === undefined) return;
    const input = event.input as Record<string, unknown>;
    const isBash = event.toolName === "bash";
    const hit = findBlocked(String(input[isBash ? "command" : "code"] ?? ""), !isBash);
    if (!hit) return;
    return {
      block: true,
      reason: `Autoresearch run ${run || "(unnamed)"} is active; ${hit} is blocked during loops. Revert with \`git revert HEAD --no-edit\` instead, and never push. If the run crashed and the marker is stale, delete ${join(ctx.cwd, MARKER)} (plain \`rm\` of that file is allowed).`,
    };
  });

  pi.on("session.compacting", async (_event, ctx) => {
    const run = activeRun(ctx.cwd);
    if (run === undefined) return;
    const runDir = resolve(ctx.cwd, run);
    const context = [summary(runDir, run || "(unnamed)"), tsvTail(runDir)].filter((s): s is string => !!s);
    return { context };
  });
}
