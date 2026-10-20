import { afterEach, describe, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import autoresearch from "../hooks/pre/autoresearch";

type Callback = (...args: unknown[]) => Promise<unknown>;
type Verdict = { block?: boolean; reason?: string } | undefined;

const RUN = "autoresearch/fix-261020-1405";
const HEADER = "iteration\tcommit\tmetric\tdelta\tguard\tstatus\tdescription";
const temps: string[] = [];

afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

function project(active: boolean, rows = 0): string {
  const cwd = mkdtempSync(join(tmpdir(), "autoresearch-hook-"));
  temps.push(cwd);
  if (!active) return cwd;
  mkdirSync(join(cwd, RUN), { recursive: true });
  writeFileSync(join(cwd, "autoresearch/.active"), `${RUN}\n`);
  const lines = [HEADER, ...Array.from({ length: rows }, (_, i) => `${i}\tc${i}\t${10 - i}\t-1\tpass\tkeep\tchange ${i}`)];
  writeFileSync(join(cwd, RUN, "fix-results.tsv"), `${lines.join("\n")}\n`);
  return cwd;
}

function loadHook() {
  const handlers: Record<string, Callback | undefined> = {};
  const apiShape = {
    on(name: string, handler: Callback) {
      handlers[name] = handler;
    },
  };
  // The test double implements only `on`, the single registration method this hook uses.
  autoresearch(apiShape as unknown as Parameters<typeof autoresearch>[0]);
  const callback = (name: string): Callback => {
    const registered = handlers[name];
    if (!registered) throw new Error(`Missing ${name} handler`);
    return registered;
  };
  // Results are the hook's own return shapes; the cast only names them for assertions.
  const toolCall = (cwd: string, toolName: string, input: unknown) =>
    callback("tool_call")({ toolName, input }, { cwd }) as Promise<Verdict>;
  return {
    events: Object.keys(handlers),
    bash: (cwd: string, command: string) => toolCall(cwd, "bash", { command }),
    evalCode: (cwd: string, code: string) => toolCall(cwd, "eval", { language: "py", code }),
    other: (cwd: string) => toolCall(cwd, "read", { command: "git push" }),
    compact: async (cwd: string): Promise<string[] | undefined> => {
      const result = await callback("session.compacting")({ sessionId: "s", messages: [] }, { cwd });
      if (result && typeof result === "object" && "context" in result && Array.isArray(result.context)) return result.context;
      return undefined;
    },
  };
}

const BLOCKED = [
  "git push",
  "git push origin main",
  "git push --force-with-lease origin main",
  "git push -f",
  "git push origin +main:main",
  "git -C sub push",
  "git reset --hard",
  "git reset --hard HEAD~1",
  "git clean -fd",
  "git clean -f",
  "git clean -n -f",
  "git clean --force -d",
  "rm -rf build",
  "rm -fr build",
  "rm -r -f build",
  "rm -f -r build",
  "rm --recursive --force build",
  "rm -R --force build",
  "/bin/rm -rf build",
  "echo ok && git push",
  "make test; rm -rf out",
  "cat log | git push",
  "FOO=1 git push",
  "sudo rm -rf /tmp/x",
  "bash -c 'git push origin main'",
];

const ALLOWED = [
  "git commit -am 'x'",
  "git revert HEAD --no-edit",
  "git status",
  "git reset --soft HEAD~1",
  "git clean -n",
  "git log --oneline",
  "rm file.txt",
  "rm -f file.txt",
  "rm -r dir",
  "echo 'git push is blocked'",
  "git commit -m 'avoid git push' && git status",
];

describe("autoresearch hook: tool_call", () => {
  test("registers only tool_call and session.compacting", () => {
    expect(loadHook().events.sort()).toEqual(["session.compacting", "tool_call"]);
  });

  test.each(BLOCKED)("blocks %p when active", async command => {
    const result = await loadHook().bash(project(true), command);
    expect(result?.block).toBe(true);
    expect(result?.reason).toContain(RUN);
    expect(result?.reason).toContain("autoresearch/.active");
  });

  test.each(BLOCKED)("allows %p when inactive", async command => {
    expect(await loadHook().bash(project(false), command)).toBeUndefined();
  });

  test.each(ALLOWED)("allows %p when active", async command => {
    expect(await loadHook().bash(project(true), command)).toBeUndefined();
  });

  test("blocks the same patterns inside eval code only when active", async () => {
    const hook = loadHook();
    const codes = [
      "import subprocess\nsubprocess.run(['git', 'push', '--force-with-lease'])",
      "subprocess.run('git reset --hard', shell=True)",
      "!git clean -fd",
      "await Bun.$`rm -rf build`",
      "os.system('rm -r -f build')",
    ];
    for (const code of codes) {
      expect((await hook.evalCode(project(true), code))?.block).toBe(true);
      expect(await hook.evalCode(project(false), code)).toBeUndefined();
    }
    expect(await hook.evalCode(project(true), "print(1 + 1)")).toBeUndefined();
    expect(await hook.evalCode(project(true), "subprocess.run(['git', 'commit', '-m', 'x'])")).toBeUndefined();
  });

  test("ignores other tools", async () => {
    expect(await loadHook().other(project(true))).toBeUndefined();
  });
});

describe("autoresearch hook: session.compacting", () => {
  test("returns nothing when inactive", async () => {
    expect(await loadHook().compact(project(false))).toBeUndefined();
  });

  test("includes run summary, state files, and header + last 10 TSV rows", async () => {
    const cwd = project(true, 15);
    writeFileSync(join(cwd, RUN, "handoff.json"), JSON.stringify({ schema_version: 1, goal: "fewer failures" }));
    const context = await loadHook().compact(cwd);
    expect(context).toHaveLength(2);
    expect(context?.[0]).toContain(RUN);
    expect(context?.[0]).toContain("fewer failures");
    expect(context?.[1]).toContain(HEADER);
    expect(context?.[1]).toContain("14\tc14\t-4\t-1\tpass\tkeep\tchange 14");
    expect(context?.[1]).toContain("\n5\tc5\t");
    expect(context?.[1]).not.toContain("\n4\tc4\t");
  });

  test("truncates large state files", async () => {
    const cwd = project(true);
    writeFileSync(join(cwd, RUN, "orchestrator-state.json"), "x".repeat(20000));
    const context = await loadHook().compact(cwd);
    expect(context?.[0].length).toBeLessThan(6000);
    expect(context?.[0]).toContain("truncated");
  });

  test("skips missing files without throwing", async () => {
    const cwd = project(true);
    rmSync(join(cwd, RUN), { recursive: true });
    const context = await loadHook().compact(cwd);
    expect(context).toHaveLength(1);
    expect(context?.[0]).toContain(RUN);
  });
});
