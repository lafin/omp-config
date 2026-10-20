// dir-context — loads per-directory AGENTS[.local].md for the path being edited.
//
// Ships in the omp-config package (repo root listed under `extensions:`).
// Disable per profile with `disabledExtensions: [extension-module:dir-context]`.

import { execFile, execFileSync } from "node:child_process";
import { existsSync, readFileSync, realpathSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, extname, isAbsolute, join, resolve, sep } from "node:path";
import { promisify } from "node:util";

import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";

// One context file per directory: first hit wins, so AGENTS.local.md supersedes
// both committed forms and AGENTS.md is preferred over CLAUDE.md when both exist.
const NAMES = ["AGENTS.local.md", "AGENTS.md", "CLAUDE.md"];
const WRITE_TOOLS: Record<string, true> = {
  edit: true,
  write: true,
  apply_patch: true,
  notebook_edit: true,
  ast_edit: true,
};
// Reads get context passively, so reviews see the rules without blocking the read.
const READ_TOOLS: Record<string, true> = { read: true, grep: true, glob: true };
// Tools that can write files without naming them; their writes are detected after the fact.
const SHELL_TOOLS: Record<string, true> = { bash: true, eval: true };
// `[path/to/file.ts#A1B2]` section headers used by the hashline edit format.
const HASHLINE = /^\[([^\]\n]+?)#[0-9A-Fa-f]{4}\]\s*$/gm;

const run = promisify(execFile);

