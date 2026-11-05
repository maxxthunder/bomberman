"""List SB5 routines (by entry point) that never executed, from a disassembly and a Mesen CDL.
Entry points: JSR/JSL/JMP/JML targets in the listing, the script-op handler table ($C2:04FA, 251 words),
the native table ($C2:0650, 3-byte pointers; count from the argument-length table at $C2:09D4), and
labels that start code right after an RTS/RTL/RTI/JMP/BRA (pointer-table or orphaned routines).
For each never-run entry: who references it (callers, and whether any caller ran), and its size.
Usage: deadcode.py <asm dir> <rom> <cdl> [--code]   (--code also prints the first lines of each routine)"""
import os, re, sys

LINE = re.compile(r"^\s+(\w{3})\s*(.*?)\s*; \$([0-9A-F]{6})")
LABEL = re.compile(r"^L_([0-9A-F]{6}):")
STOP = {"RTS", "RTL", "RTI", "JMP", "JML", "BRA", "BRL", "STP"}


def load(path):
    ins, labels, text = [], set(), {}
    for name in sorted(os.listdir(path)):
        if re.match(r"bank_C[0-7]\.asm$", name):
            pend = None
            for line in open(os.path.join(path, name)):
                m = LABEL.match(line)
                if m:
                    labels.add(int(m.group(1), 16))
                    continue
                m = LINE.match(line)
                if m:
                    a = int(m.group(3), 16)
                    ins.append((a, m.group(1), m.group(2)))
                    text[a] = line.rstrip()
    return ins, labels, text


def entries(ins, labels, rom):
    ref = {}
    for a, op, arg in ins:
        m = re.match(r"^(?:L_([0-9A-F]{6})|\$([0-9A-F]{4,6}))$", arg)
        if op in ("JSR", "JSL", "JMP", "JML") and m:
            t = int(m.group(1) or m.group(2), 16)
            if m.group(2) and len(m.group(2)) == 4:
                t |= a & 0xFF0000
            ref.setdefault(t | 0xC00000 if t >> 16 in (0x80, 0x00) else t, set()).add(a)
    w16 = lambda x: rom[x & 0x3FFFFF] | rom[(x + 1) & 0x3FFFFF] << 8
    for op in range(1, 0xFC):
        ref.setdefault(0xC20000 | w16(0xC204FA + 2 * (op - 1)), set()).add("op%02X" % op)
    n = 0
    while True:  # natives: as many as the argument-length table has
        p = 0xC20650 + 3 * n
        t = w16(p) | rom[(p + 2) & 0x3FFFFF] << 16
        if not 0xC0 <= t >> 16 <= 0xC7 or n > 255:
            break
        ref.setdefault(t, set()).add("N%02X" % (n + 1))
        n += 1
    br = {int(arg[2:], 16) for a, op, arg in ins
          if op in ("BPL", "BMI", "BVC", "BVS", "BCC", "BCS", "BNE", "BEQ", "BRA", "BRL") and arg.startswith("L_")}
    prev = None
    for a, op, arg in ins:  # code after an exit that nothing calls or branches to: pointer-table or orphaned routine
        if prev and prev[1] in STOP and a in labels and a not in ref and a not in br:
            ref[a] = {"after-%s" % prev[1]}
        prev = (a, op, arg)
    return ref


if __name__ == "__main__":
    ins, labels, text = load(sys.argv[1])
    rom = open(sys.argv[2], "rb").read()
    cdl = open(sys.argv[3], "rb").read()
    cdl = cdl[9:] if cdl[:5] == b"CDLv2" else cdl
    ran = lambda a: isinstance(a, int) and cdl[a & 0x3FFFFF] & 1
    addrs = sorted(text)
    import bisect
    ref = entries(ins, labels, rom)
    dead = [e for e in sorted(ref) if e in text and not ran(e)]
    for e in dead:
        i = bisect.bisect_left(addrs, e)
        j = i
        while j < len(addrs) and not ran(addrs[j]) and (j == i or addrs[j] not in ref or not ran(addrs[j])):
            if text[addrs[j]].split()[0] in ("RTS", "RTL", "RTI"):
                break
            j += 1
        size = (addrs[min(j, len(addrs) - 1)] - e) + 1
        callers = sorted(ref[e], key=str)
        live = [c for c in callers if ran(c)]
        kind = "callers-ran" if live else "no-live-caller"
        print("%06X  %5d bytes  %-14s %s" % (e, size, kind, " ".join(c if isinstance(c, str) else "%06X%s" % (c, "" if ran(c) else "*") for c in callers[:6])))
        if "--code" in sys.argv:
            for a in addrs[i:i + 8]:
                print("      " + text[a].strip())
    print("entries", len([e for e in ref if e in text]), "never run", len(dead), file=sys.stderr)
