#!/usr/bin/env python3
"""Auto-draft the keepout mask from the aerial: all-black (keepout) except
the THIN paved network (sidewalks). Paved = low saturation, mid-high
brightness; wide paved blobs (roads, roofs, parking lots, plazas) are then
removed with a morphological opening so only walkway-scale strips stay free.
Wide-but-drivable plazas get re-added as white vector edits (apply_edits.py).

Run from repo root:  python3 map/tools/auto_draft.py [--out PATH]
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='map/keepout_draft.pgm')
    ap.add_argument('--aerial', default='map/washu_aerial.png')
    a = ap.parse_args()

    rgb = np.asarray(Image.open(a.aerial).convert('RGB')).astype(np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    sat = mx - mn

    # paved: grayish (low chroma), bright enough to not be shadow/asphalt-dark,
    # and not green-dominant (lawns in shadow read gray but green-tinted)
    paved = (sat < 40) & (mx > 120) & (g <= r + 12)

    # clean specks / pinholes
    paved = ndimage.binary_opening(paved, np.ones((2, 2)))
    paved = ndimage.binary_closing(paved, np.ones((3, 3)))

    # keep only walkway-scale strips: subtract anything wider than ~11 px
    r = 5
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    disk = x * x + y * y <= r * r
    thin = paved & ~ndimage.binary_opening(paved, disk)

    # bridge tiny gaps, then drop isolated islands < 100 px (25 m^2)
    thin = ndimage.binary_closing(thin, np.ones((3, 3)))
    lbl, n = ndimage.label(thin)
    sizes = ndimage.sum(thin, lbl, range(1, n + 1))
    thin = np.isin(lbl, np.flatnonzero(sizes >= 100) + 1)

    mask = np.where(thin, 254, 0).astype(np.uint8)
    with open(a.out, 'wb') as f:
        f.write(f"P5\n{mask.shape[1]} {mask.shape[0]}\n255\n".encode())
        f.write(mask.tobytes())
    print(f"{a.out}: {mask.shape[1]}x{mask.shape[0]}, "
          f"{100 * thin.mean():.1f}% free")

if __name__ == '__main__':
    main()
