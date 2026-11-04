"""Write patches/sb5_debug_rooms.ips (retail ROM): three new option passwords that jump to the debug rooms.
  0172 -> scene $AC (battle test), 0173 -> $AD (level test), 0174 -> $AE (enemy test)
The option password walker ($C5:6836) reads its table at $C5:6875. The patch copies that table to free space
at $C5:6FA0, adds the three entries, and points the walker's five operands at the copy. Each new handler
does what 1999/0803 do (bit $80 via $C5:6909, so the session isn't saved) and stores the scene in $6248.
Usage: python tools/sb5/make_ips.py [rom] [out.ips]"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sb2"))
from make_ips import ips, apply  # noqa: E402  (same minimal IPS writer/reader)

OLD, NEW, HAND = 0x56875, 0x56FA0, 0x56FF0   # file offsets (bank $C5 = file $50000)
CODES = {"0172": 0xAC, "0173": 0xAD, "0174": 0xAE}


def build(rom):
    table = rom[OLD:OLD + 60]
    assert rom[OLD + 60] == 0x0A and rom[NEW:HAND + 12 * len(CODES)] == b"\xff" * (HAND + 12 * len(CODES) - NEW)
    recs, handlers = [], b""
    for i, (code, scene) in enumerate(CODES.items()):
        h = 0x6FF0 + 12 * i
        table += bytes(int(c) for c in code) + h.to_bytes(2, "little")
        handlers += bytes([0xA9, 0x80, 0x20, 0x09, 0x69, 0xA9, scene, 0x8F, 0x48, 0x62, 0x7E, 0x60])
    recs.append((NEW, table + b"\x0a"))
    recs.append((HAND, handlers))
    for op_off, field in ((0x5683A, 0), (0x56848, 1), (0x56852, 2), (0x5685C, 3), (0x56866, 4)):
        assert rom[op_off:op_off + 2] == (0x6875 + field).to_bytes(2, "little")
        recs.append((op_off, (0x6FA0 + field).to_bytes(2, "little")))
    return ips(recs)


if __name__ == "__main__":
    rom = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "roms", "Super Bomberman 5 (Japan).sfc"), "rb").read()
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "..", "patches", "sb5_debug_rooms.ips")
    p = build(rom)
    new = apply(rom, p)
    assert new[0x56FA0:0x56FA0 + 60] == rom[OLD:OLD + 60] and new[0x56FA0 + 78] == 0x0A
    open(out, "wb").write(p)
    print(out, len(p), "bytes")
