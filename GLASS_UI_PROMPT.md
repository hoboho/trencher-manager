# 🎨 Prompt — هر پروژه‌ای را گلسی کن

> پرامپت مستقل از پروژه و مستقل از رنگ. رنگ‌بندی از خود پروژه گرفته می‌شود.
> کل متن زیر خط را کپی کن و به ایجنت پروژهٔ مقصد بده.

---

# PROMPT — Turn this UI into glassmorphism

Redesign this project's UI with a **glassmorphism** look, built from the
project's **own colours**. Do not import a new palette, framework or build step.

## 1. Recon — report first, then code

Inspect the project and reply with: stack · styling method · existing theme
mechanism · existing colours/tokens · i18n + whether RTL is needed · target
(mobile/desktop/web). Then state in 2–3 lines how you will map the spec below
onto it. Only then start.

## 2. Derive the tokens from the existing colours

Do **not** invent a palette. Read what the project already uses and map it:

| Token | Derive from |
| --- | --- |
| `--primary` | the project's brand / accent colour |
| `--primary-2` | same hue, lighter or hue-shifted — for gradients |
| `--bg-0`, `--bg-1` | page background, darkest → lightest (used as a `160deg` gradient) |
| `--blob-1..4` | 3–4 **saturated** hues: the brand colour + analogous + one contrasting |
| `--text`, `--text-2`, `--text-3` | text, secondary, muted |
| `--glass` | surface colour at ~55% alpha (white in light, near-black in dark) |
| `--glass-2` | same at ~35% alpha — for bars and sheets |
| `--glass-border` | white 75% (light) · white 12% (dark) |
| `--glass-shadow` | `0 12px 40px` shadow-tint 16% (light) · `0 16px 48px` black 55% (dark) |
| `--ring` | `--primary` at 35% alpha (light) · 45% (dark) |
| `--blur` `--blur-strong` | `22px` · `34px` |
| `--radius-sm..xl` | `12px` · `16px` · `22px` · `28px` |
| `--ease` `--spring` | `cubic-bezier(.22,1,.36,1)` · `cubic-bezier(.34,1.56,.64,1)` |

If the project has one theme only, keep it and add the other derived from it.
Keep the existing theme-switch mechanism and persistence.

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

Give each blob a different `--blob-*` colour, size (`40–60vw`), position (bleeding
off the edges) and duration (`19–27s`) with a **negative** `animation-delay` so
they never sync. Animate `transform` only. Add an SVG `feTurbulence` noise
overlay at ~3.5% opacity for a premium frosted feel.

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

Every one of those five properties is load-bearing:
`blur` frosts · `saturate(165%)` stops it looking grey · the translucent
background lets the aurora tint it · the `1px` light border is the lit edge that
reads as glass · the soft shadow lifts it off the page.

## 5. Motion

- Press feedback **everywhere**: cards `scale(.97)`, icon buttons `scale(.88)`, tabs `scale(.92)`.
- Entrances: `opacity 0→1` + `translateY(16px→0)` over `.45s var(--ease)`.
- Lists stagger by `nth-child` at `.04s` steps, capped at `.33s`.
- Overlays slide `translateY(100%→0)` over `.42s`.
- **Never** animate `filter`, `box-shadow` or `backdrop-filter` — only `transform` and `opacity`.

## 6. Apply it to the components already in this project

For each existing nav bar, card, modal, input, button, chip, toast, list row,
empty state and loading state:

- use `.glass` / `.glass-soft` — never hand-roll the recipe
- radius between `12px` and `28px`; padding `14–22px`
- active/selected state = gradient fill (`--primary → --primary-2`) + `--ring` glow
- text hierarchy: value/muted, never raw grey
- inputs: translucent bg, and on focus `border-color: var(--primary)` + `box-shadow: 0 0 0 3px var(--ring)`
- lists: skip the spinner, use a shimmering skeleton block

## 7. RTL and locale

Use **logical properties** (`margin-inline`, `padding-inline-start`,
`inset-inline-start`) so the layout mirrors automatically. Key off `html[dir=rtl]`
only for the FAB, icon insets and the toggle knob. Mirror the **whole** layout,
not just the text. Format numbers/dates/currency per locale.

## 8. Gates

- Text passes WCAG AA against the glass, in **both** themes — glass lowers contrast, verify it.
- Targets ≥ `40px`; visible focus rings; real `<button>`/`<nav>` elements.
- Honour `prefers-reduced-motion` (collapse durations to ~`0.001ms`).
- `@supports not (backdrop-filter: blur(1px))` → raise the alpha to ~`0.86` to stay legible.
- ≤ ~10 visible glass layers; blur ≤ `35px`; test on a real mid-range device.
- Escape user data before it enters markup.

## 9. Pitfalls

1. Glass over a flat background is just grey — the aurora is not optional.
2. `-webkit-backdrop-filter` is required, or iOS/older Android renders it flat.
3. Don't nest glass in glass — the blur compounds and it janks.
4. Don't drop the `saturate()` or the `1px` border; both are what sell the effect.
5. Don't animate `width`/`top`/`filter` — reflow.
6. Feature-detect DOM methods (`typeof el.scrollTo === 'function'`) instead of assuming.
7. Check the empty state, zero values and missing fields — most UI is data-driven.

## 10. Deliver

Report: files changed · run command · how to toggle theme and direction ·
anything you could not implement and why · a description of each screen.

Work incrementally: tokens → aurora → glass primitive → nav → **one screen, then
stop and check in**, then the rest.

---

## 📌 یادداشت فارسی

- **مستقل از رنگ:** پرامپت هیچ پالتی نمی‌دهد؛ ایجنت رنگ‌های پروژهٔ خودت را می‌خواند و از آن‌ها توکن می‌سازد. اگر برند رنگ دارد، همان می‌شود `--primary`.
- **مستقل از فریم‌ورک:** در STEP 1 ایجنت stack را گزارش می‌دهد و بعد معادل‌سازی می‌کند؛ فریم‌ورک و bundler جدید اضافه نمی‌شود.
- **دروغ نگو، اول لایهٔ aurora:** بدون پس‌زمینهٔ رنگی، شیشه خاکستری و مرده می‌شود.
