"""Dump every text string of the PC Engine Bomberman cards (pce90 US/JP, pceub) and mark the ones never read.

Usage: python tools/pce90/textdump.py <rom.pce> [mesen.cdl ...]  > strings.tsv

Text format (print routines $00:E5xx, same in all three cards): records of `x y text` (BAT column, row) or
`lo hi text` (a VRAM word address), the text is ASCII $20-$7F plus half-width katakana $A1-$DF (JIS X 0201, $DE/$DF are the
dakuten/handakuten that follow the kana), and a record ends with $FE (another record follows) or $FF (end of
list). Lower-case is real text in the staff roll but picture tiles in menus (the skull, the link cable, the
password grid's < > END); $7B-$9F are picture tiles too, shown as {xx}.

A string is 'used' when any of its bytes has the CDL data bit set in one of the Mesen code/data logs given;
'unread' otherwise. Lists printed through a block transfer don't get the data bit (PASSWORD ERROR shows on
screen but stays 'unread'), so check an 'unread' string for code references before calling it unused. Output: rom offset, bank:offset, used flag, kana-folded text.
"""
import sys, unicodedata

rom = open(sys.argv[1], "rb").read()
cdl = bytearray(len(rom))
for p in sys.argv[2:]:
    c = open(p, "rb").read()[-len(rom):]
    for i, b in enumerate(c):
        cdl[i] |= b


def ch(b):
    if 0x20 <= b <= 0x7A:
        return chr(b)
    if 0xA1 <= b <= 0xDF:
        return unicodedata.normalize("NFKC", bytes([b]).decode("shift_jis"))
    return "{%02x}" % b


def text_ok(b):
    return 0x20 <= b <= 0x9F or 0xA1 <= b <= 0xDF


codebanks = {k >> 13 for k in range(len(rom)) if cdl[k] & 1} | set(range(12))  # text sits in the code banks 0-$0B
out, i = [], 0
while i < len(rom) - 4:
    # a record: 2 header bytes (second < $40), >=3 text bytes with >=2 letters/kana, ending in $FE or $FF
    x, y = rom[i], rom[i + 1]
    if y < 0x40 and not cdl[i] & 1 and i >> 13 in codebanks:
        j = i + 2
        while j < len(rom) and text_ok(rom[j]):
            j += 1
        t = rom[i + 2:j]
        letters = sum(1 for b in t if 0x41 <= b <= 0x5A or 0x61 <= b <= 0x7A or 0xA6 <= b <= 0xDD)
        if j < len(rom) and rom[j] in (0xFE, 0xFF) and len(t) >= 3 and letters >= 2 and letters * 2 >= len(t.strip(b" "))                 and sum(1 for b in t if 0x7B <= b <= 0x9F) * 4 <= len(t) and not any(cdl[k] & 1 for k in range(i, j + 1)):
            used = any(cdl[k] & 2 for k in range(i, j + 1))
            s = "".join(ch(b) for b in t)
            out.append((i, used, x, y, s))
            i = j + 1
            continue
    i += 1
for o, used, x, y, s in out:
    print(f"{o:05X}\t{o >> 13:02X}:{o & 0x1FFF:04X}\t{'used' if used else 'UNREAD'}\t{x},{y}\t{s}")
print(f"{len(out)} strings, {sum(1 for r in out if not r[1])} never read", file=sys.stderr)
