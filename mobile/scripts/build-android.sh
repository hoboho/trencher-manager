#!/usr/bin/env bash
#
# Build the Terencher Android APK from scratch.
#
# Installs the toolchain into <repo>/.toolchain (gitignored) so it survives
# sandbox resets, then cross-compiles the Rust core and assembles the APK.
#
# Usage:
#   scripts/build-android.sh [--abi arm64|arm|x86|x86_64|all]
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MOBILE="$REPO_ROOT/mobile"
TC="$REPO_ROOT/.toolchain"

JDK_DIR="$TC/jdk"
SDK_DIR="$TC/sdk"
NDK_VERSION="26.1.10909125"
CMDLINE_URL="https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
JDK_URL="https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse"

ABI="arm64"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --abi) ABI="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

case "$ABI" in
  arm64)  RUST_TARGETS=(aarch64-linux-android) ;;
  arm)    RUST_TARGETS=(armv7-linux-androideabi) ;;
  x86)    RUST_TARGETS=(i686-linux-android) ;;
  x86_64) RUST_TARGETS=(x86_64-linux-android) ;;
  all)    RUST_TARGETS=(aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android) ;;
  *) echo "bad --abi: $ABI" >&2; exit 1 ;;
esac

mkdir -p "$TC"

log() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }

# ── 1. JDK ──────────────────────────────────────────────────────────────────
if [[ ! -x "$JDK_DIR/bin/java" ]]; then
  log "Installing JDK 17"
  curl -sSL -o "$TC/jdk.tar.gz" "$JDK_URL"
  mkdir -p "$JDK_DIR"
  tar xzf "$TC/jdk.tar.gz" -C "$JDK_DIR" --strip-components=1
  rm -f "$TC/jdk.tar.gz"
fi
export JAVA_HOME="$JDK_DIR"
export PATH="$JAVA_HOME/bin:$PATH"

# ── 2. Android SDK + NDK ────────────────────────────────────────────────────
if [[ ! -x "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" ]]; then
  log "Installing Android command-line tools"
  curl -sSL -o "$TC/cmdline.zip" "$CMDLINE_URL"
  rm -rf "$TC/sdk_raw"
  unzip -q "$TC/cmdline.zip" -d "$TC/sdk_raw"
  mkdir -p "$SDK_DIR/cmdline-tools"
  mv "$TC/sdk_raw/cmdline-tools" "$SDK_DIR/cmdline-tools/latest"
  rm -rf "$TC/sdk_raw" "$TC/cmdline.zip"
fi
export ANDROID_HOME="$SDK_DIR"
export ANDROID_SDK_ROOT="$SDK_DIR"

if [[ ! -d "$SDK_DIR/ndk/$NDK_VERSION" ]]; then
  log "Installing SDK packages + NDK $NDK_VERSION"
  yes | "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" --sdk_root="$SDK_DIR" --licenses >/dev/null 2>&1 || true
  "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" --sdk_root="$SDK_DIR" \
    "platform-tools" "platforms;android-34" "build-tools;34.0.0" "ndk;$NDK_VERSION"
fi
export NDK_HOME="$SDK_DIR/ndk/$NDK_VERSION"

# ── 3. Rust ─────────────────────────────────────────────────────────────────
export CARGO_HOME="$TC/cargo"
export RUSTUP_HOME="$TC/rustup"
if [[ ! -x "$CARGO_HOME/bin/cargo" ]]; then
  log "Installing Rust"
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
    | sh -s -- -y --profile minimal --default-toolchain stable --no-modify-path
fi
export PATH="$CARGO_HOME/bin:$PATH"

log "Adding Rust Android targets: ${RUST_TARGETS[*]}"
for t in "${RUST_TARGETS[@]}"; do rustup target add "$t"; done

# ── 4. Build ────────────────────────────────────────────────────────────────
cd "$MOBILE"
[[ -d node_modules ]] || npm install

if [[ ! -d src-tauri/gen/android ]]; then
  log "Initialising the Android project"
  npx tauri android init
fi

log "Building APK (ABI: $ABI)"
npx tauri android build --apk --target "$ABI"

log "Done. Artifacts:"
find src-tauri/gen/android/app/build/outputs -name '*.apk' -print 2>/dev/null || true
