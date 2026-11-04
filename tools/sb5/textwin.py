"""Decode SB5 text windows (the debug menu text TCRF found at file 0x11EEFA is message $F1 of table 6).
Text drawer $C0:0000-$C0:0134: table at $80:8000 + 3*$0340 (24-bit base) -> 16-bit pointer per message,
same bank. A message is a list of windows: w h [x y] attr, then w*h tile bytes through the decompressor
at $C0:1CB0/$C0:1D45, plus a second w*h layer (tile high bytes) when attr == 0. w == 0 ends the message.
Decompressor: control byte c, count (c & 31) + 1, mode c >> 5:
  0 literal bytes, 1 previous byte + 1, 2-7 copy from 1, 2, 4, 16, 32, 64 bytes back.
The 256-byte output buffer ($0200) is shared by both layers; the drawer re-reads from the stream position.
Usage: textwin.py rom table msg [msg...]   (e.g. textwin.py rom 6 F1 F2 F3 F4 F5);  textwin.py rom test"""
import sys

DIST = [0, 0, 1, 2, 4, 16, 32, 64]


class Stream:
    def __init__(self, rom, off):
        self.rom, self.p, self.out = rom, off, []

    def take(self, n):  # n bytes through the decompressor; stops exactly at the last run used
        got, self.out, left = [], [], 0  # each layer starts a fresh history ($C0:1CB0 clears $0200)
        while len(got) < n:
            if not left:
                c = self.rom[self.p]
                self.p += 1
                mode, left = c >> 5, (c & 31) + 1
            if mode == 0:
                v = self.rom[self.p]
                self.p += 1
            elif mode == 1:
                v = (self.out[-1] + 1) & 255
            else:
                v = self.out[-DIST[mode]]
            self.out.append(v)
            got.append(v)
            left -= 1
        assert not left, "run crosses a layer end"
        return got


def windows(rom, off, flags=0):
    """Yield (x, y, w, h, attr, tiles, highs) for each window of the message at file offset off."""
    while rom[off]:
        w, h, y = rom[off], rom[off + 1], 2
        x = yy = None
        if not flags & 6:
            x, yy, y = rom[off + 2], rom[off + 3], 4
        attr = rom[off + y]
        s = Stream(rom, off + y + 1)
        tiles = s.take(w * h)
        highs = s.take(w * h) if attr == 0 else None
        off = s.p
        yield x, yy, w, h, attr, tiles, highs


def msg_offset(rom, table, msg):
    e = 0x8000 + 3 * table
    base = rom[e] | rom[e + 1] << 8 | rom[e + 2] << 16
    p = (base & 0x3FFFFF) + 2 * msg
    return (base & 0x3F0000) | rom[p] | rom[p + 1] << 8


def show(t):
    return "".join(chr(c) if 32 <= c < 127 else "{%02X}" % c for c in t)


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    if sys.argv[2] == "test":  # self-check against the retail ROM
        w = next(windows(rom, msg_offset(rom, 6, 0xF1)))
        assert msg_offset(rom, 6, 0xF1) == 0x11EEF3 and w[2:4] == (14, 11) and show(w[5][:14]) == ">REST SET XXX ", w
        print("ok")
        sys.exit()
    table = int(sys.argv[2])
    for m in sys.argv[3:]:
        off = msg_offset(rom, table, int(m, 16))
        print(f"message ${int(m, 16):02X} at file 0x{off:06X}")
        for x, y, w, h, attr, tiles, highs in windows(rom, off):
            print(f"  window x={x} y={y} {w}x{h} attr=${attr:02X}" + ("" if highs is None else f" high bytes {sorted(set(highs))}"))
            for r in range(h):
                print("   |" + show(tiles[r * w:(r + 1) * w]) + "|")
