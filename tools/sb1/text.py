"""Dump every text string in a ROM for a given character map, and mark the ones no code/data log ever read.
  python tools/sb1/text.py <rom> <map> [cdl...]
<map>: 'sb1' (the debug font: A-Z = $01-$1A, 0-9 = $20-$29, '.' $1C, ':' $1E, '-' $34, ' ' $36),
       'ascii', or a python file defining CHARS = {byte: char} (and optional MIN = shortest run).
A run counts as text when it is at least MIN mapped bytes long with 3+ letters. Read = any byte of the run
has the CDL data bit (or code bit) set in the merged logs (tools/sb1/sweep.py load_cdl)."""
import os, runpy, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep import load_cdl

SB1 = {i + 1: chr(65 + i) for i in range(26)}
SB1.update({0x20 + i: str(i) for i in range(10)})
SB1.update({0x1C: ".", 0x1E: ":", 0x34: "-", 0x36: " "})
ASCII = {i: chr(i) for i in range(0x20, 0x7F)}


def wordy(s):
    """Text, not graphics or code: a 3+ letter word with a vowel, and no single character over 40%."""
    import re
    t = s.replace(" ", "")
    if len(t) < 3 or max(t.count(ch) for ch in set(t)) > 0.4 * len(t):
        return False
    return any(re.search("[AEIOUaeiou]", w) and len(w) >= 3 for w in re.findall("[A-Za-z]+", s))


def strings(rom, chars, minlen, stride=1):
    """stride 2 = tilemap words: the low byte is the character, the high byte (attributes) stays the same."""
    out = []
    for ph in range(stride):
        i = ph
        while i < len(rom):
            j = i
            while j < len(rom) and rom[j] in chars and (stride == 1 or (j + 1 < len(rom) and rom[j + 1] == rom[i + 1])):
                j += stride
            s = "".join(chars[b] for b in rom[i:j:stride])
            if len(s) >= minlen and wordy(s):
                out.append((i, s))
            i = j + stride if j == i else j
    return sorted(out)


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    m = sys.argv[2]
    minlen, stride = 6, 1
    if m == "sb1":
        chars = SB1
    elif m == "ascii":
        chars, minlen = ASCII, 8
    else:
        g = runpy.run_path(m)
        chars, minlen, stride = g["CHARS"], g.get("MIN", 6), g.get("STRIDE", 1)
    c = load_cdl(rom, sys.argv[3:])[0] if len(sys.argv) > 3 else None
    n = un = 0
    for o, s in strings(rom, chars, minlen, stride):
        read = c is not None and any(c[k] & 3 for k in range(o, o + len(s) * stride))
        n += 1
        un += not read
        mark = "" if c is None else ("  " if read else "U ")
        print(f"{mark}${0xC00000 + o:06X} {s.rstrip()!r}")
    print(f"# {n} strings" + ("" if c is None else f", {un} never read (U)"))
