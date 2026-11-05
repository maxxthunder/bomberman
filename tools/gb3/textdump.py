"""Text dump for Bomberman GB 3: the message texts drawn with the glyph font, with whether their bytes were read in
the Mesen runs (CDL data bit).
Usage: python tools/gb3/textdump.py <rom.gb> <cdl> [<cdl> ...] > disasm/gb3/text_jp.tsv
Font: $00:0880 draws character A by unpacking one tile (the $00:0DB2 mask format) from the glyph pointer table
$00:08AD, bank $0C below $70, bank 8 above; the table was read by rendering every glyph. $00-$32 hiragana (gojuon,
with ユ where ぬ would be, small っゃょゅ last), $33-$69 katakana mixed with punctuation, Ⓐ/Ⓑ/♡, $70-$79 digits.
Messages (reader $0A:67B8, table $0A:6905, 71 entries of text pointer + mark pointer): 32 characters (two lines of
16) and an 8-byte mark mask, 2 bits per character from bit 0: 3 = ゛, 2 = ゜. $C0 = blank.
Shop prompts (reader $0A:7B7B, table $0A:7CA6, 12 entries): 20 characters (two lines of 10) and 20 mark bytes, $AA ゛,
$AB ゜, $B0 none."""
import os, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sm83

FONT = ("　あいうえおかきくけこさしすせそたちつてとなにユねのはひふへほまみむめもやゆよらりるれろわんをっゃょゅ"
        "アー「」。゛!イウエオカキクケコサシスセソタチツテトナニ・ネノハヒフヘホマⒶム♡モィミロラリルレ?ワンッャュヨⒷ゛゜/.‾"
        "0123456789")
T = dict(enumerate(FONT))
T[0xC0] = "　"


def mark(c, m):
    if m in (2, 3):
        n = unicodedata.normalize("NFC", c + ("゙" if m == 3 else "゚"))
        return n if len(n) == 1 else c + "゛゜"[m == 2]
    return c


def text(chars, marks, width):
    s = "".join(mark(T.get(b, "{%02X}" % b), m) for b, m in zip(chars, marks))
    return " / ".join(s[k:k + width].rstrip("　") for k in range(0, len(s), width) if s[k:k + width].strip("　"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rom = open(sys.argv[1], "rb").read()
    cdl = sm83.load_cdl(sys.argv[2:], len(rom))
    f = lambda a: 0xA * 0x4000 + a - 0x4000
    w = lambda o: rom[o] | rom[o + 1] << 8
    rows = []
    for k in range(71):
        t, m = f(w(f(0x6905 + 4 * k))), f(w(f(0x6905 + 4 * k + 2)))
        mk = [(rom[m + i // 4] >> (2 * (i % 4))) & 3 for i in range(32)]
        rows.append((t, 32, m, 8, "message %d: %s" % (k, text(rom[t:t + 32], mk, 16))))
    for k in range(12):
        t, m = f(w(f(0x7CA6 + 4 * k))), f(w(f(0x7CA6 + 4 * k + 2)))
        mk = [{0xAA: 3, 0xAB: 2}.get(b, 0) for b in rom[m:m + 20]]
        rows.append((t, 20, m, 20, "shop %d: %s" % (k, text(rom[t:t + 20], mk, 10))))
    print("offset\tbank:addr\tread\ttext")
    for t, n, m, mn, s in sorted(rows):
        b, a = sm83.loc(t)
        rd = any(cdl[i] & 2 for i in range(t, t + n))
        print(f"{t:05X}\t{b:02X}:{a:04X}\t{'yes' if rd else 'no'}\t{s}")
