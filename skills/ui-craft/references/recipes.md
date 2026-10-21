# UI Craft recipes

Load when writing or proposing a fix from `SKILL.md`. Translate each recipe
into the project's styling system; Tailwind forms are shown where they differ.

## Layered shadow instead of a border

```css
:root {
  --shadow-border:
    0 0 0 1px oklch(0 0 0 / 0.06),
    0 1px 2px -1px oklch(0 0 0 / 0.06),
    0 2px 4px 0 oklch(0 0 0 / 0.04);
  --shadow-border-hover:
    0 0 0 1px oklch(0 0 0 / 0.08),
    0 1px 2px -1px oklch(0 0 0 / 0.08),
    0 2px 4px 0 oklch(0 0 0 / 0.06);
}
/* Dark: depth layers are invisible, keep the ring only. Use the project's theme selector. */
.dark {
  --shadow-border: 0 0 0 1px oklch(1 0 0 / 0.08);
  --shadow-border-hover: 0 0 0 1px oklch(1 0 0 / 0.13);
}
.card {
  box-shadow: var(--shadow-border);
  transition: box-shadow 150ms ease-out;
}
@media (hover: hover) {
  .card:hover { box-shadow: var(--shadow-border-hover); }
}
```

## Image outline

```css
img { outline: 1px solid oklch(0 0 0 / 0.08); outline-offset: -1px; }
.dark img { outline-color: oklch(1 0 0 / 0.08); }
```

Tailwind: `outline outline-1 -outline-offset-1 outline-black/8 dark:outline-white/8`.

## Hit area larger than the visible control

```css
.icon-button { position: relative; width: 20px; height: 20px; }
.icon-button::after {
  content: "";
  position: absolute;
  inset: 50% auto auto 50%;
  translate: -50% -50%;
  width: 44px;
  height: 44px;
}
```

Shrink the pseudo-element if it would overlap a neighbouring control.

## Press feedback

```css
.button { transition: scale 200ms ease-out; }
.button:active:not(:disabled) { scale: 0.97; }
```

Tailwind: `transition-transform duration-200 ease-out active:not-disabled:scale-[0.97]`.
Motion: `whileTap={{ scale: 0.97 }}`.

## Icon swap

Motion installed (import from whichever of `motion/react` or `framer-motion`
the project already uses):

```tsx
<AnimatePresence initial={false} mode="popLayout">
  <motion.span
    key={copied ? "check" : "copy"}
    initial={{ opacity: 0, scale: 0.25, filter: "blur(4px)" }}
    animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
    exit={{ opacity: 0, scale: 0.25, filter: "blur(4px)" }}
    transition={{ type: "spring", duration: 0.3, bounce: 0 }}
  >
    {copied ? <CheckIcon /> : <CopyIcon />}
  </motion.span>
</AnimatePresence>
```

No motion library: keep both icons mounted, stack them, toggle a class.

```css
.swap { display: grid; }
.swap > * {
  grid-area: 1 / 1;
  transition: opacity 300ms, scale 300ms, filter 300ms;
  transition-timing-function: cubic-bezier(0.2, 0, 0, 1);
}
.swap > [data-hidden] { opacity: 0; scale: 0.25; filter: blur(4px); }
```

## Menu that animates from its trigger and only on close

```css
.menu {
  transform-origin: var(--radix-dropdown-menu-content-transform-origin, top left);
}
.menu[data-state="closed"] {
  animation: menu-out 150ms ease-out forwards;
}
@keyframes menu-out {
  to { opacity: 0; scale: 0.97; filter: blur(4px); }
}
```

Headless libraries usually expose the trigger-relative origin as a CSS
variable (Radix: `--radix-*-transform-origin`; Floating UI: compute from
`placement`). Use it instead of hard-coding.

## Disable transitions during a theme switch

```js
function setTheme(theme) {
  const style = document.createElement("style");
  style.textContent = "*,*::before,*::after{transition:none!important}";
  document.head.appendChild(style);
  document.documentElement.dataset.theme = theme;
  getComputedStyle(document.body); // force a style flush before re-enabling
  requestAnimationFrame(() => style.remove());
}
```

`next-themes`: `<ThemeProvider disableTransitionOnChange>`.

## Staggered entrance

```css
@media (prefers-reduced-motion: no-preference) {
  .enter {
    animation: enter 600ms cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
    animation-delay: calc(100ms * var(--stagger, 0));
  }
}
@keyframes enter {
  from { opacity: 0; translate: 0 8px; filter: blur(4px); }
}
```

```html
<h1 class="enter" style="--stagger: 0">…</h1>
<p class="enter" style="--stagger: 1">…</p>
<div class="enter" style="--stagger: 2">…actions…</div>
```

## Accessible form errors

```html
<form novalidate>
  <label for="email">Email</label>
  <input id="email" name="email" type="email" inputmode="email"
         autocomplete="email" aria-invalid="true" aria-describedby="email-error">
  <p id="email-error">Enter an email address like name@example.com.</p>
  <button type="submit">Create account</button>
</form>
```

On submit: validate all fields, set `aria-invalid` and the linked message on
each failure, then `firstInvalid.focus()`. Disable the button only while the
request is in flight.

## Typography root

```css
html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
h1, h2, h3 { text-wrap: balance; }
.description { text-wrap: pretty; }
.prose { max-width: 65ch; }
a {
  text-underline-position: from-font;
  text-decoration-skip-ink: auto;
}
.badge { white-space: nowrap; }
.id, .url { overflow-wrap: break-word; }
[id] { scroll-margin-top: calc(var(--header-height, 64px) + 16px); }
```

## Semantic color tokens

```css
:root {
  /* primitives: referenced only by tokens */
  --gray-1: oklch(0.99 0 0);
  --gray-6: oklch(0.88 0 0);
  --gray-12: oklch(0.21 0 0);
  --brand-9: oklch(0.62 0.19 260);

  /* tokens: what components use */
  --color-bg: var(--gray-1);
  --color-border: var(--gray-6);
  --color-text: var(--gray-12);
  --color-accent-solid: var(--brand-9);
}
.dark {
  /* separate dark primitives, not an inversion of the light scale */
  --color-bg: oklch(0.17 0 0);
  --color-border: oklch(0.32 0 0);
  --color-text: oklch(0.95 0 0);
  --color-accent-solid: oklch(0.68 0.17 260);
}
.button-primary { background: var(--color-accent-solid); }
```
