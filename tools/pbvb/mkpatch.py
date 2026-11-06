"""Write patches/pbvb_dev_menu.ips: python tools/pbvb/mkpatch.py
Panic Bomber (USA) has an unused developer menu at $0700_0A48 (VERSION 1995/07/21: GAME START, DEBUG GAME PLAY,
DEBUG AUTO PLAY, SOUND TEST, ENDING) that nothing calls. The patch calls it at power-on and points its three debug
items at the sub-mode word the finished game reads ($0500_24F8; the menu still wrote the old byte $0500_26D9)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "emu"))
from ips import ips, apply  # noqa: E402

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
RECS = [  # (file offset, original, patched)
    (0x06B2, "e1 41 e4 d1 d6 a6 ba 8b", "00 ac 96 03 bc 8b 00 00"),   # boot mode 0: JAL $0A48, BR back, instead of "mode 1"
    (0x0D09, "d1 d9 a6", "dd f8 a4"),   # DEBUG GAME PLAY: STB $26D9 -> STW $24F8
    (0x0D37, "d1 d9 a6", "dd f8 a4"),   # DEBUG AUTO PLAY
    (0x0D63, "d0 d9 a6", "dc f8 a4"),   # SOUND TEST
]
rom = open(os.path.join(root, "roms", "Panic Bomber (USA).vb"), "rb").read()
for off, old, _ in RECS:
    assert rom[off:off + len(bytes.fromhex(old))] == bytes.fromhex(old), hex(off)
patch = ips([(off, bytes.fromhex(new)) for off, _, new in RECS])
assert apply(rom, patch)[0x6B2:0x6BA] == bytes.fromhex(RECS[0][2])
open(os.path.join(root, "patches", "pbvb_dev_menu.ips"), "wb").write(patch)
print("patches/pbvb_dev_menu.ips", len(patch), "bytes")
