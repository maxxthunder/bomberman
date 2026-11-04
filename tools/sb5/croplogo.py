"""Crop a transparent RGBA layer render to its bounding box and save as an indexed PNG (index 0 transparent)."""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGBA")
im = im.crop(im.getbbox())
cols = sorted({p for p in im.getdata() if p[3]})
assert len(cols) < 256
idx = {c: i + 1 for i, c in enumerate(cols)}
out = Image.new("P", im.size, 0)
out.putpalette([0, 0, 0] + [v for c in cols for v in c[:3]])
out.putdata([idx.get(p, 0) if p[3] else 0 for p in im.getdata()])
out.save(sys.argv[2], transparency=0, optimize=True)
print(sys.argv[2], im.size, len(cols), "colors")
