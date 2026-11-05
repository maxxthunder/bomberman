"""Stage layouts of Bomberman GB 2 (JP) / Bomberman GB (US): every layout the world tables point at, and the bytes of
the layout bank no layout covers.
Usage: python tools/gb2/stages.py <rom.gb> [<cdl> ...] > disasm/gb2/stages_<ver>.tsv
Loader $00:0E32 ($C100 = world << 4 | mode << 3 | stage): bank 5 $4000 holds two word pointers (MODE-A, MODE-B) to
7 world records of 8 bytes; the first word is the world header. Header (read by $00:0FEC): graphics bank + pointer
(-> $9000), map bank + pointer (two maps -> $D800, $DC00), 3 bytes for $C015-$C017, then 3 bytes per stage: layout
pointer (in the map bank) and $C018. World 8 (C012 >= 7) and every boss (stage 7) use the 8 headers of the word table
bank 5 $4074 ($00:0ED4), stage entry 0; their entry 4 is a second 6 x 5 layout stored after the boss arena. Layout
($00:1054): width, height, then width x height metatile numbers (2 x 2 tiles each, -> $D000). "gap after" = bytes
between a layout's end and the next layout in the same bank (under $100; the compressed maps sit between worlds)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sm83

rom = open(sys.argv[1], "rb").read()
cdl = sm83.load_cdl(sys.argv[2:], len(rom))
f = lambda b, a: b * 0x4000 + a - 0x4000
w = lambda b, a: rom[f(b, a)] | rom[f(b, a) + 1] << 8
refs = {}


def header(h, stages, label):
    bank = rom[f(5, h) + 3]
    for s in stages:
        refs.setdefault(f(bank, w(5, h + 9 + 3 * s)), []).append(label if label.startswith("boss") else f"{label}-{s + 1}")


for mode in (0, 1):
    for world in range(7):
        header(w(5, w(5, 0x4000 + 2 * mode) + 8 * world), range(5), "AB"[mode] + str(world + 1))
for i in range(8):
    header(w(5, 0x4074 + 2 * i), [0], f"boss{i + 1}")
    header(w(5, 0x4074 + 2 * i), [4], f"boss{i + 1}b")   # a second 6x5 layout, stored after the boss arena
print("offset\tbank:addr\tsize\tread\tused by\tgap after")
starts = sorted(refs)
for k, o in enumerate(starts):
    W, H = rom[o], rom[o + 1]
    e = o + 2 + W * H
    rd = sum(cdl[i] >> 1 & 1 for i in range(o, e))
    nxt = starts[k + 1] if k + 1 < len(starts) else None
    gap = nxt - e if nxt and nxt >> 14 == o >> 14 and nxt - e < 0x100 else 0
    b, a = sm83.loc(o)
    print(f"{o:05X}\t{b:02X}:{a:04X}\t{W}x{H}\t{rd}/{e - o}\t{','.join(refs[o])}\t{gap or ''}")
