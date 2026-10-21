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
  source_note: "Rules restated from https://interfaces.dev/cheat-sheet (Jakub Krehel, fetched 2026-10-21); no text copied."
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
   `[data-theme]`) and the token layer (semantic vs primitive). Fixes reuse
   them.
3. **Walk the rules below** for the touched surface. Building: apply them.
   Reviewing: record findings (see Output).
4. **Verify in a real browser** (see Exit evidence). A rule is not applied
   until the state that exercises it has been seen.

Code recipes for the non-obvious rules (layered shadow, hit-area
pseudo-element, icon cross-fade, theme-switch transition kill, form error
wiring, stagger): read [references/recipes.md](references/recipes.md) when
writing or proposing the fix.

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
- **Image outline:** `outline: 1px solid` black at `8%` (light) / white at
  `8%` (dark), `outline-offset: -1px`. Pure black/white only; tinted neutrals
  read as dirt.
- **Icon stroke matches adjacent text weight** (~`1.5px` beside 400, `2px`
  beside 500–600 on a 24px grid). One icon set per surface; `currentColor`
  for states.

### Motion

- **Animate from the trigger:** set `transform-origin` toward the trigger
  (dropdown under a button → `top left`/`top center`), not `center`.
- **Frequently opened menus:** no open animation; animate close only.
- **Exits subtler than entrances:** shorter distance, fade `opacity`, add
  `blur(4px)`, shorter duration.
- **Never `transition: all`** (nor Tailwind `transition-all`). Name the
  properties.
- **Press feedback:** `scale` `0.95–0.98` on `:active`, `transition: scale
  200ms ease-out`. Never below `0.95`.
- **Icon swap:** cross-fade; incoming `scale 0.25→1`, `opacity 0→1`,
  `blur 4px→0`; outgoing reversed; both simultaneously.
- **Transitions for interactions** (retarget mid-flight); **keyframes only
  for one-shot sequences**.
- **Disable all transitions while switching theme.**
- **1–2px jitter during animation** (notably iOS Safari): add
  `will-change: transform` to that element only. Never `will-change: all`
  or blanket use.
- **Stagger entrances in small semantic groups** (~`100ms` between title,
  body, actions), not one block and not per-row on routine UI.
- **No animation on page load** unless the entrance is the point
  (`AnimatePresence initial={false}` for toggles/tabs/icons).
- **High-frequency interactions** (hover color, typing, tab switch): instant
  or ≤`150ms` on color/opacity only.
- **Reduced motion:** wrap movement in
  `@media (prefers-reduced-motion: no-preference)`; keep the static cue.

### Typography

- `.woff2` only; no `.ttf`/`.otf` on the web.
- `font-variant-numeric: tabular-nums` on timers, counters, prices, numeric
  table columns; skip in monospace fonts and on static/decorative numbers.
- Long-form measure `60–75ch` (`max-width: 65ch`).
- `text-wrap: balance` on headings, `text-wrap: pretty` on short
  descriptions; neither on long-form text.
- `overflow-wrap: break-word` for long words, URLs, IDs;
  `white-space: nowrap` on labels and badges.
- Root: `-webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale` (Tailwind `antialiased` on `<html>`/
  `<body>`), once, not per element.
- Source text in normal case; uppercase/lowercase via `text-transform`.
- Smart punctuation: curly quotes, en dash for ranges (`3–5`), em dash for
  asides, `…` not `...`.
- Underlines: `text-underline-position: from-font;
  text-decoration-skip-ink: auto`.
- Truncated text (`text-overflow: ellipsis`, `line-clamp`) must be readable
  in full via tooltip, `title`, or expanded view.

### Color

- Every palette step has a named job (page bg, hover, border, solid fill,
  text). Delete unused steps.
- Components consume **semantic tokens** (`--color-text-secondary`), never
  primitives (`--blue-500`).
- Name tokens by purpose (`--color-accent-solid`), not hue or place
  (`--color-blue-button`, `--color-sidebar-gray`).
