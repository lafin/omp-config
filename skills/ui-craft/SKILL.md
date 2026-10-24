---
name: ui-craft
description: >
  Build or review the web UI details that make an interface feel polished:
  radii, alignment, shadows, motion, typography, color tokens and themes,
  accessibility basics, spacing, microcopy. Use for "make it feel better",
  "polish this UI", "feels off", janky animation, hover/focus states, dark mode
  colors, button labels, or a frontend/CSS/Tailwind detail review. Route API
  and module interface design to api-and-interface-design, bloat review to
  leancode-review, and security to security-review.
license: MIT
metadata:
  upstream: "https://github.com/jakubkrehel/make-interfaces-feel-better"
  upstream_commit: "35545ea1512ad59fa463e6b1f95ca9c052981fe6"
  upstream_path: "skills/make-interfaces-feel-better/SKILL.md"
  adaptation: inspired
  source_note: >
    Rules restated from https://interfaces.dev/cheat-sheet (Jakub Krehel,
    fetched 2026-10-21). Also inspired by pbakaus/impeccable at
    936867543ac2576920d663cc9803597f6044f3ac (Apache-2.0; skill/reference/,
    crates/foundation/src/registry.rs) and Nutlope/hallmark at
    7ec868225c6caa040558c321ee0fefa0e73f83a8 (MIT; skills/hallmark/references/,
    skills/hallmark/scripts/sloplint.mjs), fetched 2026-10-24. No text copied.
---

# UI Craft

Owns the small, checkable details of a web interface: one rule, one value,
one location. Apply while building UI, or return a findings table when
reviewing it. Rules are defaults with concrete values; a project's documented
design system overrides them.

## Workflow

1. **Detect the styling system** from `package.json`, config, and nearby
   components: plain CSS, Tailwind, CSS-in-JS, Motion (`motion` or
   `framer-motion`). Express every fix in that system. Never add a second
   styling system or a motion library for a polish fix.
2. **Detect the theme switch** (`prefers-color-scheme`, `.dark`, or
   `[data-theme]`) and the token layer (semantic vs primitive, spacing scale,
   z-index scale, motion tokens). Fixes reuse them.
3. **Walk the rules below** for the touched surface. Building: apply them.
   Reviewing: record findings (see Output), including any generated-looking
   tells.
4. **Verify in a real browser** (see Exit evidence). A rule is not applied
   until the state that exercises it has been seen.

References, each loaded only when needed:

- [references/recipes.md](references/recipes.md): code for the non-obvious
  rules (layered shadow, hit-area pseudo-element, icon cross-fade, focus ring,
  height animation, tooltip timing, reduced-motion fallback, delayed spinner,
  drag cleanup, theme-switch transition kill, form errors, stagger, tokens).
  Read when writing or proposing a fix.
- [references/slop-tells.md](references/slop-tells.md): detection signals
  (selectors, CSS patterns, thresholds) for the generated-looking tells. Read
  when reviewing a whole page or when the user says the UI looks generic,
  templated, or AI-made.

## Rules

### Surfaces

- **Concentric radii.** Nested rounded elements: `outer = inner + padding`.
  `8px` inner with `8px` padding → `16px` outer. Above ~`24px` padding, treat
  layers as separate surfaces.
- **Optical over geometric alignment.** Icon+text button: icon side gets
  ~`2px` less padding than the text side. Play triangles shift right ~`1–2px`.
  Prefer fixing the SVG itself over adding margin.
- **Depth via layered `box-shadow`, not borders**, on cards, buttons,
  popovers. Keep real borders for dividers, table cells, inputs, and
  selected/focus states.
- **One elevation per surface:** a border **or** a shadow. A 1px border under
  a wide soft shadow is the "ghost card"; the ring-shadow recipe counts as one
  shadow.
- **Separate content by the lightest means first:** whitespace, then a 1px
  divider, then a tinted well, then a card. Cards hold independently
  interactive or different-kind content. Never a card inside a card.
- **Image outline:** `outline: 1px solid` black at `8%` (light) / white at
  `8%` (dark), `outline-offset: -1px`. Pure black/white only; tinted neutrals
  read as dirt.
