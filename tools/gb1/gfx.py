"""Bomberman GB tile graphics: the decompressor and the unused title logo.
Format ($00:1071, also Bomberman GB 3's $00:0DB2): per tile two mask bytes, plane 0 then plane 1; for each of the 8
rows a set bit reads a new byte, a clear bit repeats the last one. Sets are lists of (bank, source, VRAM, tiles)
records, $FF-terminated (stage sets $00:10C3, screen sets $00:12C2).
python tools/gb1/gfx.py logo <rom.gb> <title.vram> <out.png>   the shipped logo beside the unused one (JP $03:6911,
    Wario $03:62E2, 128 tiles, referenced by no set), both on the title's BG map (title.vram: tools/gb1/vdump.lua)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "emu"))
import gbvram
from PIL import Image


def dec(rom, o, n):
    """n tiles from rom offset o -> (2bpp bytes, end offset)"""
    out = bytearray()
    for _ in range(n):
        m0, m1 = rom[o], rom[o + 1]
        o += 2
        t, a = bytearray(16), 0
        for p, m in ((0, m0), (1, m1)):
            for y in range(8):
                if m >> y & 1:
                    a = rom[o]
                    o += 1
                t[2 * y + p] = a
        out += t
    return out, o


if __name__ == "__main__" and sys.argv[1] == "logo":
    rom = open(sys.argv[2], "rb").read()
    o = 0xE911 if rom[0x134:0x13F] != b"WARIO BLAST" else 0xE2E2
    d, e = dec(rom, o, 128)
    v = gbvram.load(sys.argv[3])
    shipped = gbvram.render_map(v, 0, 0, 20, 8, transparent=True)
    v["vram"] = v["vram"][:0x1000] + bytes(d) + v["vram"][0x1800:]   # BG tiles $9000-$97FF (LCDC bit 4 = 0)
    unused = gbvram.render_map(v, 0, 0, 20, 8, transparent=True)
    im = Image.new("RGBA", (328, 64), (255, 255, 255, 255))
    im.alpha_composite(shipped, (0, 0))
    im.alpha_composite(unused, (168, 0))
    im.convert("RGB").resize((656, 128), Image.NEAREST).save(sys.argv[4])
    print("unused logo: %d tiles, $03:%04X-$03:%04X" % (len(d) // 16, 0x4000 + (o & 0x3FFF), 0x4000 + (e & 0x3FFF)))