- `accent` = brand. `primary` never means both brand and body text.
- Measure contrast against the background directly behind the element
  (overlays, cards, images included).
- Dark mode gets its own palette; never invert light.
- One theme mechanism: `prefers-color-scheme` **or** a class/attribute, not
  both.
- Gradients declare interpolation: `in oklab` (even brightness), `in oklch`
  (vivid middle, may show undefined hues), `in srgb` (muted midtones).

### Accessibility

- Native elements: `<button>` for actions, `<a href>` for navigation.
- Style `:focus-visible`, not `:focus`; never remove an outline without a
  visible replacement.
- `tabindex` only `0` or `-1`.
- Icon-only buttons get a descriptive `aria-label`. No `aria-hidden="true"`
  on anything focusable.
- `alt` states purpose and content; decorative images `alt=""`.
- Every input: visible `<label>`, correct `type` and `inputmode`.
- Never block paste.
- Forms: submit stays enabled until the request starts; validate on submit;
  `aria-invalid="true"` on bad fields, error linked with
  `aria-describedby`, focus moves to the first invalid field.
- Hit areas ≥`24×24px`; aim `44×44px` touch, `40×40px` desktop; never
  overlapping. Extend with a pseudo-element.
- Decorative glows/gradients: `pointer-events: none`.
- Hover styles inside `@media (hover: hover)` (sticky `:hover` on touch).
- `role="status"` for routine updates; `role="alert"` only for urgent errors.
- Never color alone for state: add icon, label, or underline.

### Layout

- `scroll-margin-top` on anchor targets (≥ sticky header height).
- Space between groups ≥ 2× space within a group (`8px` items → `16px+`
  groups).

### Writing

- Buttons start with a verb: "Save draft", not "OK"/"Yes".
- Confirmations name the outcome: "Delete project" beside "Cancel".
- One next-step label per flow ("Continue" **or** "Next").
- Link text says where it goes; no "click here".
- One capitalization style everywhere; default sentence case.
- Toggles describe the on state: "Send read receipts", not "Disable …".
- Empty states explain what belongs there plus one action to start.
- Address the reader as "you", never "the user".

## Failure modes

- **Polish by restyle:** changing fonts, palette, or brand to "fix" feel.
  Rules here are rendering and behavior details; keep the product's type and
  color choices.
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
- **Claiming a motion fix without watching it:** timing bugs are invisible in
  code review.

## Exit evidence

Building: run the dev server and inspect the changed surface in a browser.
Reviewing: inspect source, then the rendered surface when runnable. Check, as
relevant to the change:

- hover, focus-visible (keyboard Tab), active, disabled, loading, empty,
  error states;
- light and dark themes, including the switch itself;
- motion at 10% speed (DevTools Animations panel), interrupted mid-flight;
- `prefers-reduced-motion: reduce` emulation;
- touch emulation for sticky hover and hit areas;
- narrow viewport with long strings/IDs for wrapping and truncation.

Report what was not checked as **Not verified**, with the reason.

## Output (review mode)

State scope, styling system, and theme mechanism. Then one table, one row per
finding; a systemic issue is one row listing every location:

| Severity | Domain | Location | Fix | Rule |
| --- | --- | --- | --- | --- |
| HIGH | Accessibility | `dialog.tsx:42` | `aria-label="Close dialog"` on icon button | Icon-only buttons need a name |
| MEDIUM | Typography | `Price.tsx:17` | add `tabular-nums` | Changing digits shift layout |
| LOW | Surfaces | `Card.tsx:28` | outer `rounded-2xl` (8+8) | Concentric radii |

- **HIGH:** inaccessible, misleading, unreadable, or repeatedly disruptive.
- **MEDIUM:** noticeable usability or consistency problem.
- **LOW:** isolated polish.

End with **Verification** (exact checks run and observed results) and a
verdict: `Block` if any HIGH remains, `Needs changes` for MEDIUM/LOW only,
`Approve` when nothing actionable remains. No findings → say "No actionable
UI-craft findings", list checks, `Approve`. Never pad to look thorough.
