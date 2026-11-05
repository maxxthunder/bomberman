"""Hidden input-code scanner for the PC Engine Bomberman listings (pce90 US/JP, pceub).

Usage: python tools/pce90/padscan.py <listing.asm> [pad-copy zp ...]

Finds every instruction that reads a pad byte ($2200-$220E: held, previous, new per port; plus any zero-page
copies given, e.g. 3F 40 41 for the demo/attract copies, 33 34 35 for pceub's OR of all ports) and prints the
next 8 instructions when they test the value against a constant: AND #/CMP #/EOR #, CMP abs(,X/Y) (a table),
or a counter (INC/DEC) - the shapes a held combination or a counted button sequence takes. Lines in 'db' (not
reached by the trace) are skipped, so run it on a listing traced with every entry point.
"""
import re, sys

lines = [l.rstrip("\n") for l in open(sys.argv[1], encoding="utf-8") if re.match(r"^[0-9A-F]{2}:[0-9A-F]{4}  ", l)]
code = [l for l in lines if not l[8:].lstrip().startswith("db ")]
zps = {z.upper() for z in sys.argv[2:]}
pad = re.compile(r"\b(?:LDA|LDX|LDY|AND|BIT|ORA|EOR|CMP) \$22(0[0-9A-E])\b|\b(?:LDA|LDX|LDY|AND|BIT) \$([0-9A-F]{2})\b(?!\w)")
test = re.compile(r"\b(AND|CMP|CPX|CPY|EOR|BIT) (#\$[0-9A-F]{2}|\$[0-9A-F]{4}(,[XY])?)|\b(INC|DEC) ")
hits = 0
for i, l in enumerate(code):
    op = l[30:] if len(l) > 31 else ""
    m = pad.search(op)
    if not m or (m.group(2) and m.group(2) not in zps):
        continue
    win = code[i + 1:i + 9]
    t = [w for w in win if test.search(w[30:])]
    consts = [w for w in t if "#$" in w[30:] and not re.search(r"#\$(0[0-9A-F]|[1-9A-F]0)$", w[30:])]
    tables = [w for w in t if re.search(r"(CMP|EOR) \$[0-9A-F]{4}", w[30:])]
    multi = [w for w in t if re.search(r"(AND|CMP) #\$([0-9A-F]{2})", w[30:]) and bin(int(re.search(r"#\$([0-9A-F]{2})", w[30:]).group(1), 16)).count("1") >= 2]
    if consts or tables or multi:
        hits += 1
        tag = ("TABLE " if tables else "") + ("COMBO " if multi else "") + ("CONST" if consts else "")
        print(f"== {l[:7]}  {op.strip()}   [{tag.strip()}]")
        for w in win:
            print("     " + w[:7] + "  " + w[30:].strip())
print(hits, "hits", file=sys.stderr)
