"""Text dump for Bomberman GB (JP) / Wario Blast: the script texts and the plain tile strings, with whether their
bytes were read in the Mesen runs (CDL data bit).
Usage: python tools/gb1/textdump.py <rom.gb> <cdl> [<cdl> ...] > disasm/gb1/text_<ver>.tsv
Font (from VRAM on the story and title screens): $C0 space; kana screens $C1-$EF ア-ン in gojuon order with ー at
$D0, $F0-$F5 ャュョィェッ, $F6 ゛ and $F8 ゜ (drawn on the row above), $F7 !, $F9 ", $FA ・, $FB ., $FC ?;
Latin $E0-$E9 0-9, $EA-$FF A-V, $CD-$CF W-Y, $DD Z, $D0 -, $DE !, and the same Latin set $40 lower ($AA = A) where
it shares the screen with kana.
Scripts (reader in bank 4, $04:45E3 JP; pointer table $04:467B, 17 entries, JP / $04:4B8C, 14, Wario): records of 5 bytes (JP:
frames to wait, VRAM address, the tile above (mark) and the character) or 4 (Wario, no mark); address $FFFF = wait
only; $FE waits for A/Start and clears, $FF ends. "read" = at least half the bytes have the CDL data bit. Plain strings: runs of Latin codes kept when they hold a word of WORDS (read off the raw scan; graphics data
decodes as letters too, so a run without one is dropped)."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sm83

KANA = "アイウエオカキクケコサシスセソータチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンャュョィェッ゛!゜\"・.?"
LAT = {0: " ", 0xD: "W", 0xE: "X", 0xF: "Y", 0x10: "-", 0x1D: "Z", 0x1E: "!", 0x1F: '"'}
LAT.update({0x20 + i: str(i) for i in range(10)})
LAT.update({0x2A + i: chr(65 + i) for i in range(22)})
K = {0xC0: " "}
K.update({0xC1 + i: c for i, c in enumerate(KANA)})
K.update({0x80 + k: v for k, v in LAT.items()})   # Latin on kana screens
L = {0xC0 + k: v for k, v in LAT.items()}
# Each script screen loads its own font arrangement; these are the codes each script uses, read off the VRAM tile
# data at the moment the record was drawn (Mesen, every script shown; matched against the story/title glyphs).
# Two hex digits + one character per entry; codes not listed fall back to K.
FONTS = {
    0: "C4エC5オC6カC7キC8クCCシCDスD1タD5トDFホE3ムEAリEFヲF5ッF6゛F7!F8\"",
    1: "C4エC5オC6カCCシCDスD1タD5トDFホEAリEFヲF2ュF5ッF6゛F7!F8\"",
    2: "C4エC5オC6カC8クCCシCDスD1タD5トDFホEAリEBルEFヲF5ッF6゛F7!F8\"",
    3: "C2イC4エC5オC6カCCシCDスD1タD5トDFホE3ムE9ラEAリEFヲF0ンF6゛F7!F8\"",
    4: "C4エC5オC6カCCシCDスD0ーD1タD5トDBハDFホE5モEAリEFヲF0ンF6゛F7!F8\"",
    5: "ACオB8タBBテBCトC7キC8クCAコCCシCDスCEセDBハDFホE3ムE4メE5モEBルEFヲF0ンF5ッF6゛F9.FCBFE・",
    6: "A8アA9イAAウACオADカB8タBBテBCトBDナC7キC8クC9ケCAコCCシCDスDBハDFホE6ヤE9ラEBルEFヲF0ンF2ュF5ッF6゛F9.FCBFE・",
    7: "A8アA9イAAウACオADカB8タB9チBAツBBテBCトC8クCBサCCシD7ニDBハDDフDEヘE1マEBルECレEFヲF2ュF5ッF6゛F9.FE・",
    8: "A9イAAウACオADカB8タB9チBBテBCトC7キC9ケCCシCDスD7ニDDフDFホE3ムE5モE9ラEBルEFヲF0ンF5ッF6゛F9.FBAFE・",
    9: "ABエACオADカB8タBBテBCトBDナC7キC8クC9ケCAコCDスD0ーDBハDCヒDDフDFホE5モE9ラEBルEDロEFヲF0ンF5ッF6゛F9.FA+FE・FF1",
    10: "C5オCCシCDスD1タDFホEFヲF6゛F7!",
    11: "C2イC5オC6カC8クCAコCDスD1タD3ツD4テDBハEEワEFヲF0ンF5ッF6゛F7!FE・",
    13: "8FYABBADDAEEAFFB1HB7NB8OB9PBBRBCSBDTBEUC1アC2イC3ウC4エC5オC6カC7キC8クC9ケCAコCBサCCシCDスCEセD0ーD1タD3ツD4テD5トD6ナDAノDBハDCヒDDフDEヘDFホE0マE1ミE2ムE4モE5ヤE6ユE7ヨE8ラE9リEAルEBレECロEDワEFンF0ャF1ュF2ョF3ィF5ッF6゛F8゜FA・",
    14: "C3ウC7キD0ーD1タD4テD5トD7ニDAノDBハDFホE0マE4モEAルECロEFンF2ョF5ッF6゛F7!F8゜FA・",
    15: "C1アC2イC6カC7キC8クCCシCDスD0ーD1タD2チD5トD7ニDBハDCヒDDフDFホE0マE2ムE4モE8ラEAルEFンF1ュF5ッF6゛F8゜FA・",
    16: "C1アC3ウC4エC6カC8クCBサCCシCDスCEセD0ーD1タD2チD4テD5トD7ニDAノDBハDDフDEヘDFホE0マE8ラE9リEBレEDワEEヲEFンF5ッF6゛F7!FA・",
}
FONTS_W = {
    0: "CBACCBCDCCEDCFED3ID5KD6LD9ODCRDDSDETE0VE7.EC:",
    1: "CBACCBCDCCEDCFED2HD3ID6LD8ND9ODCRDDSDETE0VE7.EC:",
    2: "CBACCBCDCCEDCFED2HD3ID6LD8ND9ODCRDDSDETDFUE0VE7.EC:",
    3: "CBACCBCDCCEDCFED3ID6LD8ND9ODCRDDSDETE0VE7.EC:",
    4: "CBACCBCDCCEDCFED3ID6LD7MD9ODCRDDSDETE0VE7.EC:",
    5: "D0ーD8AD9BDACDBDDCEDFHE0IE2KE3LE4ME5NE6OE9REASEBTECUEEWF4.F5\"",
    6: "D0ーD8AD9BDACDBDDCEDEGDFHE0IE3LE5NE6OE7PE9REASEBTECUEEWF0YF4.F5\"",
    7: "D8AD9BDACDBDDCEDFHE0IE4ME5NE6OE9REASEBTECUEEWF4.F5\"",
    8: "D0ーD8AD9BDBDDCEDDFDFHE0IE1JE3LE4ME5NE6OE7PE9REASEBTECUEEWF4.F5\"",
    9: "D8AD9BDACDBDDCEDEGE0IE1JE2KE3LE4ME5NE6OE7PE9REASEBTECUF0YF4.F5\"",
    11: "CBACDCCFED0FD1GD2HD3ID5KD6LD8ND9ODAPDBQDCRDDSDETDFUE0VE2XE3YE7.",
    13: "CBACCBCDCCEDCFED0FD1GD2HD3ID4JD5KD6LD7MD8ND9ODAPDCRDDSDETDFUE0VE1WE3YE4ZE7.E9・EAーED,",
}
FONTS_W[10] = FONTS_W[0]   # read in the runs but not caught by the tile log; the boss-clear screen's font
FONTS, FONTS_W = ({k: {int(v[i:i + 2], 16): v[i + 2] for i in range(0, len(v), 3)} for k, v in f.items()} for f in (FONTS, FONTS_W))
DAK = {c: chr(ord(c) + 1) for c in "カキクケコサシスセソタチツテトハヒフヘホ"}
DAK["ウ"] = "ヴ"
HAN = {c: chr(ord(c) + 2) for c in "ハヒフヘホ"}


def script(rom, o, font=None, size=5):
    """decode one script from rom offset o -> (end offset, text with ' / ' between lines, '|' at page breaks).
    size 5: delay, address, mark, character (JP); size 4: delay, address, character (Wario, no marks)"""
    rows, out = {}, []
    def flush():
        if rows:
            out.append(" / ".join("".join(rows[r][c] for c in sorted(rows[r])).strip() for r in sorted(rows)))
        rows.clear()
    while rom[o] != 0xFF:
        if rom[o] == 0xFE:
            flush(); o += 1; continue
        a, c = rom[o + 1] | rom[o + 2] << 8, rom[o + size - 1]
        if a != 0xFFFF:
            ch = (font or {}).get(c) or K.get(c, "{%02X}" % c)
            if size == 5:
                mk = (font or {}).get(rom[o + 3]) or K.get(rom[o + 3])
                ch = DAK.get(ch, ch) if mk == "゛" else HAN.get(ch, ch) if mk == "゜" else ch
            rows.setdefault((a - 0x9C00) // 32, {})[(a - 0x9C00) % 32] = ch
        o += size
    flush()
    return o + 1, " | ".join(p for p in out if p)


WORDS = set("START PASSWORD HUDSON SOFT LICENSED NINTENDO TIME ROUND PAUSE ENEMY BOSS DRAW GAME YOU LOSE WIN "
             "CONTINUE END NORMAL BATTLE PERFECT CONGRATULATIONS TECHNIQUE SELECT PLAYER VICTORY OVER WARIO "
             "BOMBERMAN".split())


def strings(rom):
    i = 0
    while i < len(rom):
        j = i
        while j < len(rom) and rom[j] in L:
            j += 1
        s = "".join(L[b] for b in rom[i:j])
        w = re.findall("[A-Z]+", s)
        if any(x in s for x in WORDS):
            yield i, j, s.strip()
        i = max(j, i + 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rom = open(sys.argv[1], "rb").read()
    cdl = sm83.load_cdl(sys.argv[2:], len(rom))
    rows = []
    wario = rom[0x134:0x13F] == b"WARIO BLAST"
    tab, n, size, fonts = (0x10B8C, 14, 4, FONTS_W) if wario else (0x1067B, 17, 5, FONTS)
    for k in range(n):
        p = 4 * 0x4000 + (rom[tab + 2 * k] | rom[tab + 2 * k + 1] << 8) - 0x4000
        e, s = script(rom, p, fonts.get(k), size)
        rows.append((p, e, "script %d: %s" % (k, s)))
    for i, j, s in strings(rom):
        rows.append((i, j, s))
    print("offset\tbank:addr\tread\ttext")
    for i, j, s in sorted(rows):
        b, a = sm83.loc(i)
        print(f"{i:05X}\t{b:02X}:{a:04X}\t{'yes' if any(cdl[k] & 2 for k in range(i, j)) else 'no'}\t{s}")
