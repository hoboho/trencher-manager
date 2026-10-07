# Terencher — Mobile (Android)

An Android app for the **Terencher** trenching-management system, rebuilt from the
original PyQt6 desktop application.

- 🦀 **Rust** core (SQLite persistence, domain logic) — same data model as the desktop app
- 📱 **Tauri 2** shell producing a real Android APK
- 🎨 **Glassmorphism** UI: animated aurora background, frosted-glass surfaces, spring motion
- 🌐 **Persian / English** with automatic RTL↔LTR switching
- 🌙 **Dark / light** themes
- 🔌 Fully **offline** — bundled fonts, no network calls

---

## Screens

| Screen | Parity with desktop |
| --- | --- |
| **Dashboard** | Net profit hero, project/machine/operator counters, recent projects |
| **Projects** | Full CRUD, financial progress bar, status filters, search |
| **Machines** | Full CRUD incl. fuel, maintenance, trenching depth/width, speed, weight |
| **Operators** | Full CRUD incl. hourly + overtime rates and threshold |
| **Finance** | Income/expense ledger, categories, balance summary, project linking |
| **Reports** | Status breakdown, expense-by-category, top projects, CSV export |
| **Settings** | Language, theme, version, storage info |

---

## Architecture

```
mobile/
├── src/                        # Frontend (vanilla ES modules, no bundler needed)
│   ├── index.html
│   ├── styles.css              # Glassmorphism design system
│   ├── main.js                 # App shell: routing, tab bar, FAB, sheet
│   ├── core/
│   │   ├── api.js              # Tauri invoke bridge + localStorage fallback
│   │   ├── form.js             # Declarative bottom-sheet form builder
│   │   ├── format.js           # Persian digits, currency, dates
│   │   ├── i18n.js             # fa/en dictionaries + direction handling
│   │   └── ui.js               # DOM helpers, toast, sheet, confirm
│   ├── locales/                # fa.js, en.js
│   ├── screens/                # One module per screen
│   └── assets/fonts/           # Vazirmatn woff2 (bundled for offline use)
│
├── rust/terencher-core/        # 🦀 Framework-free domain + persistence crate
│   ├── src/models.rs           # Serde structs mirroring the desktop SQLAlchemy models
│   ├── src/db.rs               # Schema + typed CRUD + dashboard aggregation
│   └── tests/db_test.rs        # Integration tests (in-memory SQLite)
│
├── src-tauri/                  # Tauri Android shell
│   └── src/
│       ├── lib.rs              # Builder, plugin setup, DB path resolution
│       ├── commands.rs         # #[tauri::command] wrappers over terencher-core
│       └── main.rs
│
└── test/smoke.mjs              # Headless jsdom UI test (40 assertions)
```

The Rust core is deliberately **free of any framework dependency**, so it can be
unit-tested on the host machine without the Android toolchain and reused by a
future iOS or desktop build.

---

## Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| Node.js | ≥ 18 | frontend tooling |
| Rust | stable | with Android targets |
| JDK | 17 | required by Gradle |
| Android SDK | API 34 | `platform-tools`, `platforms;android-34`, `build-tools;34.0.0` |
| Android NDK | 26.1.10909125 | Rust cross-compilation |
| `ANDROID_HOME` / `NDK_HOME` | — | must be exported |

Install the Rust Android targets:

```bash
rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android
```

---

## Quick start

```bash
cd mobile
npm install
```

### Run the tests (no Android toolchain needed)

```bash
npm run test:all     # Rust core tests + headless UI smoke test
npm run test:rust    # 4 Rust integration tests
npm run test         # 40 jsdom UI assertions
```

### Build the Android app

```bash
npm run android:init    # one-off: generates the Gradle project under src-tauri/gen/android
npm run android:dev     # run on a connected device / emulator
npm run android:apk     # produce a debug APK
npm run android:build   # produce a signed release bundle
```

The APK lands in:

```
src-tauri/gen/android/app/build/outputs/apk/universal/release/app-universal-release.apk
```

Install it with `adb install -r <path-to-apk>`.

---

## Data storage

On device the SQLite database lives in the app's private data directory
(`app_data_dir()/terencher.db`), resolved at runtime — no storage permissions
required. Writes use WAL mode.

When the frontend runs in a plain browser (`api.js` detects the missing Tauri
bridge) it transparently falls back to a `localStorage` store that mirrors the
same command contract, which is what the smoke test exercises.

---

## Adding a screen

1. Create `src/screens/<name>.js` exporting `render(host)`, `meta`, and
   optionally `load()` and `onFab()`.
2. Register it in `main.js` — add to `TABS` (bottom bar) or `EXTRA` (appbar).

## Adding a field

Entity forms are declarative — append a descriptor to the `FIELDS` array in the
relevant screen:

```js
{ key: 'new_field', label: 'machines.newField', type: 'number', required: true }
```

Then add the column in `rust/terencher-core/src/db.rs` (schema + CRUD) and the
matching field on the struct in `models.rs`.

## License

MIT — see [`../LICENSE`](../LICENSE).