#!/usr/bin/env python3
"""Sanity-check the keepout mask after editing.

Run from repo root:  python3 map/tools/check_mask.py

Checks:
  - size matches georef.yaml (broken crop = broken georeferencing)
  - values are pure trinary-safe 0/254/255 (mid-grays = "unknown" cells)
  - the free network is connected: reports component count and whether the
    key campus areas share the largest component
Exit code 1 on hard failures (size/grays), 0 otherwise.
"""
import sys

import numpy as np
import yaml
from PIL import Image
from scipy import ndimage

# map-pixel probes for areas the robot must reach (x, y)
PROBES = {
    'central campus': (1500, 950),
    'east end': (2400, 950),
    'north campus row': (900, 300),
    'west garages': (330, 330),
    'athletic area': (500, 1100),
    'South 40': (350, 1550),
}


def main():
    with open('map/georef.yaml') as f:
        g = yaml.safe_load(f)
    mask = np.asarray(Image.open('map/keepout_draft.pgm'))
    ok = True

    h, w = mask.shape
    if (w, h) != (g['width_px'], g['height_px']):
        print(f"FAIL size: {w}x{h}, georef.yaml says {g['width_px']}x{g['height_px']}")
        ok = False

    vals = np.unique(mask)
    bad = [v for v in vals if v not in (0, 254, 255)]
    if bad:
        print(f"FAIL gray values present (render as 'unknown'): {bad[:10]}")
        ok = False

    free = mask > 128
    lbl, n = ndimage.label(free, structure=np.ones((3, 3)))
    sizes = np.bincount(lbl.ravel()); sizes[0] = 0
    main_id = int(np.argmax(sizes))
    print(f"free: {100 * free.mean():.1f}%   components: {n}   "
          f"largest: {sizes[main_id]} px ({100 * sizes[main_id] / max(1, free.sum()):.0f}% of free)")

    for name, (x, y) in PROBES.items():
        r = 20
        sub = lbl[max(0, y - r):y + r, max(0, x - r):x + r]
        ids = set(np.unique(sub)) - {0}
        if main_id in ids:
            print(f"  ok      {name}")
        elif ids:
            print(f"  ISLAND  {name} — free nearby but not connected to main network")
        else:
            print(f"  BLOCKED {name} — no free cells within {r} px of probe")

    stray = int((sizes > 0).sum() - 1)
    if stray:
        small = int(((sizes > 0) & (sizes < 150)).sum())
        print(f"note: {stray} non-main components ({small} are tiny specks < 150 px)")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
