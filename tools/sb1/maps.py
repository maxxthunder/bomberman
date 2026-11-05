"""Super Bomberman stage maps: decode and render every arena layout in the ROM, referenced or not.
  python tools/sb1/maps.py <rom> <outdir>      (writes <outdir>/map_<id>_<addr>.png, sheet.png, index.txt)

Format (decoder $C4:7B33, called with the 24-bit pointer at offset $11 of each stage header; stage headers
via the table at $C3:2EEF):
  14 words: hard-block bitmap, 17 columns x 13 rows row-major, MSB first (bit set = cell $0080, a wall)
  then the BG tile stream for the same 221 cells taken two at a time: a mask word every 16 pairs, MSB first;
  bit set = two new words (tile codes for the pair), clear = repeat the last pair. ($7E:4A00 -> $04F4.)
The playfield is columns 2-14, rows 1-11; soft blocks are placed at random when the stage starts.
Unreferenced maps are found by their signature: row 0 and columns 0, 1, 15, 16 all walls."""
import os, sys
from PIL import Image, ImageDraw

W, H = 17, 13


def bitmap(rom, o):
    bits = []
    for k in range(14):
        w = int.from_bytes(rom[o + 2 * k:o + 2 * k + 2], "little")
        bits += [(w >> (15 - b)) & 1 for b in range(16)]
    return [bits[r * W:(r + 1) * W] for r in range(H)]


def tiles(rom, o):
    """BG tile codes per cell (the second stream), and its length in bytes."""
    p, out, a, b = o + 28, [], 0, 0
    n = 0
    while len(out) < 222:
        if n % 16 == 0:
            mask = int.from_bytes(rom[p:p + 2], "little"); p += 2
        if mask >> (15 - n % 16) & 1:
            a = int.from_bytes(rom[p:p + 2], "little"); b = int.from_bytes(rom[p + 2:p + 4], "little"); p += 4
        out += [a, b]
        n += 1
    return out[:W * H], p - o


def walled(m):
    return all(m[0]) and all(m[H - 1]) and all(r[0] and r[1] and r[15] and r[16] for r in m)


def table(rom):
    """The stage header table in bank $C3 ($C3:2EEF in US/EU/beta): 48 words pointing at headers whose map
    pointer (+$11) leads to a walled bitmap."""
    def ok(t, i):
        h = 0x30000 + int.from_bytes(rom[t + 2 * i:t + 2 * i + 2], "little")
        p = int.from_bytes(rom[h + 0x11:h + 0x14], "little") - 0xC00000
        return 0 <= p < len(rom) - 64 and rom[p:p + 2] == b"\xff\xff" and walled(bitmap(rom, p))
    for t in range(0x30000, 0x40000 - 96):
        if ok(t, 0) and ok(t, 1) and sum(ok(t, i) for i in range(48)) >= 46:
            return t
    raise SystemExit("no stage table")


def stage_ptrs(rom):
    ptrs = {}
    t = table(rom)
    for i in range(0x4A):
        h = 0x30000 + int.from_bytes(rom[t + 2 * i:t + 2 + 2 * i], "little")
        p = int.from_bytes(rom[h + 0x11:h + 0x14], "little")
        if p >> 16 in range(0xC0, 0xC8):
            ptrs.setdefault(p - 0xC00000, []).append(i)
    return ptrs


def name(i):
    if i < 0x30:
        return f"{i // 8 + 1}-{i % 8 + 1}"
    if 0x3D <= i <= 0x48:
        return f"battle {i - 0x3C}"
    return f"scene {i:02X}"


def render(m, t, scale=12):
    img = Image.new("RGB", (W * scale, H * scale), (40, 120, 40))
    d = ImageDraw.Draw(img)
    for r in range(H):
        for c in range(W):
            x, y = c * scale, r * scale
            if m[r][c]:
                d.rectangle([x, y, x + scale - 1, y + scale - 1], fill=(150, 150, 160), outline=(70, 70, 80))
            elif t is not None:  # floor: shade by tile code so special floors (belts, holes, warps) show
                v = t[r * W + c] & 0x3FF
                d.rectangle([x + 3, y + 3, x + scale - 4, y + scale - 4], fill=((v * 53) % 200 + 40, (v * 97) % 160 + 60, 60))
    return img


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    ptrs = stage_ptrs(rom)
    found = {o for o in range(0, len(rom) - 64) if rom[o] == 0xFF and rom[o + 1] == 0xFF and walled(bitmap(rom, o))}
    allm = sorted(set(ptrs) | found)
    lines, imgs = [], []
    for o in allm:
        m = bitmap(rom, o)
        t, n = tiles(rom, o)
        ids = ptrs.get(o)
        label = ", ".join(name(i) for i in ids) if ids else "UNREFERENCED"
        extra = sum(m[r][c] for r in range(1, 12) for c in range(2, 15)) - 30  # walls beyond the usual 30 pillars
        img = render(m, t)
        fn = f"map_{0xC00000 + o:06X}.png"
        img.save(os.path.join(out, fn))
        imgs.append((img, f"${0xC00000 + o:06X} {label}"))
        lines.append(f"${0xC00000 + o:06X} {n:4}B  extra walls {extra:+3}  {label}")
    open(os.path.join(out, "index.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    cols = 6
    cw, chh = imgs[0][0].width + 8, imgs[0][0].height + 22
    sheet = Image.new("RGB", (cols * cw, ((len(imgs) + cols - 1) // cols) * chh), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for k, (im, lab) in enumerate(imgs):
        x, y = (k % cols) * cw, (k // cols) * chh
        sheet.paste(im, (x + 4, y + 18))
        d.text((x + 4, y + 3), lab[:34], fill=(0, 0, 0) if "UNREF" not in lab else (200, 0, 0))
    sheet.save(os.path.join(out, "sheet.png"))
