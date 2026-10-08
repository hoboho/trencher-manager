# 🎨 Reusable Prompt — Glassmorphism UI

> **چیست:** یک پرامپت خودبسنده که می‌توانی در هر پروژهٔ دیگری کپی کنی تا همین
> زبان بصری شیشه‌ای (Glassmorphism) پیاده‌سازی شود.
>
> **نحوهٔ استفاده:** کل محتوای بخش «PROMPT» را کپی کن و به‌عنوان پیام اول به
> ایجنت کدنویس در پروژهٔ مقصد بده.
>
> **نکته:** پرامپت به انگلیسی نوشته شده چون ایجنت‌های کدنویس با دستور انگلیسی
> دقیق‌تر عمل می‌کنند؛ اما الزامات فارسی و RTL صریحاً داخلش آمده است.

---

<!-- ======================= COPY FROM HERE ======================= -->

# PROMPT

You are a senior front-end engineer and visual designer. Your task is to
implement a **glassmorphism design system** in this project.

Implement it faithfully — the visual language below is a precise specification,
not a suggestion — but **adapt it to this project's existing stack**. Do not
introduce a new framework, bundler or build step if the project already has one.

---

## STEP 0 — Reconnaissance (do this first, do not skip)

Before writing any code, inspect the project and **report back** (concise, bullet
list) on:

1. The rendering layer (React / Vue / Svelte / plain DOM / native / other)
2. The styling approach (CSS files / CSS-in-JS / Tailwind / styled-components / other)
3. Any existing theming or dark-mode mechanism
4. Any existing design tokens / variables
5. The i18n approach, and whether RTL languages are needed
6. The component inventory (buttons, cards, modals, nav, forms)
7. Whether the target is mobile, desktop, or both

Then state, in one short paragraph, **how you will map the spec below onto those
conventions**. Only after that, start implementing.

---

## STEP 1 — Design tokens

Create the tokens first, in whatever mechanism the project uses (CSS custom
properties, a theme object, Tailwind config, …). Everything else must reference
these — **no hard-coded colours anywhere else**.

### Primitives

```css
:root {
  --blur: 22px;
  --blur-strong: 34px;
  --radius-xl: 28px;
  --radius-lg: 22px;
  --radius-md: 16px;
  --radius-sm: 12px;
  --sat: 165%;                                    /* saturation boost inside glass */
  --ease: cubic-bezier(0.22, 1, 0.36, 1);         /* smooth ease-out, no bounce */
  --spring: cubic-bezier(0.34, 1.56, 0.64, 1);    /* slight overshoot for taps */
  --safe-top: env(safe-area-inset-top, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --tabbar-h: 74px;
}
```

### Light theme

```css
[data-theme='light'] {
  --bg-0: #eef2fb;
  --bg-1: #f7f9ff;
  --blob-1: #6f8bff;
  --blob-2: #b06bff;
  --blob-3: #35d0d6;
  --blob-4: #ff8fb1;

  --glass: rgba(255, 255, 255, 0.55);
  --glass-2: rgba(255, 255, 255, 0.38);
  --glass-border: rgba(255, 255, 255, 0.75);
  --glass-shadow: 0 12px 40px rgba(31, 45, 92, 0.16);

  --text: #101828;
  --text-2: #5b6478;
  --text-3: #8b93a7;

  --primary: #4f6bff;
  --primary-2: #8b5cff;
  --accent: #ff6b9d;
  --success: #12b76a;
  --danger: #f04438;
  --warning: #f79009;
  --income: #12b76a;
  --expense: #f04438;

  --ring: rgba(79, 107, 255, 0.35);
  --input-bg: rgba(255, 255, 255, 0.6);
  --chip: rgba(79, 107, 255, 0.1);
}
```

### Dark theme

```css
[data-theme='dark'] {
  --bg-0: #070a16;
  --bg-1: #0d1224;
  --blob-1: #3b56ff;
  --blob-2: #8b3bff;
  --blob-3: #12b6c9;
  --blob-4: #ff4f8b;

  --glass: rgba(24, 30, 54, 0.55);
  --glass-2: rgba(30, 38, 66, 0.35);
  --glass-border: rgba(255, 255, 255, 0.12);
  --glass-shadow: 0 16px 48px rgba(0, 0, 0, 0.55);

  --text: #f4f6ff;
  --text-2: #a7b0cc;
  --text-3: #6f7896;

  --primary: #6d8bff;
  --primary-2: #a97bff;
  --accent: #ff7fb0;
  --success: #2ee59d;
  --danger: #ff6b6b;
  --warning: #ffb020;
  --income: #2ee59d;
  --expense: #ff6b6b;

  --ring: rgba(109, 139, 255, 0.45);
  --input-bg: rgba(255, 255, 255, 0.06);
  --chip: rgba(109, 139, 255, 0.16);
}
```