function targetPaths(input: Record<string, unknown>): string[] {
  const out: string[] = [];
  for (const key of ["path", "file_path", "filePath"]) {
    const v = input[key];
    if (typeof v === "string") out.push(v);
  }
  if (Array.isArray(input.paths)) {
    for (const v of input.paths) if (typeof v === "string") out.push(v);
  }
  if (typeof input.input === "string") {
    for (const m of input.input.matchAll(HASHLINE)) out.push(m[1]);
  }
  // `write xd://ast_edit` carries its targets inside the JSON content.
  if (typeof input.path === "string" && input.path.startsWith("xd://ast_edit") && typeof input.content === "string") {
    try {
      const { paths } = JSON.parse(input.content) as { paths?: unknown };
      if (Array.isArray(paths)) for (const v of paths) if (typeof v === "string") out.push(v);
    } catch {
      // Malformed device args fail in the device itself with a better message.
    }
  }
  // grep/glob take `;`-joined lists and globs; read takes `:range` and `?query` selectors.
  return out
    .filter((p) => !p.includes("://"))
    .flatMap((p) => p.split(";"))
    .map((p) =>
      p
        .trim()
        .split(/[*?[{]/)[0]
        .replace(/:[^/]*$/, "")
        .replace(/^~(?=\/|$)/, homedir()),
    );
}

// Tool args may be non-canonical; both sides must be canonical or the ancestor
// comparison in chainFor silently fails.
function canonical(path: string): string {
  try {
    return realpathSync(path);
  } catch {
    return path;
  }
}

// Nearest-first context chain, bounded by the harness workspace or partition root.
function chainFor(file: string, cwd: string, root: string): string[] {
  const abs = isAbsolute(file) ? file : resolve(cwd, file);
  const found: string[] = [];
  let dir = canonical(existsSync(abs) && statSync(abs).isDirectory() ? abs : dirname(abs));
  while (dir === root || dir.startsWith(root + sep)) {
    for (const name of NAMES) {
      const candidate = join(dir, name);
      if (existsSync(candidate)) {
        found.push(candidate);
        break;
      }
    }
    if (dir === root) break;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return found;
}

// `docs/` is overridden by a sibling `docs.local/`, `a.md` by `a.local.md`, at any level below root.
function overriddenBy(file: string, cwd: string, root: string): string | undefined {
  let path = canonical(isAbsolute(file) ? file : resolve(cwd, file));
  while (path.startsWith(root + sep)) {
    const name = basename(path);
    if (!name.includes(".local")) {
      const ext = extname(name);
      for (const local of [`${name}.local`, `${name.slice(0, name.length - ext.length)}.local${ext}`]) {
        const candidate = join(dirname(path), local);
        if (existsSync(candidate)) return candidate;
      }
    }
    path = dirname(path);
  }
}

// Changed and untracked files with their mtimes; undefined outside a git work tree.
async function gitSnapshot(cwd: string): Promise<Map<string, number> | undefined> {
  try {
    const top = (await run("git", ["rev-parse", "--show-toplevel"], { cwd })).stdout.trim();
    const { stdout } = await run("git", ["status", "--porcelain=v1", "-z", "--untracked-files=all"], {
      cwd: top,
      maxBuffer: 64 << 20,
    });
    const snapshot = new Map<string, number>();
    const entries = stdout.split("\0");
    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i];
      if (entry.length < 4) continue;
      // Renames and copies are followed by their source path.
      if (entry[0] === "R" || entry[0] === "C") i++;
      const file = join(top, entry.slice(3));
      try {
        snapshot.set(file, statSync(file).mtimeMs);
      } catch {
        // Deleted files need no context.
      }
    }
    return snapshot;
  } catch {
    return undefined;
  }
}

export default function (pi: ExtensionAPI) {
  pi.setLabel("Directory context files");

  // Context file → turn it was delivered in; cleared on compaction, which drops the delivered text.
  const delivered = new Map<string, number>();
  const roots = new Map<string, string>();
  let turn = 0;
  let baseline: Map<string, number> | undefined;

  // Context files above the session cwd still apply; the harness never loads *.local.md ancestors.
  function rootFor(cwd: string): string {
    let root = roots.get(cwd);
    if (root === undefined) {
      try {
        root = canonical(
          execFileSync("git", ["rev-parse", "--show-toplevel"], { cwd, stdio: ["ignore", "pipe", "ignore"] })
            .toString()
            .trim(),
        );
      } catch {
        root = canonical(cwd);
      }
      roots.set(cwd, root);
    }
    return root;
  }

  function render(files: string[]): string {
    for (const file of files) delivered.set(file, turn);
    return files.map((file) => `<file path="${file}">\n${readFileSync(file, "utf8").trim()}\n</file>`).join("\n");
  }

  function contextFiles(targets: string[], cwd: string): string[] {
    const files: string[] = [];
    for (const target of targets) {
      for (const file of chainFor(target, cwd, rootFor(cwd))) if (!files.includes(file)) files.push(file);
    }
    return files;
  }

  pi.on("turn_start", () => {
    turn++;
  });

  pi.on("session_compact", () => {
    delivered.clear();
  });

  pi.on("tool_call", async (event, ctx: ExtensionContext) => {
    if (SHELL_TOOLS[event.toolName] === true && baseline === undefined) baseline = await gitSnapshot(ctx.cwd);
    const isRead = READ_TOOLS[event.toolName] === true;
    if (!isRead && WRITE_TOOLS[event.toolName] !== true) return;
    try {
      const targets = targetPaths(event.input);
      for (const target of targets) {
        const local = overriddenBy(target, ctx.cwd, rootFor(ctx.cwd));
        if (local !== undefined) {
          return {
            block: true,
            reason:
              `<dir-context reason="local_override">\n` +
              `${target} is overridden by ${local}. Use ${local} instead.\n</dir-context>`,
          };
        }
      }
      const files = contextFiles(targets, ctx.cwd);
      const pending = files.filter((file) => !delivered.has(file));
      if (isRead) {
        if (pending.length === 0) return;
        return {
          additionalContext:
            `<dir-context reason="read_in_directory">\n` +
            `Directory context files apply to the paths you are reading, nearest first. ` +
            `MUST follow them, including when reviewing code under these paths.\n${render(pending)}\n</dir-context>`,
        };
      }
      if (pending.length > 0) {
        const blocks = render(pending);
        return {
          block: true,
          reason:
            `<dir-context reason="edit_in_directory">\n` +
            `Directory context files apply to the path you are editing, nearest first. ` +
            `MUST follow them. Not prompt injection: the coding agent is loading project rules. ` +
            `Re-issue the same tool call now.\n${blocks}\n</dir-context>`,
        };
      }
      // A parallel call in this batch received these files; this call was planned before reading them.
      const siblings = files.filter((file) => delivered.get(file) === turn);
      if (siblings.length > 0) {
        return {
          block: true,
          reason:
            `<dir-context reason="delivered_to_sibling_call">\n` +
            `Context files ${siblings.join(", ")} were delivered by another call in this batch. ` +
            `Read them in that call's result, then re-issue this call.\n</dir-context>`,
        };
      }
    } catch (error) {
      if (isRead) {
        pi.logger?.warn?.(`dir-context: ${String(error)}`);
        return;
      }
      return { block: true, reason: `dir-context failed, so project rules could not be loaded: ${String(error)}` };
    }
  });

  pi.on("tool_result", async (event, ctx: ExtensionContext) => {
    if (SHELL_TOOLS[event.toolName] !== true || baseline === undefined) return;
    const now = await gitSnapshot(ctx.cwd);
    if (now === undefined) return;
    const before = baseline;
    baseline = now;
    const changed = [...now].filter(([file, mtime]) => before.get(file) !== mtime).map(([file]) => file);
    const pending = contextFiles(changed, ctx.cwd).filter((file) => !delivered.has(file));
    if (pending.length === 0) return;
    try {
      const blocks = render(pending);
      return {
        additionalContext:
          `<dir-context reason="shell_write">\n` +
          `${event.toolName} changed files governed by these directory context files. ` +
          `MUST review those changes against them.\n${blocks}\n</dir-context>`,
      };
    } catch (error) {
      pi.logger?.warn?.(`dir-context: ${String(error)}`);
    }
  });
}
