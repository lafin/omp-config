import { afterEach, describe, expect, test } from "bun:test";
import { execFileSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import dirContext from "../extensions/dir-context";

type Callback = (...args: unknown[]) => Promise<unknown>;
type BlockResult = { block: true; reason: string } | undefined;
type ContextResult = { additionalContext: string } | undefined;

const roots: string[] = [];

afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

function workspace(files: Record<string, string>): string {
  const root = realpathSync(mkdtempSync(join(tmpdir(), "dir-context-")));
  roots.push(root);
  for (const [path, body] of Object.entries(files)) {
    const full = join(root, path);
    mkdirSync(join(full, ".."), { recursive: true });
    writeFileSync(full, body);
  }
  return root;
}

function loadExtension(cwd: string) {
  const handlers: Record<string, Callback> = {};
  const apiShape = {
    setLabel() {},
    on(name: string, registered: Callback) {
      handlers[name] = registered;
    },
  };
  // The test double implements only the registration methods this extension uses.
  dirContext(apiShape as unknown as Parameters<typeof dirContext>[0]);
  const call = (toolName: string, input: Record<string, unknown>) =>
    handlers.tool_call({ toolName, input }, { cwd }) as Promise<BlockResult>;
  return Object.assign(call, {
    result: (toolName: string) => handlers.tool_result({ toolName }, { cwd }) as Promise<ContextResult>,
    turn: () => handlers.turn_start(),
    compact: () => handlers.session_compact(),
  });
}

function loadedPaths(result: BlockResult): string[] {
  return [...(result?.reason ?? "").matchAll(/<file path="([^"]+)">/g)].map((m) => m[1]);
}

describe("dir-context extension", () => {
  test("AGENTS.local.md wins over AGENTS.md and CLAUDE.md in the same directory", async () => {
    const root = workspace({
      "pkg/AGENTS.local.md": "local rules",
      "pkg/AGENTS.md": "agents rules",
      "pkg/CLAUDE.md": "claude rules",
    });
    const result = await loadExtension(root)("edit", { path: "pkg/a.ts" });
    expect(loadedPaths(result)).toEqual([join(root, "pkg/AGENTS.local.md")]);
    expect(result?.reason).toContain("local rules");
    expect(result?.reason).not.toContain("agents rules");
    expect(result?.reason).not.toContain("claude rules");
  });

  test("AGENTS.md wins over CLAUDE.md, and each directory contributes nearest first", async () => {
    const root = workspace({
      "CLAUDE.md": "root claude",
      "pkg/AGENTS.md": "pkg agents",
      "pkg/CLAUDE.md": "pkg claude",
    });
    const result = await loadExtension(root)("write", { path: join(root, "pkg/sub/a.ts") });
    expect(loadedPaths(result)).toEqual([join(root, "pkg/AGENTS.md"), join(root, "CLAUDE.md")]);
    expect(result?.reason).not.toContain("pkg claude");
  });

  test("reads deliver context passively; writes block", async () => {
    const root = workspace({ "AGENTS.md": "rules" });
    expect(await loadExtension(root)("lsp", { path: "a.ts" })).toBeUndefined();
    for (const tool of ["read", "grep", "glob"]) {
      const result = (await loadExtension(root)(tool, { path: "a.ts:10-20" })) as unknown as ContextResult;
      expect(result?.additionalContext).toContain(`<file path="${join(root, "AGENTS.md")}">`);
    }
    for (const tool of ["edit", "write", "apply_patch", "notebook_edit", "ast_edit"]) {
      expect(loadedPaths(await loadExtension(root)(tool, { path: "a.ts" }))).toEqual([join(root, "AGENTS.md")]);
    }
  });

  test("grep path lists and glob patterns resolve to their directories", async () => {
    const root = workspace({ "a/AGENTS.md": "a rules", "b/AGENTS.md": "b rules", "b/x/y.ts": "" });
    const result = (await loadExtension(root)("grep", { path: "a/**/*.ts;b/x" })) as unknown as ContextResult;
    expect([...(result?.additionalContext ?? "").matchAll(/<file path="([^"]+)">/g)].map((m) => m[1])).toEqual([
      join(root, "a/AGENTS.md"),
      join(root, "b/AGENTS.md"),
    ]);
  });

  test("a context file is delivered once per session", async () => {
    const root = workspace({ "AGENTS.md": "rules" });
    const call = loadExtension(root);
    expect(loadedPaths(await call("edit", { path: "a.ts" }))).toHaveLength(1);
    call.turn();
    expect(await call("edit", { path: "b.ts" })).toBeUndefined();
  });

  test("a parallel call in the same turn is blocked until the delivering call's result is read", async () => {
    const root = workspace({ "AGENTS.md": "rules" });
    const call = loadExtension(root);
    call.turn();
    expect(loadedPaths(await call("edit", { path: "a.ts" }))).toHaveLength(1);
    expect((await call("edit", { path: "b.ts" }))?.reason).toContain("delivered_to_sibling_call");
    call.turn();
    expect(await call("edit", { path: "b.ts" })).toBeUndefined();
  });

  test("compaction redelivers context files", async () => {
    const root = workspace({ "AGENTS.md": "rules" });
    const call = loadExtension(root);
    await call("edit", { path: "a.ts" });
    call.compact();
    call.turn();
    expect(loadedPaths(await call("edit", { path: "a.ts" }))).toHaveLength(1);
  });

  test("xd://ast_edit targets are read from the JSON content", async () => {
    const root = workspace({ "pkg/AGENTS.md": "rules" });
    const content = JSON.stringify({ ops: [], paths: ["pkg/a.ts"] });
    const result = await loadExtension(root)("write", { path: "xd://ast_edit", content });
    expect(loadedPaths(result)).toEqual([join(root, "pkg/AGENTS.md")]);
  });

  test("an unreadable context file blocks the write instead of allowing it", async () => {
    const root = workspace({ "AGENTS.md": "rules" });
    chmodSync(join(root, "AGENTS.md"), 0);
    const result = await loadExtension(root)("edit", { path: "a.ts" });
    chmodSync(join(root, "AGENTS.md"), 0o644);
    expect(result?.block).toBe(true);
    expect(result?.reason).toContain("dir-context failed");
  });

  test("files written through bash get their context after the call", async () => {
    const root = workspace({ "AGENTS.md": "root rules", "pkg/AGENTS.md": "pkg rules", "other/x.ts": "" });
    execFileSync("git", ["init", "-q"], { cwd: root });
    const call = loadExtension(root);
    expect(await call("bash", { command: "touch pkg/a.ts" })).toBeUndefined();
    writeFileSync(join(root, "pkg/a.ts"), "x");
    const result = await call.result("bash");
    expect([...(result?.additionalContext ?? "").matchAll(/<file path="([^"]+)">/g)].map((m) => m[1])).toEqual([
      join(root, "pkg/AGENTS.md"),
      join(root, "AGENTS.md"),
    ]);
    await call("bash", { command: "true" });
    expect(await call.result("bash")).toBeUndefined();
  });

  test("context files above a subdirectory cwd load up to the git root", async () => {
    const root = workspace({ "AGENTS.local.md": "root rules", "pkg/AGENTS.local.md": "pkg rules", "pkg/svc/a.ts": "" });
    execFileSync("git", ["init", "-q"], { cwd: root });
    const call = loadExtension(join(root, "pkg/svc"));
    expect(loadedPaths(await call("edit", { path: "a.ts" }))).toEqual([
      join(root, "pkg/AGENTS.local.md"),
      join(root, "AGENTS.local.md"),
    ]);
  });

  test(".local siblings override their counterparts at every level", async () => {
    const root = workspace({
      "CLAUDE.md": "claude",
      "AGENTS.md": "agents",
      "AGENTS.local.md": "root local",
      "docs/a.md": "",
      "docs.local/a.md": "",
      "aaa/AGENTS.local.md": "aaa local",
      "aaa/bbb/file1.ts": "",
      "bbb/file1.ts": "",
    });
    const call = loadExtension(root);
    expect(loadedPaths(await call("edit", { path: "bbb/file1.ts" }))).toEqual([join(root, "AGENTS.local.md")]);
    expect(loadedPaths(await call("edit", { path: "aaa/bbb/file1.ts" }))).toEqual([join(root, "aaa/AGENTS.local.md")]);
    expect((await call("read", { path: "docs/a.md" }))?.reason).toContain(join(root, "docs.local"));
    expect((await call("edit", { path: "AGENTS.md" }))?.reason).toContain(join(root, "AGENTS.local.md"));
    expect(await call("read", { path: "docs.local/a.md" })).toBeUndefined();
  });
});
