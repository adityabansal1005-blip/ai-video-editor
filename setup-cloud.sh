#!/usr/bin/env bash
# Installs the video-editing tools on a Linux machine (Claude Code cloud sessions).
# Safe to run more than once: it skips anything already installed.
#   bash setup-cloud.sh            # tools + base Whisper model
#   bash setup-cloud.sh --small    # also the small model (better Hindi, ~490 MB)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p tools

SUDO=""
if [ "$(id -u)" != "0" ] && command -v sudo >/dev/null; then SUDO="sudo"; fi

# FFmpeg
if ! command -v ffmpeg >/dev/null; then
  echo "== installing ffmpeg"
  $SUDO apt-get update -qq && $SUDO apt-get install -y -qq ffmpeg
fi

# yt-dlp
if ! command -v yt-dlp >/dev/null; then
  echo "== installing yt-dlp"
  python3 -m pip install -q --user yt-dlp || python3 -m pip install -q --break-system-packages yt-dlp
  export PATH="$HOME/.local/bin:$PATH"
fi

# whisper.cpp (built from source; the Windows build lives in tools/whisper/ instead)
if [ ! -x tools/whisper-cli ]; then
  echo "== building whisper.cpp"
  command -v cmake >/dev/null || { $SUDO apt-get update -qq && $SUDO apt-get install -y -qq cmake build-essential; }
  [ -d tools/whisper.cpp ] || git clone --depth 1 https://github.com/ggml-org/whisper.cpp tools/whisper.cpp
  cmake -S tools/whisper.cpp -B tools/whisper.cpp/build -DCMAKE_BUILD_TYPE=Release >/dev/null
  cmake --build tools/whisper.cpp/build -j"$(nproc)" --target whisper-cli >/dev/null
  ln -sf "$PWD/tools/whisper.cpp/build/bin/whisper-cli" tools/whisper-cli
fi

# Whisper models
HF=https://huggingface.co/ggerganov/whisper.cpp/resolve/main
[ -f tools/ggml-base.bin ] || { echo "== downloading base model"; curl -L --fail -o tools/ggml-base.bin "$HF/ggml-base.bin"; }
if [ "${1:-}" = "--small" ] && [ ! -f tools/ggml-small.bin ]; then
  echo "== downloading small model"; curl -L --fail -o tools/ggml-small.bin "$HF/ggml-small.bin"
fi

# Node packages for each reel project (fonts + GSAP)
for d in reel-*/; do
  [ -f "$d/package.json" ] && [ ! -d "$d/node_modules" ] && (cd "$d" && npm ci --no-audit --no-fund >/dev/null)
done

echo "== checks"
ffmpeg -version | head -1
yt-dlp --version
tools/whisper-cli --help >/dev/null 2>&1 && echo "whisper-cli ok"
node --version
npx -y hyperframes --version
