"""Title logo from a title-screen screenshot (shot() in Mesen, CGB colours): rows 0..H (default 54), the flat
background flood-filled transparent from the border, cropped. Usage: python tools/max/logo.py <title.png> <out.png> [H]"""
import sys
from PIL import Image
src, out, H = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 54
im = Image.open(src).convert('RGBA').crop((0, 0, 160, H))
px = im.load(); w, h = im.size; bg = px[0, 0]
st = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
seen = set()
while st:
    x, y = st.pop()
    if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or px[x, y][:3] != bg[:3]:
        continue
    seen.add((x, y)); px[x, y] = (0, 0, 0, 0)
    st += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
im.crop(im.getbbox()).save(out)
