# -*- coding: utf-8 -*-
import sys, glob, os
from PIL import Image
d = sys.argv[1]
files = sorted(glob.glob(os.path.join(d, "page-*.png")))
print("pages:", len(files))
for f in files:
    im = Image.open(f).convert("L")
    w, h = im.size
    px = im.load()
    body_h = int(h * 0.94)
    rows = [y for y in range(body_h) if any(px[x, y] < 160 for x in range(0, w, 4))]
    top, bottom = (rows[0], rows[-1]) if rows else (None, None)
    fill = bottom / body_h * 100 if bottom else 0
    print(f"{os.path.basename(f)}: {top}..{bottom} bottom={fill:.1f}%")