**If the project has a brand colour**, keep the neutral/glass values and swap only
`--primary` / `--primary-2`, then re-derive `--ring` as the primary colour at
~35% alpha (light) / ~45% alpha (dark).

Default to the **dark** theme unless the OS explicitly prefers light.
Persist the user's choice.

---

## STEP 2 — Animated aurora background

A fixed, full-viewport layer that every glass surface blurs against. **This is
what makes the glass read as glass** — without something colourful behind it,
`backdrop-filter` looks like flat grey.

```css
#bg {
  position: fixed; inset: 0; z-index: 0; overflow: hidden;
  background: linear-gradient(160deg, var(--bg-0), var(--bg-1));
}
.blob {
  position: absolute; border-radius: 50%;
  filter: blur(70px);
  opacity: .55;
  will-change: transform;
  animation: drift 22s var(--ease) infinite alternate;
}
[data-theme='light'] .blob { opacity: .45; filter: blur(80px); }

.b1 { width: 60vw; height: 60vw; background: var(--blob-1); top: -18vw; left: -12vw;  animation-duration: 19s; }
.b2 { width: 52vw; height: 52vw; background: var(--blob-2); top: 22vh;  right: -16vw; animation-duration: 24s; animation-delay: -6s; }
.b3 { width: 46vw; height: 46vw; background: var(--blob-3); bottom: -14vw; left: 8vw; animation-duration: 27s; animation-delay: -12s; }
.b4 { width: 40vw; height: 40vw; background: var(--blob-4); bottom: 18vh;  right: 6vw; animation-duration: 21s; animation-delay: -3s; }

@keyframes drift {
  0%   { transform: translate3d(0, 0, 0) scale(1); }
  50%  { transform: translate3d(4vw, -5vh, 0) scale(1.12); }
  100% { transform: translate3d(-5vw, 6vh, 0) scale(0.94); }
}
```

Add a very subtle noise overlay on top of the blobs for a premium frosted feel
(an SVG `feTurbulence` data-URI at ~3.5% opacity works well).

**Rules**
- Negative `animation-delay` values desynchronise the blobs so the motion never
  looks mechanical.
- Only `transform` is animated — never `width`/`top`/`filter`.
- The blobs must be **behind** all content (`z-index: 0`), with the app shell at
  `z-index: 1`.

---

## STEP 3 — The glass primitive

Two reusable classes. **Every** card, bar and sheet must use one of them — never
hand-roll the recipe.

```css
.glass {
  background: var(--glass);
  backdrop-filter: blur(var(--blur)) saturate(var(--sat));
  -webkit-backdrop-filter: blur(var(--blur)) saturate(var(--sat));   /* required for Safari/iOS */
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.glass-soft {                      /* for large surfaces: bars, sheets */
  background: var(--glass-2);
  backdrop-filter: blur(var(--blur-strong)) saturate(var(--sat));
  -webkit-backdrop-filter: blur(var(--blur-strong)) saturate(var(--sat));
  border: 1px solid var(--glass-border);
}
```

**Why each property matters — do not drop any of them:**

| Property | Purpose |
| --- | --- |
| `backdrop-filter: blur()` | the frost itself |
| `saturate(165%)` | stops glass looking grey/washed out |
| translucent `background` | lets the aurora tint the surface |
| `1px` light `border` | simulates the lit edge of real glass |
| soft, large-radius `box-shadow` | lifts the surface off the background |

---

## STEP 4 — Typography

- Base font: the project's existing font. If none, or if Persian/Arabic is
  needed, use **Vazirmatn** (weights 400/500/600/700/800), bundled locally —
  never a CDN, the app must work offline.
- Fallback stack: `'Vazirmatn', 'Inter', system-ui, -apple-system, sans-serif`.
- Weight discipline: body `500`, labels `600`–`700`, headings `700`–`800`.
- Tighten headings: `letter-spacing: -0.2px` … `-1px` as size grows.
- Muted text uses `--text-2` / `--text-3`; never pure grey.

---

## STEP 5 — Motion

