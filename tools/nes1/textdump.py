"""Dump the text strings of the NES Bomberman carts (nes1, nes2) and mark the ones never read.

Usage: python tools/nes1/textdump.py <rom.nes> [<cdlhex> ...]  > strings.tsv

Both carts keep text as ASCII tile numbers ($20-$5F) in the PRG: nes1 uses ':' ($3A) for a space in its screens,
nes2 '@' ($40). A string is any run of 4+ such bytes with 3+ letters, outside executed code, where letters are at
least half the non-space bytes. 'used' = one of its bytes has the CDL data bit (bit 1) from a run; 'UNREAD'
otherwise (a string copied by code that reads it with an index the CDL marks still counts as read). Columns: PRG
offset, bank:address, used flag, text (':' and '@' shown as spaces).
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import m6502 as M

rom = M.prg(sys.argv[1])
cdl = M.read_cdl(sys.argv[2:], len(rom)) if len(sys.argv) > 2 else bytearray(len(rom))
nb = len(rom) // M.BANK
out = []
for m in re.finditer(rb"[\x20-\x5f]{4,}", rom):
    s, i, j = m.group(), m.start(), m.end()
    letters = sum(65 <= c <= 90 for c in s)
    body = s.replace(b":", b"").replace(b"@", b"").replace(b" ", b"")
    if letters < 3 or letters * 2 < len(body) or any(cdl[k] & 1 for k in range(i, j)):
        continue
    used = any(cdl[k] & 2 for k in range(i, j))
    b = i // M.BANK
    out.append((i, b, (0xC000 if b == nb - 1 else 0x8000) | i % M.BANK, used, s.decode().replace(":", " ").replace("@", " ")))
for i, b, a, used, s in out:
    print(f"{i:05X}\t{b:02X}:{a:04X}\t{'used' if used else 'UNREAD'}\t{s}")
print(f"{len(out)} strings, {sum(1 for r in out if not r[3])} never read", file=sys.stderr)