- **Icon stroke matches adjacent text weight** (~`1.5px` beside 400, `2px`
  beside 500–600 on a 24px grid). One icon set per surface; `currentColor`
  for states. Real icons, never emoji or Unicode glyphs.
- **Named z-index scale** in fixed order (base < raised < dropdown < sticky <
  modal < toast < tooltip). No ad-hoc `9999`.
- **Clip with `overflow-x: clip`**, not `hidden`, on page wrappers; `hidden`
  creates a scroll container and breaks `position: sticky`.

### Motion

- **Duration by job:** `100–150ms` press, toggle, color; `150–300ms` hover
  reveal, menu, tooltip; `300–500ms` modal, drawer, accordion, view change;
  `500–800ms` only for one authored entrance. Longer feedback reads as lag.
- **Easing by direction:** ease-out for arrivals (`cubic-bezier(0.16, 1, 0.3,
  1)` or the project token), ease-in for departures, ease-in-out for on-screen
  toggles. `linear` only for progress and scrubbing. No bounce, elastic, or
  overshoot on UI state.
- **Animate from the trigger:** set `transform-origin` toward the trigger
  (dropdown under a button → `top left`/`top center`), not `center`.
- **Frequently opened menus:** no open animation; animate close only.
- **Exits subtler than entrances:** `60–75%` of the entrance duration,
  shorter distance, fade `opacity`, add `blur(4px)`.
- **Never `transition: all`** (nor Tailwind `transition-all`). Name the
  properties.
- **Animate `transform` and `opacity`** (`filter`, `clip-path` when smooth).
  Never `width`, `height`, `top`, `left`, or margins: height via
  `grid-template-rows: 0fr → 1fr`, tab indicators via `transform`.
- **Press feedback:** `scale` `0.95–0.98` on `:active`, `transition: scale
  200ms ease-out`. Never below `0.95`.
- **Focus rings never animate.**
- **Tooltips:** `800–1000ms` hover delay, instant on keyboard focus, stay
  while the pointer moves onto them, `Esc` dismisses (WCAG 1.4.13).
- **Icon swap:** cross-fade; incoming `scale 0.25→1`, `opacity 0→1`,
  `blur 4px→0`; outgoing reversed; both simultaneously.
- **Transitions for interactions** (retarget mid-flight); **keyframes only
  for one-shot sequences**.
- **Disable all transitions while switching theme.**
- **1–2px jitter during animation** (notably iOS Safari): add
  `will-change: transform` to that element only. Never `will-change: all`
  or blanket use.
- **Stagger entrances in small semantic groups** (~`100ms` between title,
  body, actions), total under `500ms`; not one block and not per-row on
  routine UI.
- **No animation on page load** unless the entrance is the point
  (`AnimatePresence initial={false}` for toggles/tabs/icons). Content is
  visible by default; never parked at `opacity: 0` waiting for a script.
- **High-frequency interactions** (hover color, typing, tab switch): instant
  or ≤`150ms` on color/opacity only.
- **Loops stop** off-screen and under reduced motion; anything moving longer
  than 5s gets a pause control (WCAG 2.2.2). No pulsing status dots or
  unpausable marquees.
- **Reduced motion:** wrap travel, scale, and parallax in
  `@media (prefers-reduced-motion: no-preference)`; keep opacity and color
  state changes (~`150ms` cross-fade). A global `transition-duration: 0.01ms`
  kill removes feedback too.
- **Scroll-driven animation** only inside
  `@supports (animation-timeline: view())` plus the reduced-motion guard,
  with the static page complete without it.

### Typography

- `.woff2` only; no `.ttf`/`.otf` on the web. `font-display: swap`, a
  same-build fallback (grotesk → `system-ui`, serif → Georgia),
  `font-synthesis: none`, only the weights used.
- Body text ≥`16px`; nothing running below `12px`. Form inputs ≥`16px` on
  mobile or iOS Safari zooms on focus.
- Size steps between heading levels and body ≥`1.25×`; flatter reads as no
  hierarchy.
