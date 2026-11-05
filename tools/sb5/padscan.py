"""Static scan for hidden input codes in an SB5 disassembly (disasm/sb5, disasm/sb5/caravan, disasm/sb5en).
Groups the code banks ($C0-$C7) into routines (label to RTS/RTL/JMP) and reports each routine that reads a
joypad register or one of the game's pad copies, with the features that mark a cheat-code reader:
a compare against a multi-button constant (combo), a compare against a table (table), or a press counter
(a RAM byte incremented or compared with a count in the same routine).
Pad copies (built at $C0:0A56 from $4218-$421F): $19-$1E raw, $2C-$30 held A X L R B Y Sel St,
$31-$35 held d-pad, $36-$3A newly pressed buttons, $3B-$3F new d-pad, $40-$44 d-pad auto-repeat.
Usage: padscan.py <asm dir> [--all]   (default: only routines with at least one feature)"""
import os, re, sys

LINE = re.compile(r"^\s+(\w{3})\s*(.*?)\s*; \$([0-9A-F]{6})")
PAD = re.compile(r"^\$(?:0000|00)?(19|1A|1B|1C|1D|1E|2[C-F]|3[0-9A-F]|4[0-4])(?:,X|,Y)?$|^\$(?:00)?421[89A-F]$|^\$(?:00)?401[67]$")
BITS = "A X L R B Y Sl St".split()
END = ("RTS", "RTL", "RTI", "JMP", "JML")


def combo(v):
    return "+".join(b for i, b in enumerate(BITS) if v & (0x80 >> i))


def routines(path):
    cur = []
    for name in sorted(os.listdir(path)):
        if re.match(r"bank_C[0-7]\.asm$", name):
            for line in open(os.path.join(path, name)):
                m = LINE.match(line)
                if m:
                    cur.append((int(m.group(3), 16), m.group(1), m.group(2)))
                    if m.group(1) in END:
                        yield cur
                        cur = []


def features(r):
    reads = [(a, op, arg) for a, op, arg in r if op in ("LDA", "BIT", "AND", "ORA", "EOR", "CMP") and PAD.match(arg)]
    if not reads:
        return None, []
    tags = set()
    for i, (a, op, arg) in enumerate(r):
        if op == "CMP" and arg.startswith("#$"):
            v = int(arg[2:], 16)
            prev = [x for x in r[max(0, i - 4):i] if PAD.match(x[2])]
            if prev and v and v & (v - 1):
                tags.add("combo %s=%s @%06X" % (arg, combo(v) if prev[-1][2].lstrip("$0").upper()[:2] in ("2C", "2D", "2E", "2F", "30", "36", "37", "38", "39", "3A") else "pad", a))
        elif op == "CMP" and re.match(r"^\$[0-9A-F]{4,6},[XY]$", arg) and not PAD.match(arg):
            tags.add("table %s @%06X" % (arg, a))
        elif op in ("INC", "DEC") and arg.startswith("$") and not PAD.match(arg) and not arg.startswith("$0D"):
            tags.add("count %s" % arg)
    return reads, sorted(tags)


if __name__ == "__main__":
    for r in routines(sys.argv[1]):
        reads, tags = features(r)
        if reads and (tags or "--all" in sys.argv):
            print("%06X-%06X  reads %s  | %s" % (r[0][0], r[-1][0], ",".join(sorted({x[2] for x in reads})), "; ".join(tags)))
