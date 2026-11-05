"""Capture a game's Super Game Boy packets in Mesen (plain GB mode, tools/emu/sgb.lua) and render what they carry.
Usage: python tools/emu/sgb_dump.py <game dir, e.g. tools/gb1> <ver> <scenario.lua> <out dir>
The scenario is any Lua body for that game's run.sh (lib.lua + sgb.lua are put in front of it).
Writes to <out dir>: packets.txt (frame, command name, bytes), border_<n>.png (each CHR_TRN + PCT_TRN pair
rendered at 256 x 224, colour 0 transparent), pal_<n>.png (each PAL01/23/03/12 packet as swatches) and
trn_<cmd>_<n>.bin (every *_TRN payload). PAL_TRN system palettes go to pal_trn_<n>.png (512 palettes x 4 colours).
Each shot(name) of the scenario is also written as sgb_<name>.png: the DMG shades recoloured with the SGB palettes in
force at that frame (PAL01-PAL12 packets, or PAL_SET's system palettes with its attribute file; ATTR_BLK and the other
area commands are not applied, palette 0 covers the screen then)."""
import os, subprocess, sys
from PIL import Image

NAMES = {0: "PAL01", 1: "PAL23", 2: "PAL03", 3: "PAL12", 4: "ATTR_BLK", 5: "ATTR_LIN", 6: "ATTR_DIV", 7: "ATTR_CHR",
         8: "SOUND", 9: "SOU_TRN", 0xA: "PAL_SET", 0xB: "PAL_TRN", 0xC: "ATRC_EN", 0xD: "TEST_EN", 0xE: "ICON_EN",
         0xF: "DATA_SND", 0x10: "DATA_TRN", 0x11: "MLT_REQ", 0x12: "JUMP", 0x13: "CHR_TRN", 0x14: "PCT_TRN",
         0x15: "ATTR_TRN", 0x16: "ATTR_SET", 0x17: "MASK_EN", 0x18: "OBJ_TRN"}


