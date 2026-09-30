#!/usr/bin/env python3
"""Fails if two framework files define the same top-level name.

Every *_ren.py file under game/phone/ runs in the one `phone` named store,
so a helper in one app silently replaces a same-named one in another.
"""

import collections
import glob
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "game", "phone")
TOP_LEVEL = re.compile(r"(?:def|class)\s+([A-Za-z_]\w*)|([A-Za-z_]\w*)\s*=(?!=)")

defs = collections.defaultdict(set)
for path in glob.glob(os.path.join(ROOT, "**", "*_ren.py"), recursive=True):
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = TOP_LEVEL.match(line)
            if m:
                defs[m.group(1) or m.group(2)].add(os.path.relpath(path, ROOT))

clashes = {name: files for name, files in defs.items() if len(files) > 1}
for name, files in sorted(clashes.items()):
    print("phone store name {!r} is defined in: {}".format(name, ", ".join(sorted(files))))
sys.exit(1 if clashes else 0)
