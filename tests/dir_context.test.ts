import { afterEach, describe, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import dirContext from "../extensions/dir-context";

type Callback = (...args: unknown[]) => Promise<unknown>;
type BlockResult = { block: true; reason: string } | undefined;

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
  let handler: Callback | undefined;
  const apiShape = {
    setLabel() {},
    on(name: string, registered: Callback) {
      expect(name).toBe("tool_call");
      handler = registered;
    },
  };
  // The test double implements only the registration methods this extension uses.
  dirContext(apiShape as unknown as Parameters<typeof dirContext>[0]);
  return (toolName: string, input: Record<string, unknown>) => {
    if (!handler) throw new Error("Missing tool_call handler");
    return handler({ toolName, input }, { cwd }) as Promise<BlockResult>;
  };
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

  test("only write tools trigger loading", async () => {
    const root = workspace({ "AGENTS.md": "rules" });
    for (const tool of ["read", "grep", "bash", "glob"]) {
      expect(await loadExtension(root)(tool, { path: "a.ts" })).toBeUndefined();
    }
    for (const tool of ["edit", "write", "apply_patch", "notebook_edit"]) {
      expect(loadedPaths(await loadExtension(root)(tool, { path: "a.ts" }))).toEqual([join(root, "AGENTS.md")]);
    }
  });

  test("a context file is delivered once per session", async () => {
    const root = workspace({ "AGENTS.md": "rules" });
    const call = loadExtension(root);
    expect(loadedPaths(await call("edit", { path: "a.ts" }))).toHaveLength(1);
    expect(await call("edit", { path: "b.ts" })).toBeUndefined();
  });
});
