"""Hidden input-code scanner for the NES Bomberman listings (tools/m6502.py output).

Usage: python tools/nes1/padscan.py <listing.asm> <pad addr> [...]     (hex, e.g. 12 13 for nes1; 04B5 04B6 04B7
       04B8 04B9 04BA 04C3 04C4 for nes2)

Finds every instruction that reads one of the pad bytes and prints the next 8 instructions when they test the value
against a constant (AND #/CMP #/EOR # with 2+ bits, or a constant that is not a single button), a table (CMP/EOR
abs) or count it (INC/DEC) - the shapes a held combination or a typed sequence takes. Lines in 'db' (not reached
by the trace) are skipped, so run it on a listing traced with every CDL entry point.
"""
import re, sys

code = []
for l in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"^([0-9A-F]{2}:[0-9A-F]{4})  (?:[0-9a-f]{2} ?)+\s+(\S.*)$", l.rstrip("\n"))
    if m and not m.group(2).startswith(("db ", ".far")):
        code.append((m.group(1), m.group(2)))
pads = {a.upper().lstrip("0").rjust(2, "0") for a in sys.argv[2:]}
pad = re.compile(r"^(?:LDA|LDX|LDY|AND|BIT|ORA|EOR|CMP) \$(?:00)?([0-9A-F]{2,4})(?:,[XY])?$")
test = re.compile(r"^(AND|CMP|CPX|CPY|EOR|BIT) (#\$[0-9A-F]{2}|\$[0-9A-F]{4}(,[XY])?)|^(INC|DEC) ")
hits = 0
for i, (a, op) in enumerate(code):
    m = pad.match(op)
    if not m or m.group(1).lstrip("0").rjust(2, "0") not in pads:
        continue
    win = code[i + 1:i + 9]
    t = [w for w in win if test.match(w[1])]
    cst = [w for w in t if "#$" in w[1] and bin(int(re.search(r"#\$([0-9A-F]{2})", w[1]).group(1), 16)).count("1") >= 2]
    tab = [w for w in t if re.match(r"(CMP|EOR) \$[0-9A-F]{4}", w[1])]
    if cst or tab:
        hits += 1
        print(f"== {a}  {op}   [{('TABLE ' if tab else '') + ('MULTI' if cst else '')}]")
        for w in win:
            print(f"     {w[0]}  {w[1]}")
print(hits, "hits", file=sys.stderr)