| Token | Value | Use |
| --- | --- | --- |
| `--ease` | `cubic-bezier(0.22, 1, 0.36, 1)` | entrances, colour fades, anything calm |
| `--spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | press feedback, toggles, pops |

### Rules

- **Press feedback is mandatory** on every interactive element:
  `transform: scale(0.97)` for cards, `scale(0.88)` for icon buttons, `scale(0.92)`
  for tabs. This is what makes the UI feel physical.
- **Screen entrance:** `opacity 0 → 1` + `translateY(16px → 0)` over `.45s --ease`.
- **Staggered lists:** apply the same entrance with `nth-child` delays of
  `0.04s, 0.09s, 0.14s, 0.19s, 0.24s, 0.29s`, then cap at `0.33s` for the rest.
- **Bottom sheet:** `translateY(100% → 0)` over `.42s --ease` on open.
- Durations: `0.25s`–`0.35s` for micro-interactions, `0.45s`–`0.6s` for entrances.
- Never animate `box-shadow`, `filter` or `backdrop-filter` — they are very
  expensive. Animate `transform` and `opacity` only.

---

## STEP 6 — Component specification

Reproduce these. Adapt markup to the framework; keep the visual result identical.

### App bar
Pill-shaped glass bar, inset from the screen edges.
`margin-top: calc(safe-top + 10px)`, side margin `14px`, `padding: 12px 16px`,
`border-radius: var(--radius-lg)`. Contains: brand block (icon tile + title +
subtitle), flexible spacer, then up to 2 icon buttons (`40×40`, radius `13px`).
The brand icon tile is `38×38`, radius `12px`, filled with a
`linear-gradient(135deg, var(--primary), var(--primary-2))` and a `--ring` glow.

### Bottom tab bar
Floating glass pill, **not** edge-to-edge:
`left/right: 12px`, `bottom: calc(safe-bottom + 10px)`, height `74px`,
`border-radius: var(--radius-xl)`. 5 items max, each with icon above a `10.5px`
label. The active tab: colour `--primary`, icon `translateY(-2px) scale(1.16)`,
and a soft `--chip` pill behind it that pops in with `--spring`.

### Floating action button
`58×58`, `border-radius: 20px`, gradient fill, `box-shadow` using `--ring`.
Positioned above the tab bar: `bottom: calc(tabbar-h + safe-bottom + 24px)`.
On press: `scale(0.88) rotate(90deg)`.

### Cards
`border-radius: var(--radius-lg)`, `padding: 16px`. Always use the `.glass`
recipe. Structure:
- header row: `46×46` icon tile (radius `15px`) + title (`15.5px/700`) + subtitle
  (`12.5px`, `--text-3`) + optional status badge
- body rows: label/value pairs, label in `--text-3` at `500`, value at `700`
- action row: 1–2 ghost buttons, `padding: 10px`, radius `11px`; destructive one
  tinted `--danger`

### Hero card
The one loud surface. Gradient fill (primary → primary-2 → accent), radius
`var(--radius-xl)`, padding `22px`, a soft white radial highlight overlay, and an
oversized translucent circle bleeding off the bottom-right corner. Headline value
at `33px/800`, `letter-spacing: -1px`, in white. Below it, translucent
`rgba(255,255,255,.2)` pills with a `1px` white border.

### Stat tiles
2-column grid, `12px` gap, radius `var(--radius-lg)`, padding `16px`.
`40×40` icon tile on a `--chip` background, value at `22px/800`, label at
`12px/600` in `--text-3`.

### Badges
Pill, `11px/700`, `padding: 5px 11px`. Always
`background: <colour at 15% alpha>`, `color: <colour>`, `border: 1px solid <colour at 30%>`.
One badge style per semantic state (active / completed / paused / cancelled /
income / expense).

### Progress bar
Track height `7px`, radius `10px`, `background: var(--input-bg)`. Fill is a
`linear-gradient(90deg, var(--primary), var(--primary-2))` with
`transition: width .8s var(--ease)` so it animates on data load.

### Bottom sheet (modal)
Full-screen scrim at `rgba(6,10,25,.5)` with `backdrop-filter: blur(6px)`.
Sheet: full width, max-height `92%`, radius `var(--radius-xl)` on top corners
only, padding `10px 18px calc(safe-bottom + 22px)`, `.glass` recipe, sliding up.
A `42×5` grabber at the top. Tapping the scrim closes it.

### Inputs
Padding `13px 14px`, radius `var(--radius-sm)`, `background: var(--input-bg)`,
`border: 1px solid var(--glass-border)`. On focus:
`border-color: var(--primary)` + `box-shadow: 0 0 0 3px var(--ring)`.
Placeholder in `--text-3`. Remove the native `select` arrow (`appearance: none`).

### Segmented control
Wrapper: `padding: 5px`, radius `14px`, `--input-bg` background.
Each segment: `padding: 10px`, radius `10px`, `13px/700`, `--text-3`.
Active segment: gradient fill, white text, `--ring` glow.

### Toggle switch
`50×29` track, radius `20px`. Knob `22×22`, animated with `--spring`.
On: gradient track, white knob.

### Toast
Centred above the tab bar, radius `16px`, `.glass` recipe, max-width `88vw`.
Animates in with `opacity` + `translateY(26px → 0)` using `--spring`.
Tint the text for success (`--success`) / error (`--danger`).

### Filter chips
Horizontal scrolling row, no scrollbar. Pill, `padding: 8px 15px`, radius `20px`,
`12.5px/700`. Active: gradient fill, white text, `--ring` glow.

### Empty state
Centred, generous vertical padding (`~54px`). Large icon at ~46px / 55% opacity,
a `15px/700` title in `--text-2`, then a `12.5px` hint in `--text-3`.

### Loading skeleton
Block radius `var(--radius-lg)`, height `~96px`, filled with a moving gradient:
`linear-gradient(100deg, var(--input-bg) 30%, var(--chip) 50%, var(--input-bg) 70%)`
with `background-size: 220% 100%` and a `1.3s` shimmer. Use these instead of a
spinner for list content.

---

## STEP 7 — Layout pattern (mobile-first)

```
┌──────────────────────────────┐
│  ╭─ app bar (glass pill) ─╮  │  sticky, inset 14px
│  ╰────────────────────────╯  │
│                              │
│   scrollable content         │  padding 16px 14px
│   (padding-bottom reserves   │  + tabbar height + safe-area
│    room for the tab bar)     │  + 22px
│                        ╭──╮  │
│                        │＋│  │  FAB, floats above tab bar
│  ╭─ tab bar (glass) ────╯──╯  │
│  ╰────────────────────────╯  │  fixed, inset 12px
└──────────────────────────────┘
```

- The content area is the only scrolling region; hide its scrollbar.
- Reserve bottom padding = `tabbar-h + safe-bottom + 22px` so the last card is
  never hidden behind the tab bar.
- Screens are switched by toggling visibility, not by remounting the whole tree.
  Re-render a screen only when its data is stale.

---

## STEP 8 — RTL and localisation

- Drive direction from the active language: `document.documentElement.dir = 'rtl' | 'ltr'`,
  and set `lang` accordingly.
- **Prefer CSS logical properties** — `margin-inline`, `padding-inline-start`,
  `inset-inline-start` — so most of the layout mirrors automatically.
- For the few places that cannot be logical, key off `html[dir='rtl']`.
  The known ones in this design:
  - the FAB moves from the right edge to the left edge
  - the search icon moves from the left inset to the right inset
  - the toggle-switch knob travels in the opposite direction
- **Mirror the whole layout, not the text flow only.** A glass design that is
  half-flipped looks broken.
- Format numbers and currency per locale (Persian digits, thousand separators,
  and `هزار / میلیون / میلیارد` for compact money).
- Every user-facing string must exist in **all** supported languages. A missing
  key must degrade to a visible placeholder, never to `undefined`.

---

## STEP 9 — Quality gates

These are **acceptance criteria**, not suggestions.

### Accessibility
- [ ] Body text meets WCAG AA contrast against the glass surface, in **both**
      themes. Glass lowers contrast — check it, do not assume.
- [ ] Interactive targets are at least `40×40`.
- [ ] Visible focus rings on inputs and buttons (`--ring`).
- [ ] Semantic elements: real `<button>`, `<nav>`, labels tied to inputs.
- [ ] Honour `prefers-reduced-motion: reduce` by collapsing all animation and
      transition durations to ~`0.001ms`.

### Performance
- [ ] `backdrop-filter` is expensive: keep the number of simultaneously visible
      glass layers low (roughly ≤ 10).
- [ ] Blur radius stays ≤ ~35px — large radii on large surfaces are the main
      cause of jank on mid-range Android.
- [ ] Animate `transform`/`opacity` only.
- [ ] Add `will-change: transform` to the animated blobs, and nothing else.
- [ ] Test on a real mid-range device, not just a desktop browser — Android
      WebView is the worst case for `backdrop-filter`.

### Resilience
- [ ] Provide a fallback if `backdrop-filter` is unsupported
      (`@supports not (backdrop-filter: blur(1px))` → raise the background alpha
      so the surface stays legible, e.g. `0.86`).
- [ ] All layout maths involving safe areas must have a `0px` default.
- [ ] Escape all user-supplied values before interpolating them into markup.
- [ ] Persist the theme and language choice across restarts.

---

## STEP 10 — Pitfalls (learned the hard way — do not repeat)

1. **Glass with nothing behind it is just grey.** The aurora layer is not
   decoration; it is what makes the effect work. Build it first.
2. **`-webkit-backdrop-filter` is required.** Without it the glass silently
   renders flat on iOS and on older Android WebViews.
3. **Don't skip the `saturate()`.** `blur()` alone desaturates whatever is
   behind it, so the result looks muddy.
4. **Don't nest glass inside glass.** Stacking `backdrop-filter` compounds the
   blur and tanks performance; keep it to one glass layer per visual plane.
5. **A `1px` translucent border is not optional.** It is the single cheapest
   trick that makes a surface read as glass rather than as a translucent box.
6. **Watch RTL regressions.** Use logical properties from the start; retrofitting
   them later is painful.
7. **Don't animate layout properties.** Animating `width`, `top` or `filter`
   causes reflow — animate `transform`/`opacity`.
8. **Don't guard DOM calls behind things that may not exist.** Feature-detect
   (for example `typeof el.scrollTo === 'function'`) and fall back, rather than
   assuming a method exists.
9. **A `user-scalable=no` viewport with a keyboard open can trap users.**
   Prefer `viewport-fit=cover` and let the sheet scroll.
10. **Test the empty state.** Most of this design is data-driven; make sure
    empty lists, zero values and missing optional fields still look intentional.

---

## STEP 11 — Deliverable

When you are done, report:

1. Which files you created or changed, and why.
2. The exact command to run the app.
3. How to toggle light/dark, and how to switch language / direction.
4. A short list of anything in the spec you could **not** implement and the
   reason.
5. Screenshots or a description of each screen at mobile width.

Do it incrementally: tokens → aurora background → glass primitive → app bar and
navigation → one representative screen. **Stop and check in after the first
screen renders correctly**, then continue with the rest.

<!-- ======================== COPY TO HERE ======================== -->

---

## 📌 یادداشت‌های استفاده

### چه چیزی را باید در پرامپت شخصی‌سازی کنی؟

| جای پرامپت | چه بنویسی |
| --- | --- |
| STEP 0 | کاری نکن — عمداً گذاشته شده تا ایجنت اول پروژه را بشناسد |
| STEP 1 | اگر برند رنگ دارید، فقط `--primary` و `--primary-2` را عوض کن |
| STEP 4 | فونت پروژه؛ اگر فارسی لازم نیست، وزیرمتن را حذف کن |
| STEP 6 | اگر صفحهٔ خاصی دارید، نمونه‌اش را به فهرست اضافه کن |
| STEP 11 | مراحل تحویل را به سلیقهٔ خودت تنظیم کن |

### اگر پروژه دسکتاپ است

- `--tabbar-h` و `safe-area` را حذف کن
- تب‌بار پایین را به سایدبار عمودی یا نوار کناری تبدیل کن
- پدینگ محتوا را بیشتر کن (حداقل `24px`)
- عرض کارت‌ها را محدود کن (`max-width: 1100px`) و مرکزچین کن

### اگر پروژه وب است (نه موبایل)

- `user-select: none` را حذف کن
- `overflow: hidden` روی `body` را بردار تا اسکرول طبیعی بماند
- `100dvh` را جای `100%` بگذار

### تلهٔ اصلی

اگر پشت سطوح شیشه‌ای **چیز رنگی نباشد**، طرح خاکستری و مرده می‌شود.
پس همیشه **اول لایهٔ aurora** را بساز، بعد شیشه.

---

## 🔗 منبع

این پرامپت از پیاده‌سازی واقعی در همین مخزن استخراج شده است:

| فایل | محتوا |
| --- | --- |
| [`src/styles.css`](src/styles.css) | سیستم طراحی کامل |
| [`src/main.js`](src/main.js) | پوستهٔ اپ، مسیریابی، تب‌بار، FAB |
| [`src/screens/`](src/screens) | نمونهٔ هر الگوی صفحه |
| [`src/core/ui.js`](src/core/ui.js) | toast، شیت، confirm |

برای دیدن نتیجه: APK در [آخرین ریلیز](https://github.com/hoboho/trencher-manager/releases/latest).
