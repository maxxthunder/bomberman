"""List and draw the player-sprite pieces no frame uses: python tools/mega/unused.py
The four player sprite sets (installed by $9840-$98BA via $776: frame table, DMA table) give, per frame, a DMA list
`count, $FF, count x (source.l, length/8 bytes, VRAM tile)`. Every 128-byte piece in the sheets ($BD000-$D8000)
that no list points at is printed and drawn to docs/img/mega/unused/pieces.png (crying pieces excluded: cry.py)."""
import os, struct
from PIL import Image, ImageDraw
import cry
rom = cry.rom
L = lambda a: struct.unpack('>I', rom[a:a + 4])[0]
SETS = [(0xEB6B4, 0xECBC0, 184), (0xEC250, 0xEE6C8, 108), (0xEDC6C, 0xEFA92, 173), (0xEF17E, 0xF0D76, 102)]  # frames 1..n
used = set()
for ft, dt, n in SETS:
    for i in range(1, n + 1):
        d = L(dt + 4 * i)
        for k in range(rom[d]):
            a, ln = L(d + 2 + 6 * k), rom[d + 6 + 6 * k]
            used.update(range(a, a + ln * 8, 0x80))
CRY = {a for frs in cry.CRY for ps in frs for a, *_ in ps}
un = [a for a in range(0xBD000, 0xD8000, 0x80) if a not in used and any(rom[a:a + 0x80])]
assert CRY - used <= set(un)
other = [a for a in un if a not in CRY]
print('unreferenced pieces:', len(un), '| crying:', len(CRY - used), '| other:', ' '.join('%X' % a for a in other))
if __name__ == '__main__':
    W = 8; im = Image.new('P', (W * 24, ((len(other) + W - 1) // W) * 28))
    for n, a in enumerate(other): cry.piece(im, a, 0, (n % W) * 24 + 4, (n // W) * 28)
    im.putpalette([0, 136, 255] + cry.PAL[3:] + [0] * (768 - 48))
    im = im.convert('RGB').resize((im.width * 3, im.height * 3), Image.NEAREST); d = ImageDraw.Draw(im)
    for n, a in enumerate(other): d.text(((n % W) * 72 + 4, (n // W) * 84 + 50), '%X' % a, fill=(255, 255, 255))
    im.save(os.path.join(cry.here, '../../docs/img/mega/unused/pieces.png'))
