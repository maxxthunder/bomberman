"""Text dump for Bomberman GB 2 (JP) / Bomberman GB (US): every run of bytes that decodes as text, with whether the
runs' bytes were read in the Mesen runs (CDL data bit).
Usage: python tools/gb2/textdump.py <rom.gb> <us|jp> <cdl> [<cdl> ...] > text_<ver>.tsv
Encoding (the story text at $05:7327 US / $05:7363 JP, found by a CDL diff over the intro): $00 space, $01-$0A
0-9, $0B-$24 A-Z, $28 !, $2C 、/, $2D ., $5F ..., $29 ー; JP: $30-$5D katakana ア-ン, $60-$8D hiragana あ-ん,
$90-$9F small kana. JP text is stored as (mark, character) pairs: mark $00 none, $25 ゛, $26 ゜.
Story text is in fixed 16-column lines; a run is kept when it has at least 6 letters / kana, 3/4 of its non-space
characters are letters or kana and it uses at least 5 different ones (graphics data decodes too)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sm83

KATA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
HIRA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
SMALL = "ァィェャュョッぁぃぅぇぉゃゅょっ"   # $93 ャ $94 ュ $96 ッ $9D ゅ $9E ょ $9F っ seen in the story text; the rest guessed
DAK = {c: chr(ord(c) + 1) for c in "かきくけこさしすせそたちつてとはひふへほカキクケコサシスセソタチツテトハヒフヘホ"}
HAN = {c: chr(ord(c) + 2) for c in "はひふへほハヒフヘホ"}
T = {0: " ", 0x28: "!", 0x29: "ー", 0x2A: "?", 0x2B: "・", 0x2C: "、", 0x2D: ".", 0x2E: "「", 0x2F: "」", 0x5F: "…"}
T.update({1 + i: str(i) for i in range(10)})
T.update({0xB + i: chr(65 + i) for i in range(26)})
T.update({0x30 + i: c for i, c in enumerate(KATA)})
T.update({0x60 + i: c for i, c in enumerate(HIRA)})
T.update({0x90 + i: c for i, c in enumerate(SMALL)})


def runs_single(rom):
    i = 0
    while i < len(rom):
        j = i
        while j < len(rom) and rom[j] in T and rom[j] < 0x30:
            j += 1
        if sum(0xB <= b <= 0x24 for b in rom[i:j]) >= 6 and rom[i:j].count(0) >= 2 and sum(b == 0 for b in rom[i:j]) * 6 < (j - i) * 5:
            yield i, j, "".join(T[b] for b in rom[i:j]).rstrip()
            i = j
        i = max(i + 1, j)


def runs_pairs(rom):
    i = 0
    while i < len(rom) - 1:
        j, out = i, []
        while j < len(rom) - 1 and rom[j] in (0, 0x25, 0x26) and rom[j + 1] in T:
            c = T[rom[j + 1]]
            out.append(DAK.get(c, c) if rom[j] == 0x25 else HAN.get(c, c) if rom[j] == 0x26 else c)
            j += 2
        kana = sum(1 for c in out if c in KATA + HIRA + SMALL or c.isalpha())
        if kana >= 6:
            yield i, j, "".join(out).rstrip()
            i = j
        else:
            i += 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rom = open(sys.argv[1], "rb").read()
    cdl = sm83.load_cdl(sys.argv[3:], len(rom))
    print("offset\tbank:addr\tread\ttext")
    for i, j, s in (runs_single(rom) if sys.argv[2] == "us" else runs_pairs(rom)):
        ns = [c for c in s if c != " "]
        if sum(c.isalpha() for c in ns) < 0.75 * len(ns) or len(set(ns)) < 5:   # tile/graphics data that happens to decode
            continue
        rd = sum(1 for k in range(i, j) if cdl[k] & 2)
        b, a = sm83.loc(i)
        print(f"{i:05X}\t{b:02X}:{a:04X}\t{'yes' if rd else 'no'}\t{' / '.join(s[k:k + 16].strip() for k in range(0, len(s), 16) if s[k:k + 16].strip())}")
