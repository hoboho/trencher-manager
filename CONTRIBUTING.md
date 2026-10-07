# Contributing to Terencher

Thanks for helping improve the Terencher Android app! 🛠️

## Ways to contribute

- 🐛 Reporting bugs
- 💡 Proposing features
- 📝 Improving the Persian/English translations
- 🎨 Refining the UI
- 🔧 Submitting fixes

## Development setup

```bash
npm install
npm run test:all     # must pass before you open a PR
```

Running the app:

```bash
npm run android:dev  # needs the Android SDK/NDK, see README
```

## Pull requests

1. Fork the repo and branch off `main`.
2. Keep changes focused — one concern per PR.
3. Add or update tests for behaviour changes.
4. Run `npm run test:all` and make sure it is green.
5. Update the docs (`README.md` / `RELEASE_NOTES.md`) when user-facing
   behaviour changes.

## Project conventions

### Frontend (`src/`)

- Plain ES modules — no bundler, no framework. Keep it that way.
- One module per screen under `src/screens/`; export `render(host)` plus an
  optional `load()` and `onFab()`.
- **Always** escape user data with `esc()` from `core/ui.js` before putting it
  into a template string.
- All user-visible strings go through `t('some.key')` and must exist in **both**
  `src/locales/fa.js` and `src/locales/en.js`.
- Entity forms are declarative: add a descriptor to the screen's `FIELDS` array
  rather than writing markup by hand.

### Rust (`rust/terencher-core/`)

- The core crate must stay **free of UI/framework dependencies** so it can be
  tested on the host. Keep `tauri` out of it.
- Add a column in three places: the `CREATE TABLE` in `db.rs`, the `params!`
  list of the create/update functions, and the struct in `models.rs`.
- Add an integration test in `tests/db_test.rs` for new behaviour.

### Tauri shell (`src-tauri/`)

- Commands are thin wrappers — put logic in `terencher-core`, not in
  `commands.rs`.

## Code style

- Rust: `cargo fmt` and `cargo clippy`.
- JS: 2-space indent, single quotes, trailing commas, `const` over `let`.

## License

By contributing you agree that your contributions are licensed under the MIT
License (see [`LICENSE`](LICENSE)).
