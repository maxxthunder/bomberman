"""SB5 menu/room script listing (the bytecode VM at $C2:038F).
Op sizes: ops 01-FB take C2:0AF5[op-1] argument bytes (handlers C2:04FA); FF nn / FE nn call native nn
(argument lengths from the table at C2:09D4); FD nn / FC nn take C2:0B9E / C2:0BAC[nn-1] bytes.
Scene/room n runs entry n-1 of the 3-byte script table at $C6:0000 (checked in Mesen). Some ops (switch tables) carry inline data
the size table doesn't know about, so a linear listing can drift; it re-syncs after a few ops.
Usage: scripts.py rom dis <addr hex> [count]   |   scripts.py rom routes   (op 0F targets per room)"""
import sys

rom = open(sys.argv[1], "rb").read()
rd = lambda a: rom[a & 0x3FFFFF]
w16 = lambda a: rd(a) | rd(a + 1) << 8
p24 = lambda a: rd(a) | rd(a + 1) << 8 | rd(a + 2) << 16


def oplen(a):
    op = rd(a)
    if op >= 0xFE:
        lens = w16(0xC209D4 + (0xFF - op) * 2) | 0xC20000
        return 2 + rd(lens + rd(a + 1) - 1), "N%d.%02X" % (0xFF - op, rd(a + 1))
    if op in (0xFD, 0xFC):
        return 2 + rd((0xC20B9E if op == 0xFD else 0xC20BAC) + rd(a + 1) - 1), "%02X.%02X" % (op, rd(a + 1))
    return (1, "00") if op == 0 else (1 + rd(0xC20AF5 + op - 1), "op%02X" % op)


def name(r):
    v = w16(0x808A8A + 2 * r)
    return "%d-%d" % (v // 1000, v % 1000) if v >= 1000 else "boss%d" % v


if __name__ == "__main__":
    if sys.argv[2] == "dis":
        a = int(sys.argv[3], 16)
        for _ in range(int(sys.argv[4]) if len(sys.argv) > 4 else 40):
            n, nm = oplen(a)
            print("%06X %-8s %s" % (a, nm, " ".join("%02x" % rd(a + i) for i in range(n))))
            a += n
    else:  # exits: a warp is "11 <dest+3> x y 00" followed by its handler "[05/06 flag]... 0F <dest> 00"
        import re
        starts = sorted({p24(0xC60000 + 3 * i) for i in range(0xAE)})
        graph = {}
        for r in range(0x0D, 0x75):
            a = p24(0xC60000 + 3 * (r - 1))
            end = next((t for t in starts if t > a), a + 0x400)
            blob = bytes(rd(x) for x in range(a, end))
            graph[r] = sorted({m.group(1)[0] for m in re.finditer(rb"\x0f(.)\x00", blob, re.S)} - {r})
            print("%02X %-7s script %06X ->" % (r, name(r), a), " ".join("%02X(%s)" % (t, name(t) if t < 0x75 else "scene") for t in graph[r]))
        for e in (0x6C, 0x6D, 0x6E):  # zone-4 bosses: which endings their zone-5 entries can reach
            seen, todo = set(), [t for t in graph[e] if 0x49 <= t <= 0x66]
            while todo:
                t = todo.pop()
                if t not in seen:
                    seen.add(t)
                    todo += [u for u in graph.get(t, []) if 0x49 <= u <= 0x70]
            print("from %s: reaches %s" % (name(e), ", ".join(name(b) for b in (0x6F, 0x70) if b in seen)))
