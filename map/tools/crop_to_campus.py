#!/usr/bin/env python3
"""One-time crop of the NAIP export down to the campus extent.

Original export: 4004x2664 px, 0.5 m/px, WGS84 bbox
lon -90.3235..-90.3005, lat 38.6435..38.6555 (SW corner = pixel (0, 2663)).

Crop window (original pixel coords): x 1284..4004, y 804..2664
-> 2720x1860 px. Bottom/right edges are unchanged, so the south edge
latitude is unchanged and only the west longitude / north latitude move.

Run from the repo root:  python3 map/tools/crop_to_campus.py
Safe to re-run only against the ORIGINAL 4004x2664 files (it checks).
"""
import numpy as np
from PIL import Image

X0, Y0, X1, Y1 = 1284, 804, 4004, 2664
ORIG_W, ORIG_H = 4004, 2664

def crop_image(path):
    im = Image.open(path)
    if im.size != (ORIG_W, ORIG_H):
        raise SystemExit(f"{path} is {im.size}, expected {(ORIG_W, ORIG_H)} — already cropped?")
    return im.crop((X0, Y0, X1, Y1))

def save_pgm(arr, path):
    with open(path, 'wb') as f:
        f.write(f"P5\n{arr.shape[1]} {arr.shape[0]}\n255\n".encode())
        f.write(arr.astype(np.uint8).tobytes())

if __name__ == '__main__':
    crop_image('map/washu_aerial.png').save('map/washu_aerial.png')

    keep = np.asarray(crop_image('map/keepout_draft.pgm').convert('L'))
    save_pgm(keep, 'map/keepout_draft.pgm')

    base = np.full((Y1 - Y0, X1 - X0), 254, np.uint8)
    save_pgm(base, 'map/base_map.pgm')

    print(f"cropped to {X1-X0}x{Y1-Y0}")
