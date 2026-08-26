#!/usr/bin/env python3
"""Render the keepout mask over the aerial for review.

Usage (from repo root):
  python3 map/tools/render_overlay.py OUT.png [--scale S] [--tile X0 Y0 X1 Y1]
                                      [--grid STEP] [--alpha A]

Keepout (black in the mask) renders red at ALPHA over the aerial; free stays
untinted. --tile crops to a pixel window (full-res map coords) BEFORE scaling;
--grid draws labeled lines every STEP map-pixels (labels are global map
coords, so agents can report edit coordinates straight off the render).
"""
import argparse
import numpy as np
from PIL import Image, ImageDraw

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--tile', type=int, nargs=4, metavar=('X0','Y0','X1','Y1'))
    ap.add_argument('--grid', type=int, default=0)
    ap.add_argument('--alpha', type=float, default=0.45)
    ap.add_argument('--aerial', default='map/washu_aerial.png')
    ap.add_argument('--mask', default='map/keepout_draft.pgm')
    a = ap.parse_args()

    aerial = np.asarray(Image.open(a.aerial).convert('RGB')).astype(np.float32)
    mask = np.asarray(Image.open(a.mask).convert('L'))
    assert aerial.shape[:2] == mask.shape, (aerial.shape, mask.shape)

    keep = mask < 128
    red = np.array([255, 30, 30], np.float32)
    aerial[keep] = aerial[keep] * (1 - a.alpha) + red * a.alpha
    im = Image.fromarray(aerial.astype(np.uint8))

    x0 = y0 = 0
    if a.tile:
        x0, y0, x1, y1 = a.tile
        im = im.crop((x0, y0, x1, y1))
    if a.scale != 1.0:
        im = im.resize((round(im.width * a.scale), round(im.height * a.scale)),
                       Image.LANCZOS)
    if a.grid:
        d = ImageDraw.Draw(im)
        s = a.scale
        gx = (x0 // a.grid) * a.grid
        while gx <= x0 + im.width / s:
            px = (gx - x0) * s
            d.line([(px, 0), (px, im.height)], fill=(255, 255, 0), width=1)
            d.text((px + 2, 2), str(gx), fill=(255, 255, 0))
            gx += a.grid
        gy = (y0 // a.grid) * a.grid
        while gy <= y0 + im.height / s:
            py = (gy - y0) * s
            d.line([(0, py), (im.width, py)], fill=(255, 255, 0), width=1)
            d.text((2, py + 2), str(gy), fill=(255, 255, 0))
            gy += a.grid

    im.save(a.out)
    print(f"{a.out}: {im.size}")

if __name__ == '__main__':
    main()
