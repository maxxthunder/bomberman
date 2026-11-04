"""Render TCRF's unused crying animations straight from the ROM: python tools/mega/cry.py
Each frame is a set of 16x16 sprite pieces (128 bytes, 4 tiles column-major, the format the player DMA lists
point at). The pieces and offsets were found by matching TCRF's GIFs against every 128-byte block in $BD000-$D8000.
Writes docs/img/mega/unused/cry.png (9 characters, 2 frames each, in TCRF's order, 3x)."""
import os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
rom = open(os.path.join(here, '../../roms/Mega Bomberman (USA).md'), 'rb').read()
CRAM0 = bytes.fromhex('006008880eee0ccc0eee0a0e0e60008e0a600ea00a220e860a42008e00000eee')   # battle CRAM line 0
PAL = [((w >> s) & 0xE) * 255 // 14 for i in range(16) for w in [CRAM0[2*i] << 8 | CRAM0[2*i+1]] for s in (0, 4, 8)]
# (block, hflip, x, y); first frame then second frame; the head piece is shared by both frames
CRY = [
    [[(0xbdc00, 0, -1, -9), (0xbf500, 0, -1, 7)], [(0xbdc00, 0, -1, -9), (0xbf580, 0, -1, 7)]],
    [[(0xc1200, 0, -1, -7), (0xc2280, 0, -1, 9)], [(0xc1200, 0, -1, -7), (0xc2300, 0, -1, 9)]],
    [[(0xc4a00, 0, 0, -5), (0xc4600, 0, 0, 11)], [(0xc4a00, 0, 0, -5), (0xc4700, 0, 0, 11)]],
    [[(0xc6480, 0, -1, -9), (0xc6500, 0, -1, 7)], [(0xc6480, 0, -1, -9), (0xc6580, 0, -1, 7)]],
    [[(0xc8a00, 0, -6, -11), (0xc8a00, 1, 9, -11), (0xc8b00, 0, -6, 5), (0xc8980, 0, 10, 5)],
     [(0xc8a00, 0, -6, -11), (0xc8a00, 1, 9, -11), (0xc8900, 0, -6, 5), (0xc8980, 0, 10, 5)]],
    [[(0xcf000, 0, -1, -7), (0xd0400, 0, -1, 9)], [(0xcf000, 0, -1, -7), (0xd0500, 0, -1, 9)]],
    [[(0xd1480, 0, 0, -5), (0xd2100, 0, 0, 11)], [(0xd1480, 0, 0, -5), (0xd2180, 0, 0, 11)]],
    [[(0xd4e80, 0, -1, -7), (0xd5080, 0, -1, 9)], [(0xd4e80, 0, -1, -7), (0xd5a80, 0, -1, 9)]],
    [[(0xcdd00, 0, -3, 0)], [(0xcdd80, 0, -3, 0)]],
]
def piece(im, a, hf, ox, oy):
    for t in range(4):
        for y in range(8):
            for x in range(8):
                b = rom[a + t * 32 + y * 4 + x // 2]; v = b >> 4 if x % 2 == 0 else b & 15
                px = (t // 2) * 8 + x
                if v: im.putpixel((ox + (15 - px if hf else px), oy + (t % 2) * 8 + y), v)
if __name__ == '__main__':
    C = 40
    im = Image.new('P', (len(CRY) * C, 2 * C))
    for n, frs in enumerate(CRY):
        for f, ps in enumerate(frs):
            for a, hf, x, y in ps: piece(im, a, hf, n * C + 10 + x, f * C + 14 + y)
    im.putpalette([0, 136, 255] + PAL[3:] + [0] * (768 - 48))
    im.convert('RGB').resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(here, '../../docs/img/mega/unused/cry.png'))
