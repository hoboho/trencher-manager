---
name: glassmorphism-ui
description: Redesign an existing UI with a glassmorphism (frosted-glass) look derived from the project's own colours. Use when the user asks to make an interface glassy, add frosted glass, blur or translucency, apply glassmorphism, modernise a UI, or port a glass design system into another project. Covers deriving tokens from existing colours, the aurora background, the glass recipe, motion, RTL and accessibility/performance gates.
license: MIT
compatibility: Any stack able to edit CSS and markup. No network access required.
metadata:
  author: hoboho/trencher-manager
  version: "1.0"
---

# Glassmorphism UI

Turn a project's existing UI into a frosted-glass design, **built from the colours
it already has**. Never import a new palette, framework or build step.

## 1. Recon — report before coding

Inspect and reply with: stack · styling method · theme mechanism · existing
colours/tokens · i18n and RTL need · target (mobile / desktop / web).
Then state in 2–3 lines how you will map this skill onto it. Only then start.

## 2. Derive tokens from the existing colours

Do **not** invent a palette. Map what exists:

| Token | Derive from |
| --- | --- |
| `--primary` | the project's brand / accent colour |
| `--primary-2` | same hue, lighter or shifted — for gradients |
| `--bg-0`, `--bg-1` | page background, darkest → lightest |
| `--blob-1..4` | 3–4 **saturated** hues: brand + analogous + one contrasting |
| `--text`, `--text-2`, `--text-3` | text, secondary, muted |
| `--glass` | surface colour at ~55% alpha |
| `--glass-2` | same at ~35% alpha — bars and sheets |
| `--glass-border` | white 75% (light) · white 12% (dark) |
| `--glass-shadow` | `0 12px 40px` tint 16% · `0 16px 48px` black 55% |
| `--ring` | `--primary` at 35% alpha (light) · 45% (dark) |
| `--blur`, `--blur-strong` | `22px` · `34px` |
| `--radius-sm..xl` | `12px` · `16px` · `22px` · `28px` |
| `--ease`, `--spring` | `cubic-bezier(.22,1,.36,1)` · `cubic-bezier(.34,1.56,.64,1)` |

If there is only one theme, keep it and derive the other. Keep the existing
theme-switch mechanism and persistence.

## 3. Aurora background — build this FIRST

Glass is only visible against something colourful. A fixed full-viewport layer
behind everything, with 3–4 large blurred drifting blobs:

```css
#bg { position: fixed; inset: 0; z-index: 0; overflow: hidden;
      background: linear-gradient(160deg, var(--bg-0), var(--bg-1)); }
.blob { position: absolute; border-radius: 50%; filter: blur(70px);
        opacity: .55; will-change: transform;
        animation: drift 22s var(--ease) infinite alternate; }

@keyframes drift {
  0%   { transform: translate3d(0,0,0) scale(1); }
  50%  { transform: translate3d(4vw,-5vh,0) scale(1.12); }
  100% { transform: translate3d(-5vw,6vh,0) scale(.94); }
}
```

Give each blob a different `--blob-*` colour, a size of `40–60vw`, a position
bleeding off the edges, and a duration of `19–27s` with a **negative**
`animation-delay` so they never sync. Animate `transform` only. Add an SVG
`feTurbulence` noise overlay at ~3.5% opacity for a premium frosted feel.

## 4. The glass recipe — use everywhere

```css
.glass {                                /* cards, tiles */
  background: var(--glass);
  backdrop-filter: blur(var(--blur)) saturate(165%);
  -webkit-backdrop-filter: blur(var(--blur)) saturate(165%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}
.glass-soft {                           /* bars, sheets, modals */
  background: var(--glass-2);
  backdrop-filter: blur(var(--blur-strong)) saturate(165%);
  -webkit-backdrop-filter: blur(var(--blur-strong)) saturate(165%);
  border: 1px solid var(--glass-border);
}
```

All five properties are load-bearing: `blur` frosts · `saturate(165%)` stops it
looking grey · the translucent background lets the aurora tint it · the `1px`
border is the lit edge that reads as glass · the soft shadow lifts it off the
page. Never hand-roll the recipe.

## 5. Motion

- Press feedback **everywhere**: cards `scale(.97)`, icon buttons `scale(.88)`, tabs `scale(.92)`.
- Entrances: `opacity 0→1` + `translateY(16px→0)` over `.45s var(--ease)`.
- Lists stagger by `nth-child` in `.04s` steps, capped at `.33s`.
- Overlays slide `translateY(100%→0)` over `.42s`.
- **Never** animate `filter`, `box-shadow` or `backdrop-filter` — only `transform` and `opacity`.

## 6. Apply to the components already present

For every existing nav bar, card, modal, input, button, chip, toast, list row,
empty state and loading state:

- use `.glass` / `.glass-soft`, never hand-roll
- radius `12–28px`, padding `14–22px`
- active/selected state = gradient fill (`--primary → --primary-2`) + `--ring` glow
- inputs: translucent background; on focus `border-color: var(--primary)` and `box-shadow: 0 0 0 3px var(--ring)`
- lists: use a shimmering skeleton block, not a spinner
- text hierarchy from `--text` / `--text-2` / `--text-3`, never raw grey

## 7. RTL and locale

Use **logical properties** (`margin-inline`, `padding-inline-start`,
`inset-inline-start`) so the layout mirrors automatically. Key off `html[dir=rtl]`
only for the floating action button, icon insets and toggle knobs. Mirror the
**whole** layout, not just the text. Format numbers, dates and currency per locale.

## 8. Gates

- Text passes WCAG AA against the glass in **both** themes — glass lowers contrast, verify it.
- Interactive targets ≥ `40px`; visible focus rings; real `<button>` / `<nav>` elements.
- Honour `prefers-reduced-motion` — collapse durations to ~`0.001ms`.
- `@supports not (backdrop-filter: blur(1px))` → raise the background alpha to ~`0.86` so surfaces stay legible.
- Keep ≤ ~10 visible glass layers; blur ≤ `35px`; test on a real mid-range device.
- Escape user data before it enters markup.

## 9. Pitfalls

1. Glass over a flat background is just grey — the aurora is not optional.
2. `-webkit-backdrop-filter` is required, or iOS and older Android render it flat.
3. Do not nest glass inside glass — the blur compounds and it janks.
4. Do not drop `saturate()` or the `1px` border; both are what sell the effect.
5. Do not animate `width`, `top` or `filter` — they cause reflow.
6. Feature-detect DOM methods (`typeof el.scrollTo === 'function'`) instead of assuming.
7. Check empty states, zero values and missing fields — most UI is data-driven.

## 10. Deliver

Report: files changed · the run command · how to toggle theme and direction ·
anything you could not implement and why · a description of each screen.

Work incrementally: tokens → aurora → glass primitive → navigation → **one
screen, then stop and check in**, then the rest.
