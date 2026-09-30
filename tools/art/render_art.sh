#!/usr/bin/env bash
# Renders the placeholder art in game/gui/phone/ from the specs in
# tools/art/*.rpy, using Ren'Py itself (so fonts and shapes match the engine).
#
#   RENPY_SDK=/path/to/renpy-sdk tools/art/render_art.sh [spec-name-prefix]
#
# Only needed when changing the placeholder art; games replace the files.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SDK="${RENPY_SDK:?set RENPY_SDK to the Ren Py SDK folder}"
OUT="$(mktemp -d)"
PROJECT="$OUT/project"
mkdir -p "$PROJECT/game/_art"

for entry in "$ROOT"/game/*; do
    name="$(basename "$entry")"
    case "$name" in saves|cache|demo|script.rpy) continue ;; esac
    ln -s "$entry" "$PROJECT/game/$name"
done
for spec in "$ROOT"/tools/art/*.rpy; do
    ln -s "$spec" "$PROJECT/game/_art/$(basename "$spec")"
done
ln -s "$ROOT/tools/art/shapes" "$PROJECT/game/_art/shapes"

PHONE_RENDER_ART="$ROOT/game/gui/phone" PHONE_RENDER_ONLY="${1:-}" PHONE_TEST_RES=1920x1080 \
    SDL_AUDIODRIVER=dummy timeout 600 xvfb-run -a -s "-screen 0 2600x1500x24" \
    "$SDK/renpy.sh" "$PROJECT" run >"$OUT/render.log" 2>&1 || true

if grep -q "^ART DONE" "$OUT/render.log"; then
    grep -E "^ART " "$OUT/render.log"
else
    tail -40 "$OUT/render.log"
    rm -rf "$OUT"
    exit 1
fi
rm -rf "$OUT"