- Line height: body `1.5–1.65` (long prose up to `1.75`), display
  `1.0–1.15`, never below `1.3` on running text.
- Tracking: display `-0.02em` to `-0.04em` (never tighter; heavy or condensed
  faces `0` to `-0.015em`); body and labels ≤`0.05em`.
- `font-variant-numeric: tabular-nums` on timers, counters, prices, numeric
  table columns; skip in monospace fonts and on static/decorative numbers.
- Long-form measure `45–75ch` (default `max-width: 65ch`).
- `text-wrap: balance` on headings, `text-wrap: pretty` on short
  descriptions; neither on long-form text.
- `overflow-wrap: break-word` for long words, URLs, IDs;
  `white-space: nowrap` on labels and badges. Flex/grid children that hold
  text get `min-width: 0` so they can shrink.
- Justified text only with `hyphens: auto`; otherwise left-align.
- Root: `-webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale` (Tailwind `antialiased` on `<html>`/
  `<body>`), once, not per element.
- Source text in normal case; uppercase/lowercase via `text-transform`.
  Labels, table heads, and meta in sentence case.
- Smart punctuation: curly quotes, en dash for ranges (`3–5`), em dash for
  asides (sparingly), `…` not `...`, non-breaking space in number+unit pairs
  (`10 MB`, `⌘ K`).
- Underlines: `text-underline-position: from-font;
  text-decoration-skip-ink: auto`; thickness ≤`2px`, offset ≤`0.25em`.
- Truncated text (`text-overflow: ellipsis`, `line-clamp`) must be readable
  in full via tooltip, `title`, or expanded view.
- Monospace only for code, data, and measurements.

### Color

- Every palette step has a named job (page bg, hover, border, solid fill,
  text). Delete unused steps.
- Components consume **semantic tokens** (`--color-text-secondary`), never
  primitives (`--blue-500`).
- Name tokens by purpose (`--color-accent-solid`), not hue or place
  (`--color-blue-button`, `--color-sidebar-gray`).
- `accent` = brand. `primary` never means both brand and body text. The
  accent is a signal (primary action, active item, focus, links), not a fill,
  unless the brand deliberately floods a surface.
- Contrast: body text `4.5:1`, large text (≥`24px`, or ≥`18.7px` bold)
  `3:1`; icons, focus rings, and input borders `3:1` (WCAG 1.4.11).
- Measure contrast against the background directly behind the element
  (overlays, cards, images included).
- Never gray text on a colored surface: derive secondary text from the
  surface hue or the foreground.
- Neutrals carry a faint tint of the brand hue (OKLCH chroma
  `~0.005–0.015`); pure `#000`/`#fff` surfaces and text read harsh.
- OKLCH ramps step lightness and lower chroma near white and black.
- Dark mode gets its own palette; never invert light. Raised surfaces are
  lighter than the canvas, elevation comes from lightness or a ring (shadows
  barely show), accent chroma drops `0.02–0.04` with lightness up `5–10%`.
  Set `color-scheme: dark`; never `filter: invert()` on images.
- One theme mechanism: `prefers-color-scheme` **or** a class/attribute, not
  both.
- Gradients declare interpolation: `in oklab` (even brightness), `in oklch`
  (vivid middle, may show undefined hues), `in srgb` (muted midtones). At
  most three stops.

### Accessibility

- Native elements: `<button>` for actions, `<a href>` for navigation,
  `<dialog>` with `showModal()` for modals (focus containment, `Esc`, inert
  page), focus returned to the trigger on close. Explicit `type` on every
  `<button>`.
- Style `:focus-visible`, not `:focus`; never remove an outline without a
  visible replacement. Default ring: `outline: 2px solid` focus token,
  `outline-offset: 2px` (inset on inputs), `3:1` against both the element and
  the page; never a border-width change.
- `tabindex` only `0` or `-1`.
- Icon-only buttons get a descriptive `aria-label`. No `aria-hidden="true"`
  on anything focusable. Decorative SVGs get `aria-hidden="true"`.
