import { describe, expect, test } from "bun:test";
import kesselRefusal from "../extensions/kessel-refusal";

const PREFIX = "upstream safety classifier declined the request";
const REDIRECT_NOTICE = "Kessel response reports a session redirect after a safety refusal (cyber); configured target: z-ai/glm-5.3:high. This signal does not confirm a successful answer. /tree can rewind manually; /compact may release the redirect so a later request retries the requested model.";
const FALLBACK_NOTICE = "Kessel response reports Anthropic server-side fallback to claude-opus-5. This signal does not confirm completion of the agent run.";
const REFUSAL_NOTICE = "Request refused. /tree can rewind for manual rephrasing. /compact may release an existing redirect; a later request can still refuse or fail. Rewinding does not undo file or command side effects.";

type Callback = (event: unknown, ctx: unknown) => unknown;

function loadExtension() {
  const handlers: Record<string, Callback> = {};
  const notices: Array<[string, string | undefined]> = [];
  // Only registration and UI notification exist: unexpected requests or session writes fail.
  kesselRefusal({
    setLabel() {},
    on(name: string, handler: Callback) {
      handlers[name] = handler;
    },
  } as unknown as Parameters<typeof kesselRefusal>[0]);
  const ctx = { ui: { notify: (message: string, type?: string) => notices.push([message, type]) } };
  return {
    notices,
    handlers,
    response: (headers: Record<string, string> = {}, status = 200) =>
      handlers.after_provider_response(Object.freeze({ headers: Object.freeze(headers), status }), ctx),
    end: (message: Record<string, unknown>) => handlers.message_end({ message: Object.freeze(message) }, ctx),
  };
}

describe("Kessel refusal response signals", () => {
  test("registers only observational events and reports both headers immediately", () => {
    const ext = loadExtension();
    expect(Object.keys(ext.handlers).sort()).toEqual(["after_provider_response", "message_end"]);
    expect(ext.response({
      "x-kessel-refusal-redirect": "category=cyber; model=z-ai/glm-5.3:high",
      "x-kessel-server-fallback": "model=claude-opus-5",
    })).toBeUndefined();
    expect(ext.notices).toEqual([[REDIRECT_NOTICE, "warning"], [FALLBACK_NOTICE, "warning"]]);
  });

  test("repeated callbacks report each signal without a visible assistant message", () => {
    const ext = loadExtension();
    for (let i = 0; i < 2; i++) {
      ext.response({ "x-kessel-refusal-redirect": "category=cyber; model=z-ai/glm-5.3:high" });
      ext.response({ "x-kessel-server-fallback": "model=claude-opus-5" });
    }
    expect(ext.notices).toEqual([
      [REDIRECT_NOTICE, "warning"], [FALLBACK_NOTICE, "warning"],
      [REDIRECT_NOTICE, "warning"], [FALLBACK_NOTICE, "warning"],
    ]);
  });

  test("headerless retries, subsequent runs, and new instances inherit no signals", () => {
    const ext = loadExtension();
    ext.response({ "x-kessel-refusal-redirect": "category=cyber; model=z-ai/glm-5.3:high" });
    ext.notices.length = 0;
    for (let i = 0; i < 2; i++) {
      ext.response();
      ext.end({ role: "assistant", stopReason: "stop", content: [] });
    }
    expect(ext.notices).toEqual([]);
    const next = loadExtension();
    next.response();
    expect(next.notices).toEqual([]);
  });

  test("ignores malformed headers rather than partially parsing them", () => {
    const malformedModels = ["", " ", "foo bar", "foo\tbar", "foo\n", "foo\r", "foo\x00", "foo\x1b", "foo\x7f", "foo; extra=yes", "foo, model=bar"];
    const ext = loadExtension();
    for (const model of malformedModels) {
      ext.response({
        "x-kessel-refusal-redirect": `category=cyber; model=${model}`,
        "x-kessel-server-fallback": `model=${model}`,
      });
    }
    for (const header of [
      "category=; model=foo", "category=cyber-policy; model=foo", "category=cyber policy; model=foo",
      "category=cyber; model=foo; model=bar", "category=cyber; model=foo, category=bio; model=bar",
      "prefix category=cyber; model=foo", "category=cyber; model=foo\n",
      "model=foo; category=cyber", "category=cyber;model=foo", "Category=cyber; model=foo",
    ]) ext.response({ "x-kessel-refusal-redirect": header });
    for (const header of ["prefix model=foo", "model=foo; extra=yes", "Model=foo", "model=foo\n"]) {
      ext.response({ "x-kessel-server-fallback": header });
    }
    expect(ext.notices).toEqual([]);
  });

  test("a malformed signal does not suppress another valid header", () => {
    const ext = loadExtension();
    ext.response({ "x-kessel-refusal-redirect": "broken", "x-kessel-server-fallback": "model=claude-opus-5" });
    expect(ext.notices).toEqual([[FALLBACK_NOTICE, "warning"]]);
  });

  test("category is a word, not a provider name or a category whitelist", () => {
    const ext = loadExtension();
    ext.response({ "x-kessel-refusal-redirect": "category=policy_2; model=openai/gpt-6.1:high" });
    expect(ext.notices[0][0]).toContain("safety refusal (policy_2); configured target: openai/gpt-6.1:high.");
    expect(ext.notices[0][0]).not.toContain("Claude");
  });

  test("requires an assistant error containing the owned prefix", () => {
    const ext = loadExtension();
    for (const role of ["user", "toolResult"]) {
      ext.end({ role, stopReason: "error", errorMessage: PREFIX });
    }
    for (const stopReason of ["stop", "toolUse", "aborted", "length"]) {
      ext.end({ role: "assistant", stopReason, errorMessage: PREFIX });
    }
    for (const errorMessage of [undefined, "content_filter", "Provider finish_reason: content_filter", "upstream error 502"]) {
      ext.end({ role: "assistant", stopReason: "error", errorMessage });
    }
    expect(ext.notices).toEqual([]);
    for (const errorMessage of [`400: ${PREFIX} (category cyber)`, `SSE error: ${PREFIX} (category bio)`]) {
      expect(ext.end({ role: "assistant", stopReason: "error", errorMessage })).toBeUndefined();
    }
    expect(ext.notices).toEqual([[REFUSAL_NOTICE, "warning"], [REFUSAL_NOTICE, "warning"]]);
  });

  test("tool use then non-refusal failure never becomes a completed-answer notice", () => {
    const ext = loadExtension();
    ext.response({ "x-kessel-server-fallback": "model=claude-opus-5" });
    ext.end({ role: "assistant", stopReason: "toolUse", errorMessage: PREFIX });
    ext.end({ role: "toolResult", content: "tool failed" });
    ext.end({ role: "assistant", stopReason: "error", errorMessage: "upstream error 502" });
    expect(ext.notices).toEqual([[FALLBACK_NOTICE, "warning"]]);
  });

  test("a header-bearing refusal produces a signal followed by manual guidance", () => {
    const ext = loadExtension();
    ext.response({ "x-kessel-refusal-redirect": "category=cyber; model=z-ai/glm-5.3:high" });
    ext.end({ role: "assistant", stopReason: "error", errorMessage: PREFIX });
    expect(ext.notices).toEqual([[REDIRECT_NOTICE, "warning"], [REFUSAL_NOTICE, "warning"]]);
  });
});
