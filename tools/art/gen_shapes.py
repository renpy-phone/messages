#!/usr/bin/env python3
"""Generate the white base shapes that tools/art/ tints into placeholder art.

Pure standard library so it runs anywhere. Re-run after changing a shape:

    python3 tools/art/gen_shapes.py
"""

import math
import os
import struct
import zlib

OUT = os.path.join(os.path.dirname(__file__), "shapes")
SAMPLES = 4  # supersampling per axis for anti-aliased edges


def write_png(path, width, height, alpha_rows):
    raw = bytearray()
    for row in alpha_rows:
        raw.append(0)  # filter: none
        for a in row:
            raw += bytes((255, 255, 255, a))

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png)


def render(width, height, inside):
    """Rasterise a shape given as inside(x, y) -> bool, with supersampling."""
    rows = []
    step = 1.0 / SAMPLES
    for y in range(height):
        row = []
        for x in range(width):
            hits = 0
            for sy in range(SAMPLES):
                for sx in range(SAMPLES):
                    if inside(x + (sx + 0.5) * step, y + (sy + 0.5) * step):
                        hits += 1
            row.append(int(round(255 * hits / (SAMPLES * SAMPLES))))
        rows.append(row)
    return rows


def rounded_rect(width, height, radius):
    def inside(x, y):
        cx = min(max(x, radius), width - radius)
        cy = min(max(y, radius), height - radius)
        return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2

    return inside


def ring(size, outer, inner):
    c = size / 2.0

    def inside(x, y):
        d = math.hypot(x - c, y - c)
        return inner <= d <= outer

    return inside


SHAPES = {
    # 9-slice frames: use Frame(img, radius, radius).
    "round_8.png": (48, 48, rounded_rect(48, 48, 8)),
    "round_18.png": (64, 64, rounded_rect(64, 64, 18)),
    "round_48.png": (128, 128, rounded_rect(128, 128, 48)),
    # Masks and dots.
    "circle.png": (256, 256, rounded_rect(256, 256, 128)),
    "ring.png": (256, 256, ring(256, 128, 116)),
    # App icon background (squircle-ish).
    "app_icon.png": (192, 192, rounded_rect(192, 192, 44)),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (w, h, shape) in SHAPES.items():
        write_png(os.path.join(OUT, name), w, h, render(w, h, shape))
        print("wrote", name)


if __name__ == "__main__":
    main()