def rgb(w):
    return ((w & 31) * 255 // 31, (w >> 5 & 31) * 255 // 31, (w >> 10 & 31) * 255 // 31, 255)


def snes_tile(chr_, n):
    o = n * 32
    rows = []
    for y in range(8):
        p = [chr_[o + 2 * y], chr_[o + 2 * y + 1], chr_[o + 16 + 2 * y], chr_[o + 17 + 2 * y]]
        rows.append([sum(((p[k] >> (7 - x)) & 1) << k for k in range(4)) for x in range(8)])
    return rows


def border(chr_, pct):
    im = Image.new("RGBA", (256, 224), (0, 0, 0, 0))
    px = im.load()
    pal = pct[0x800:0x880]
    for ty in range(28):
        for tx in range(32):
            w = pct[2 * (ty * 32 + tx)] | pct[2 * (ty * 32 + tx) + 1] << 8
            t, p, hf, vf = w & 0xFF, (w >> 10) & 7, w >> 14 & 1, w >> 15 & 1
            for y, row in enumerate(snes_tile(chr_, t)):
                for x, c in enumerate(row):
                    if c:
                        q = 16 * ((p - 4) & 3) + c
                        px[tx * 8 + (7 - x if hf else x), ty * 8 + (7 - y if vf else y)] = rgb(pal[2 * q] | pal[2 * q + 1] << 8)
    return im


def swatch(cols, w=16):
    im = Image.new("RGBA", (w * len(cols), w))
    for i, c in enumerate(cols):
        im.paste(rgb(c), (i * w, 0, i * w + w, w))
    return im


SHADE = {255: 0, 176: 1, 104: 2, 0: 3}      # Mesen's default DMG greys -> colour number


def colourize(png, pals, attr):
    im = Image.open(png).convert("RGB")
    px = im.load()
    for y in range(144):
        for x in range(160):
            n = attr[(y // 8) * 20 + x // 8] if attr else 0
            px[x, y] = rgb(pals[n][SHADE.get(px[x, y][0], 0)])[:3]
    return im


if __name__ == "__main__":
    game, ver, scen, out = sys.argv[1:5]
    os.makedirs(out, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    s = os.path.join(out, "sgb.lua")
    open(s, "w").write(open(os.path.join(here, "sgb.lua")).read() + "\n" + open(scen).read())
    res = subprocess.run(["sh", os.path.join(game, "run.sh"), s, ver], capture_output=True, text=True,
                         env=dict(os.environ, OUT=out)).stdout
    log, chrs, nb, npal, ntrn = [], {}, 0, 0, 0
    pals, attr, sysp, files = [[0x7FFF, 0x56B5, 0x294A, 0] for _ in range(4)], None, None, None
    for line in res.splitlines():
        p = line.split()
        if p and p[0] == "SGB":
            b = bytes.fromhex(p[2])
            cmd = b[0] >> 3
            log.append(f"{p[1]:>6} {NAMES.get(cmd, '?%02X' % cmd):9} {b.hex(' ')}")
            if cmd <= 3:
                w = [b[1 + 2 * i] | b[2 + 2 * i] << 8 for i in range(7)]
                a, c = [(0, 1), (2, 3), (0, 3), (1, 2)][cmd]
                pals[a], pals[c] = w[:4], w[:1] + w[4:7]
                for q in pals: q[0] = w[0]
                swatch(w[:4] + w[:1] + w[4:7]).save(os.path.join(out, f"pal_{npal}_{NAMES[cmd]}.png")); npal += 1
            if cmd == 0xA and sysp:
                for k in range(4):
                    i = b[1 + 2 * k] | b[2 + 2 * k] << 8
                    pals[k] = [sysp[8 * i + 2 * j] | sysp[8 * i + 2 * j + 1] << 8 for j in range(4)]
                for q in pals: q[0] = pals[0][0]
                if b[9] & 0x80 and files:
                    f = files[90 * (b[9] & 0x3F):90 * (b[9] & 0x3F) + 90]
                    attr = [(f[i // 4] >> (6 - 2 * (i % 4))) & 3 for i in range(360)]
        elif p and p[0] == "SHOT":
            pass
        elif p and p[0] == "TRN":
            cmd, arg, data = int(p[1], 16), int(p[2], 16), bytes.fromhex(p[3])
            open(os.path.join(out, f"trn_{cmd:02x}_{ntrn}.bin"), "wb").write(data); ntrn += 1
            log.append(f"{'':>6} {NAMES[cmd]} payload -> trn_{cmd:02x}_{ntrn - 1}.bin (arg {arg:02x})")
            if cmd == 0x13:
                chrs[arg & 1] = data
            elif cmd == 0x14:
                c = chrs.get(0, bytes(4096)) + chrs.get(1, bytes(4096))
                border(c, data).save(os.path.join(out, f"border_{nb}.png")); nb += 1
            elif cmd == 0x15:
                files = data
            elif cmd == 0x0B:
                sysp = data
                im = Image.new("RGBA", (4 * 4, 512 * 2))
                for i in range(512):
                    for k in range(4):
                        o = 8 * i + 2 * k
                        im.paste(rgb(data[o] | data[o + 1] << 8), (4 * k, 2 * i, 4 * k + 4, 2 * i + 2))
                im.save(os.path.join(out, f"pal_trn_{ntrn - 1}.png"))
        elif line.startswith("wrote") and line.endswith(".png"):
            n = line.split()[1]
            colourize(os.path.join(out, n), [q[:] for q in pals], attr).save(os.path.join(out, "sgb_" + n))
            print(line)
        elif line.startswith("rc") or "error" in line.lower():
            print(line)
    open(os.path.join(out, "packets.txt"), "w").write("\n".join(log) + "\n")
    print(len(log), "log lines,", nb, "borders,", npal, "palette packets")
