#!/usr/bin/env bash
# Lints the project and runs the in-engine tests at several resolutions.
#
#   RENPY_SDK=/path/to/renpy-8.5.3-sdk tools/test.sh [--shots DIR]
#
# Needs xvfb-run on Linux (the game opens a window).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${RENPY_SDK:?set RENPY_SDK to the Ren Py SDK folder}"
SHOTS=""
if [[ "${1:-}" == "--shots" ]]; then
    SHOTS="$(mkdir -p "$2" && cd "$2" && pwd)"
fi
RESOLUTIONS="${PHONE_RESOLUTIONS:-1280x720 1920x1080 2560x1440}"
OUT="$(mktemp -d)"
status=0

echo "== lint"
"$SDK/renpy.sh" "$ROOT" lint >"$OUT/lint.txt" 2>&1 || true
# Lint reports problems before its statistics section.
if sed '/^Statistics:/,$d' "$OUT/lint.txt" | grep -vE '^\s*$|lint report, generated at' | grep -q .; then
    sed '/^Statistics:/,$d' "$OUT/lint.txt"
    status=1
else
    echo "clean"
fi

for res in $RESOLUTIONS; do
    echo "== tests at $res"
    PHONE_TESTS=1 PHONE_TEST_RES="$res" PHONE_TEST_OUT="$OUT/$res.txt" PHONE_SHOTS="$SHOTS" \
        SDL_AUDIODRIVER=dummy timeout 300 xvfb-run -a -s "-screen 0 2600x1500x24" \
        "$SDK/renpy.sh" "$ROOT" run >"$OUT/$res.log" 2>&1 || true
    if [[ -f "$OUT/$res.txt" ]]; then
        grep -E '^(FAIL|ERROR|RESULT)' -A30 "$OUT/$res.txt" | grep -v '^RUN' || true
        grep -q '^RESULT PASS' "$OUT/$res.txt" || status=1
    else
        echo "no results; engine log:"
        tail -30 "$OUT/$res.log"
        status=1
    fi
done

rm -rf "$OUT"
exit $status
