import { describe, expect, test } from "bun:test";
import leancode, { leancodeReminder } from "../hooks/pre/leancode";

const MARKER = "[omp:leancode-state]";

type Callback = (...args: unknown[]) => Promise<unknown>;

function loadHook(extension = leancode) {
  const handlers: Record<string, Callback | undefined> = {};
  let command: Callback | undefined;
  const statuses: Array<[string, string | undefined]> = [];
  const notifications: Array<[string, string | undefined]> = [];
  const apiShape = {
    on(name: string, handler: Callback) {
      handlers[name] = handler;
    },
    registerCommand(name: string, definition: { handler: Callback }) {
      expect(name).toBe("leancode");
      command = definition.handler;
    },
  };
  // The test double intentionally implements only the two registration methods used by this hook.
  const api = apiShape as unknown as Parameters<typeof leancode>[0];
  const context = {
    ui: {
      setStatus(key: string, value: string | undefined) {
        statuses.push([key, value]);
      },
      notify(message: string, type?: string) {
        notifications.push([message, type]);
      },
    },
  };
  const callback = (name: string): Callback => {
    const registered = handlers[name];
    if (!registered) throw new Error(`Missing ${name} handler`);
    return registered;
  };

  extension(api);

  return {
    statuses,
    notifications,
    start: () => callback("session_start")({}, context),
    setMode: (mode: string) => {
      if (!command) throw new Error("Missing leancode command");
      return command(mode, context);
    },
    apply: async (messages: unknown[] = []) => {
      const result = await callback("context")({ messages }, context);
      if (!result || typeof result !== "object" || !("messages" in result) || !Array.isArray(result.messages)) {
        throw new Error("Context handler did not return messages");
      }
      return { messages: result.messages };
    },
  };
}

function markedTexts(messages: unknown[]): string[] {
  return messages.flatMap(message => {
    if (!message || typeof message !== "object" || !("role" in message) || message.role !== "user") return [];
    if (!("content" in message) || !Array.isArray(message.content)) return [];
    return message.content.flatMap(part => {
      if (!part || typeof part !== "object" || !("type" in part) || part.type !== "text") return [];
      if (!("text" in part) || typeof part.text !== "string" || !part.text.includes(MARKER)) return [];
      return [part.text];
    });
  });
}

describe("leancode hook state", () => {
  test("reminders distinguish every active intensity and explicit off", () => {
    for (const mode of ["lite", "full", "ultra"] as const) {
      expect(leancodeReminder(mode)).toContain(`ACTIVE at ${mode}`);
    }
    expect(leancodeReminder("off")).toContain("Leancode is OFF");
    expect(leancodeReminder("off")).toContain("Do not apply leancode instructions");
  });

  test("active reminders let an explicitly requested report or format win; off does not", () => {
    for (const mode of ["lite", "full", "ultra"] as const) {
      expect(leancodeReminder(mode)).toContain("an explicitly requested report or format wins");
    }
    expect(leancodeReminder("off")).not.toContain("report or format wins");
  });

  test("all modes update context, status, and notification", async () => {
    const hook = loadHook();
    await hook.start();
    expect(hook.statuses).toEqual([["leancode", "lean:full"]]);

    let result = await hook.apply([]);
    expect(markedTexts(result.messages)).toHaveLength(1);
    expect(markedTexts(result.messages)[0]).toContain("ACTIVE at full");
    const injected = result.messages.at(-1);
    expect(injected && typeof injected === "object" && "attribution" in injected && injected.attribution).toBe("agent");

    for (const mode of ["lite", "ultra", "off", "full"] as const) {
      await hook.setMode(mode);
      result = await hook.apply([]);
      const reminders = markedTexts(result.messages);
      expect(reminders).toHaveLength(1);
      expect(reminders[0]).toContain(mode === "off" ? "Leancode is OFF" : `ACTIVE at ${mode}`);
    }

    expect(hook.statuses).toEqual([
      ["leancode", "lean:full"],
      ["leancode", "lean:lite"],
      ["leancode", "lean:ultra"],
      ["leancode", "lean:off"],
      ["leancode", "lean:full"],
    ]);
    expect(hook.notifications).toEqual([
      ["leancode lite", "info"],
      ["leancode ultra", "info"],
      ["leancode off", "info"],
      ["leancode full", "info"],
    ]);
  });

  test("invalid input reports the current mode without changing it", async () => {
    const hook = loadHook();
    await hook.start();
    await hook.setMode("constructor");
    const result = await hook.apply([]);

    expect(hook.statuses).toEqual([["leancode", "lean:full"]]);
    expect(hook.notifications).toEqual([["leancode: full (use lite|full|ultra|off)", "info"]]);
    expect(markedTexts(result.messages)[0]).toContain("ACTIVE at full");
  });

  test("mode persists across in-process hook instances", async () => {
    const firstSession = loadHook();
    await firstSession.setMode("off");

    const nextSession = loadHook();
    await nextSession.start();

    expect(nextSession.statuses).toEqual([["leancode", "lean:off"]]);
    expect(markedTexts((await nextSession.apply([])).messages)[0]).toContain("Leancode is OFF");
    await firstSession.setMode("full");
  });

  test("a fresh process defaults to full", async () => {
    const firstProcess = loadHook();
    await firstProcess.setMode("off");
    expect(markedTexts((await firstProcess.apply([])).messages)[0]).toContain("Leancode is OFF");

    // A distinct module instance has the same clean state as a restarted process.
    const restartedModule = await import("../hooks/pre/leancode.ts?restart-default");
    const restartedProcess = loadHook(restartedModule.default);
    await restartedProcess.start();
    expect(restartedProcess.statuses).toEqual([["leancode", "lean:full"]]);
    expect(markedTexts((await restartedProcess.apply([])).messages)[0]).toContain("ACTIVE at full");
    await firstProcess.setMode("full");
  });
});
