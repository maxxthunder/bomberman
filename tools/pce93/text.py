"""Dump every text string of a '93 or '94 HuCard and mark the ones no coverage run ever read.

  python tools/pce93/text.py <93|94> <rom> <out.txt> <cdl...>

'93: strings are plain bytes, ASCII plus JIS X 0201 half-width katakana ($A1-$DF), ended by $00.
'94: ASCII with control codes, ended by $00: $01 x y = move the cursor, '#' + digit/letter = palette, '_' = space,
';' is drawn as ':', '@' as the copyright sign. Japanese text in '94 is drawn as graphics, not stored as text.
A candidate is a run of at least 4 such characters, mostly letters, ended by $00 (or a control code in '94).
Status: 'read' when Mesen's code/data log marks any of its bytes as read as data, else 'NEVER'.
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep import load_cdl


def strings93(rom):
    for m in re.finditer(rb"[\x20-\x7e\xa1-\xdf]{4,}(?=\x00)", rom):
        s = m.group()
        letters = sum(1 for c in s if 0x41 <= c <= 0x5A or 0xA6 <= c <= 0xDD or c == 0x20)
        kana = sum(1 for c in s if 0xA1 <= c <= 0xDF)
        if letters < len(s) * 0.75:
            continue
        # tile-number runs (ｵｶｷｸｹ, ABCDEF...) are not text: reject 4+ consecutive ascending codes
        if any(s[i + 1] == s[i] + 1 and s[i + 2] == s[i] + 2 and s[i + 3] == s[i] + 3 for i in range(len(s) - 3)) and len(s) < 12:
            continue
        if kana and kana < len(s.replace(b" ", b"")) * 0.5:
            continue
        if kana:   # kana text: anything else must be punctuation or whole upper-case words (RUN, SAVE, PASSWORD)
            rest = re.sub(rb"[\xa1-\xdf]", b" ", s)
            if re.search(rb"[^ A-Z!?.,'\-]", rest) or any(len(w) < 3 for w in re.findall(rb"[A-Z]+", rest)):
                continue
            if len(s) < 5 and not re.search(rb"[\xde\xdf]", s):   # short kana runs without (han)dakuten: tile codes
                continue
        yield m.start(), m.end(), s.decode("cp932")


def strings94(rom):
    for m in re.finditer(rb"(?:\x01..|#[0-9A-F]|[\x20-\x7e])+\x00", rom, re.S):
        s = m.group()[:-1]
        txt, i, parts = [], 0, []
        while i < len(s):
            c = s[i]
            if c == 1:
                if txt:
                    parts.append("".join(txt))
                txt = []
                i += 3
                continue
            if c == 0x23 and i + 1 < len(s):
                i += 2
                continue
            txt.append({0x5F: " ", 0x3B: ":", 0x40: "(c)"}.get(c, chr(c)))
            i += 1
        if txt:
            parts.append("".join(txt))
        t = " / ".join(re.sub(" +", " ", p.strip()) for p in parts if p.strip())
        letters = sum(ch.isalpha() for ch in t)
        if len(t) >= 4 and letters >= len(t.replace(" ", "")) * 0.5 and re.search(r"[A-Z]{3}", t):
            yield m.start(), m.end(), t


if __name__ == "__main__":
    game, romf, out = sys.argv[1:4]
    rom = open(romf, "rb").read()
    cdl = load_cdl(sys.argv[4:], len(rom))
    rows = []
    for a, b, t in (strings93 if game == "93" else strings94)(rom):
        if any(cdl[x] & 1 for x in range(a, b)):   # inside executed code: an opcode run, not text
            continue
        st = "read " if any(cdl[x] & 2 for x in range(a, b)) else "NEVER"
        rows.append(f"${a:05X} {a >> 13:02X}:{a & 0x1FFF:04X} {st} {t}")
    open(out, "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print(out, len(rows), "strings,", sum("NEVER" in r for r in rows), "never read")
