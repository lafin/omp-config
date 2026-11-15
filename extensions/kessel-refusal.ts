// Disable per profile with `disabledExtensions: [extension-module:kessel-refusal]`.
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Match the whole header; reject controls, whitespace in model ids, and joined/extra fields.
const REDIRECT = /^category=(\w+); model=([^\s\x00-\x1f\x7f;,]+)(?![\s\S])/;
const SERVER_FALLBACK = /^model=([^\s\x00-\x1f\x7f;,]+)(?![\s\S])/;
const REFUSAL_PREFIX = "upstream safety classifier declined the request";

export default function (pi: ExtensionAPI) {
  pi.setLabel("Kessel refusal signals");

  pi.on("after_provider_response", (event, ctx) => {
    const redirect = REDIRECT.exec(event.headers["x-kessel-refusal-redirect"] ?? "");
    if (redirect) {
      ctx.ui.notify(
        `Kessel response reports a session redirect after a safety refusal (${redirect[1]}); configured target: ${redirect[2]}. This signal does not confirm a successful answer. /tree can rewind manually; /compact may release the redirect so a later request retries the requested model.`,
        "warning",
      );
    }
    const fallback = SERVER_FALLBACK.exec(event.headers["x-kessel-server-fallback"] ?? "");
    if (fallback) {
      ctx.ui.notify(
        `Kessel response reports Anthropic server-side fallback to ${fallback[1]}. This signal does not confirm completion of the agent run.`,
        "warning",
      );
    }
  });

  pi.on("message_end", ({ message }, ctx) => {
    if (
      message.role === "assistant" &&
      message.stopReason === "error" &&
      message.errorMessage?.includes(REFUSAL_PREFIX)
    ) {
      ctx.ui.notify(
        "Request refused. /tree can rewind for manual rephrasing. /compact may release an existing redirect; a later request can still refuse or fail. Rewinding does not undo file or command side effects.",
        "warning",
      );
    }
  });
}
