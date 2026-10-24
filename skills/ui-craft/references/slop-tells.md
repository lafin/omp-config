# Generated-looking tells: detection signals

Load from `SKILL.md` when reviewing a whole page or when the UI "looks
generic". Each row: the tell, a source or render signal to search for, and the
fix. A signal is a lead, not a verdict: confirm in the render, and skip any
tell the project's documented design system chose on purpose. Thresholds are
restated from the impeccable detector registry and Hallmark's sloplint gates.

## Surfaces and color

| Tell | Signal | Fix |
| --- | --- | --- |
| Side stripe | `border-left`/`border-right` ≥`3px` (≥`2px` with radius) in an accent color on a card, alert, list item; Tailwind `border-l-4`+ | Remove, or full 1px border / tinted background for state |
| Thick border on rounded card | accent `border` ≥`3px` plus `border-radius` | Ring shadow or no border |
| Gradient text | `background-clip: text` (`bg-clip-text`) with a gradient + transparent fill | Solid text token; emphasis via weight or size |
| AI palette | purple/violet gradient (`from-purple`, `from-violet`, `to-indigo`), cyan text on near-black | One tonal ramp from the brand hue |
| Glow / halo | zero-offset colored `box-shadow`/`text-shadow`; colored blurred shadow on dark; saturated `radial-gradient(… transparent)` behind a hero | Neutral offset shadow or none |
| Ghost card row | every card in a row has a 1px border **and** a wide soft shadow | Pick one elevation |
| Nested cards | bordered/shadowed box whose ancestor is also a card | Flatten; space and dividers inside |
| Hard offset shadow | unblurred shadow offset ≥`4px` (`4px 4px 0`) | Blur it, unless the system is neobrutalist |
| Decorative pattern | `repeating-linear-gradient` stripes; two-axis hairline `linear-gradient` grid tiled at a fixed cell; `feTurbulence` grain | Plain surface unless a real canvas/map/blueprint sits under it |
| Gray on color | neutral-gray text token on a saturated background | Text derived from the surface hue, or near-white |
| Gradient overreach | gradient with >3 stops | ≤3 stops, declared interpolation |

## Layout and structure

| Tell | Signal | Fix |
| --- | --- | --- |
| Icon-tile feature grid | ≥3 equal siblings each = rounded-square icon container + heading + paragraph | Fewer, unequal items; icon inline beside heading; or a real product sample |
| Eyebrow / kicker | short `uppercase` + `letter-spacing` > `0.03em` block (or pill chip) directly above an `h1`/`h2` | Delete; the heading carries itself |
| Section numbers | `01`/`02`/`03` labels beside consecutive headings | Remove unless order is the information |
| Hero metric template | big number + small label + supporting stat row, numbers not supplied | Remove, or real data with source |
| Monotonous spacing | ≥10 spacing values, one value >60% of them, ≤3 distinct | Tight within groups, wide between |
| Content hidden at rest | large share of text at `opacity: 0`/`visibility: hidden` after scripts run | Visible by default; animate from visible |
| Clipped popover | `overflow: hidden` ancestor wrapping an absolutely positioned menu/tooltip | Visible overflow, `overflow-x: clip`, or top-layer popover |
| Cramped padding | text <`8px` from its bordered container edge | Padding from the spacing scale |
| Text at viewport edge | body text <`16px` from the viewport edge (<`12px` at ≤`480px`) | Container gutter |

## Typography

| Tell | Signal | Fix |
| --- | --- | --- |
| Flat hierarchy | heading/body size ratio <`1.25` at every step | One stronger step |
| Extreme tracking | `letter-spacing` < `-0.04em` | `-0.02em` to `-0.03em` |
| Tight leading | `line-height` < `1.3` on multi-line text | `1.5–1.65` body |
| Wide tracking | `letter-spacing` > `0.05em` on body | Normal tracking; wide only on short labels |
| Tiny text | running text <`12px`; interactive text <`11px` | ≥`16px` body, ≥`12px` meta |
| All-caps body | ≥80 characters uppercase in a run | Sentence case |
| Long line | rendered lines >~`80` characters | `max-width: 65ch` |
| Narrow justified | `text-align: justify` without `hyphens: auto` | Left-align |
| Skipped heading | `h1` → `h3` with no `h2` | Step one level at a time |
| Accented word | one `<em>`/`<span>` with italic or accent color inside a headline | One weight, style, color per heading |
| Mono costume | monospace on marketing prose or headings | Mono only for code, data, measurements |

## Motion

| Tell | Signal | Fix |
| --- | --- | --- |
| Bounce | `animate-bounce`; `cubic-bezier` with a y value >1 or <0 on UI state | Ease-out curve |
| `transition: all` | `transition: all`, `transition-all` | Name properties |
| Layout animation | transitions on `width`, `height`, `top`, `left`, `margin` | `transform`, `grid-template-rows` |
| Decorative loop | `animate-pulse`/`animate-ping` on a status dot; infinite `blink` caret outside an input; marquee without pause | Static indicator; pause control |
| Same reveal everywhere | identical fade-up on every section | One authored entrance or none |

## Copy

| Tell | Signal | Fix |
| --- | --- | --- |
| Buzzwords | `/\b(seamless(ly)?|unlock|elevate|empower|supercharge|streamline your|world-class|best-in-class|cutting-edge|next-generation|game-changer|revolutioni[sz]e)\b/i` | The literal verb and noun of what it does |
| Rebuttal cadence | ≥3 sections ending "Not X. Y." / "X. No Y." / "It's not just X, it's Y" | Plain statement once |
| Em-dash saturation | ≥8 em dashes at ~1 per 500 characters of body | Commas, colons, full stops |
| Invented proof | testimonials, logos, counts, ratings the user never supplied | Remove or visible placeholder |
| Fake success | form handler shows "Thanks!" without sending | Say nothing was sent; wire the endpoint |
| Emoji icons | emoji or `★ ✓ →` glyphs as feature/list icons | One SVG icon set |
| Broken image | `<img>` with empty, missing, or placeholder `src` | Real asset or remove |