- `alt` states purpose and content; decorative images `alt=""`.
- Every input: visible `<label>`, correct `type`, `inputmode`, and
  `autocomplete`. Placeholders show an example, never the label.
- Never block paste.
- Forms: submit stays enabled until the request starts; validate on submit;
  `aria-invalid="true"` on bad fields, error linked with
  `aria-describedby`, focus moves to the first invalid field.
- Disabled uses the native `disabled` attribute (`aria-disabled="true"` when
  it must stay focusable), lowered opacity, and `cursor: not-allowed`.
- Hit areas ≥`24×24px`; aim `44×44px` touch, `40×40px` desktop; never
  overlapping. Extend with a pseudo-element.
- Decorative glows/gradients: `pointer-events: none`.
- Hover styles inside `@media (hover: hover)` (sticky `:hover` on touch).
  Input modality via `(hover)`/`(pointer: coarse)`, not viewport width.
- Drag surfaces set `touch-action`; `pointercancel`, `lostpointercapture`,
  and `blur` clear drag state so the next gesture works.
- `role="status"` for routine updates; `role="alert"` only for urgent errors.
- Never color alone for state: add icon, label, or underline.
- Content survives `200%` zoom without loss or overlap.

### Layout

- Spacing from the project scale (default 4px base: `4, 8, 12, 16, 24, 32,
  48, 64, 96`); no raw off-scale values. `gap` for siblings, margin only to
  break flow.
- Space between groups ≥ 2× space within a group (`8px` items → `16px+`
  groups). Space above a heading > space below it.
- One spacing value everywhere is monotony; rhythm needs at least three
  steps in use.
- `scroll-margin-top` on anchor targets (≥ sticky header height).
- Text ≥`16px` from the viewport edge (`24–32px` ideal). Fixed bars use
  `max(1rem, env(safe-area-inset-bottom))` with `viewport-fit=cover`.
- Cap content width on wide screens; grids use `minmax(0, 1fr)`; media in
  flex rows get `flex-shrink: 0`.
- Images declare `width`/`height` or `aspect-ratio`; never
  `loading="lazy"` on the largest above-the-fold image.
- Clickable labels (buttons, nav, tabs) stay on one line: shorten, then
  `nowrap`, then collapse behind a menu. Tab rows scroll sideways.
- Tables on phones keep the identifying and action columns visible: restack
  rows as labelled blocks or pin the first column.

### States

- Every interactive element: default, hover, focus-visible, active,
  disabled, loading, error; success where an action completes.
- Loading keeps the control's width. Spinner appears only after
  `150–300ms` and stays ≥`300ms` once shown; past ~`2s`, name the operation.
  Never fake progress.
- Empty states distinguish first use, no results, filtered out, no
  permission, and failure; each explains what belongs there plus one action.
- Reversible destructive actions act immediately with a `5–10s` Undo;
  confirm only irreversible ones.
- Optimistic updates roll back visibly on failure.
- Success is mostly inline ("Copied" for ~`2s`), not a toast. Toasts last
  `4–6s` and pause on hover/focus; error toasts with an action persist until
  dismissed.
- Search-as-you-type debounces `250–300ms`.

### Writing

- Buttons start with a verb: "Save draft", never "OK"/"Yes"/"Submit".
- Confirmations name the outcome: "Delete project" beside "Cancel".
- One next-step label per flow ("Continue" **or** "Next").
- Link text says where it goes; no "click here".
- One capitalization style everywhere; default sentence case.
- One term per concept across the product; no synonyms for variety.
- Toggles describe the on state: "Send read receipts", not "Disable …".
- Errors say what happened, why if known, and how to fix it. No "Oops", no
  exclamation marks, no raw error codes as the message.
- Address the reader as "you", never "the user".
- Never invent figures, testimonials, or a success message for a form that
  sends nothing; use a visible placeholder and say what is missing.

### Generated-looking tells

Defaults that make a UI read as templated. Each is a finding unless the
project's design system deliberately chose it. Detection signals:
[references/slop-tells.md](references/slop-tells.md).

