"""Decode the ending's staff-roll script (the only encoded text in Mega Bomberman; every other word on screen is
drawn as graphics). Usage: text.py rom.md [start_hex]   (USA $16A8C, Europe $16A86)

Script, read by $16880 / $1691e through $BE40:
  block:  F D T   F = flags (bit 7 clear; bit 0 = second font, bit 1 = scroll position, bit 2 = no sound
                  cue), D = frames to wait before it, T = frames it stays; then commands until 00:
    01 r c   cursor to row (r + 6) & 31, column c & 31 (plane A at $E000)
    23 h     '#' + hex digit: palette line (h & 3)
    20       blank; 41-5A letters A-Z, drawn as 2 tiles: (c - $41) * 2 (+ $80 unless font bit set) over +1
  80 n     wait n frames and continue; 81-FF: end (the reader keeps re-reading that byte)
"""
import sys
d = open(sys.argv[1], 'rb').read(); p = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x16A8C
blocks = []
while True:
    f = d[p]; p += 1
    if f & 0x80:
        if f & 0x7F: print('%06X  end (%02X: the reader stops here)' % (p - 1, f)); break
        print('%06X  pause %d' % (p - 1, d[p])); p += 1; continue
    dly, t = d[p], d[p + 1]; p += 2; lines = []; cur = ''; pos = None; s0 = p
    while True:
        c = d[p]; p += 1
        if c == 0: break
        if c == 1:
            if cur: lines.append((pos, cur))
            pos = (d[p], d[p + 1]); p += 2; cur = ''
        elif c == 0x23: cur += '{pal %s}' % chr(d[p]); p += 1
        else: cur += chr(c)
    if cur: lines.append((pos, cur))
    print('%06X  flags %02X wait %3d show %3d  ' % (s0 - 3, f, dly, t) + ' | '.join('@r%d,c%d %s' % ((x + 6) & 31, y & 31, s) for (x, y), s in lines))