- Gradient text; purple-to-blue/pink gradients; cyan on dark; glows, radial
  halos, zero-offset colored shadows.
- Thick colored side stripe (`border-left` ≥`3px`) on cards, alerts, list
  items.
- Tracked-uppercase eyebrow above headings; pill chip above the hero
  headline; one italic or colored word in a headline.
- Same-size grid of icon tile + heading + text as the page structure;
  nested cards; ghost cards.
- Hard offset shadows (`4px 4px 0`) outside a neobrutalist system.
- Emoji or Unicode glyphs as icons; monospace as "technical" costume.
- Decorative grid/stripe backgrounds and noise grain with no subject reason.
- Section numbers (`01 / 02 / 03`) that carry no sequence.
- Hero metrics and stat rows with numbers nobody supplied.
- Bounce easing, pulsing dots, blinking carets, marquees.
- Copy: buzzwords ("seamless", "unlock", "elevate", "game-changer"),
  "not just X, it's Y" cadence, em dash in most sentences.

## Failure modes

- **Polish by restyle:** changing fonts, palette, or brand to "fix" feel.
  Rules here are rendering and behavior details; keep the product's type and
  color choices. Removing a tell means removing the decoration, not
  rebranding.
- **Second system:** inline CSS in a Tailwind codebase, or installing Motion
  for one icon swap. Use the CSS cross-fade.
- **Shadow everything:** replacing dividers, inputs, or focus borders with
  shadows. Those borders carry structure or state.
- **Blanket `will-change`/`transition`** on a global selector. Scope to the
  element that needs it.
- **Stagger as decoration:** stagger on list rows, hovers, or keystrokes.
- **`initial={false}` everywhere:** kills intentional hero entrances.
- **Primitive token leak:** a fix that writes `--gray-200` into a component.
- **Contrast checked on the page background** while the text sits on a card,
  image, or translucent overlay.
- **Slop hunt as taste veto:** flagging a deliberate, documented brand choice
  (a neobrutalist offset shadow, a mono-first product) as a tell.
- **Claiming a motion fix without watching it:** timing bugs are invisible in
  code review.

## Exit evidence

Building: run the dev server and inspect the changed surface in a browser.
Reviewing: inspect source, then the rendered surface when runnable. Check, as
relevant to the change:

- hover, focus-visible (keyboard Tab), active, disabled, loading, empty,
  error, success states;
- light and dark themes, including the switch itself;
- motion at 10% speed (DevTools Animations panel), interrupted mid-flight;
- `prefers-reduced-motion: reduce` emulation;
- touch emulation for sticky hover, hit areas, and an interrupted drag;
- widths `320`, `375`, `768`, `1024`, `1440`, `1920` with long strings/IDs
  for wrapping and truncation, plus `200%` zoom;
- slow network throttling for loading thresholds.

Report what was not checked as **Not verified**, with the reason.

## Output (review mode)

State scope, styling system, and theme mechanism. Then one table, one row per
finding; a systemic issue is one row listing every location:

| Severity | Domain | Location | Fix | Rule |
| --- | --- | --- | --- | --- |
| HIGH | Accessibility | `dialog.tsx:42` | `aria-label="Close dialog"` on icon button | Icon-only buttons need a name |
| MEDIUM | Typography | `Price.tsx:17` | add `tabular-nums` | Changing digits shift layout |
| MEDIUM | Tells | `Hero.tsx:12` | drop `bg-clip-text` gradient; solid `--color-text` | Gradient text |
| LOW | Surfaces | `Card.tsx:28` | outer `rounded-2xl` (8+8) | Concentric radii |

- **HIGH:** inaccessible, misleading, unreadable, or repeatedly disruptive.
- **MEDIUM:** noticeable usability or consistency problem; a generated-looking
  tell on a primary surface.
- **LOW:** isolated polish.

End with **Verification** (exact checks run and observed results) and a
verdict: `Block` if any HIGH remains, `Needs changes` for MEDIUM/LOW only,
`Approve` when nothing actionable remains. No findings → say "No actionable
UI-craft findings", list checks, `Approve`. Never pad to look thorough.
