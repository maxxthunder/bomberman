"""Build the '94 ROM patches as IPS files: python tools/pce94/mkpatch.py  (writes patches/pce94_*.ips)
Each patch is checked against the ROM it is for: the bytes it replaces must be the expected originals.
IPS: 'PATCH', then records of 3-byte offset, 2-byte length, data, then 'EOF'."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
ROMS = {"jp": "Bomberman '94 (Japan).pce"}
STUB1 = "8908F0034CA2D8858DA908858CA9C48567A9B5856820EAEEA90160"
STUB2 = "A9448508A9D8850920FBC9A908858CA9118567A9B5856820EAEEA9668523A9DF8524A90160"
# name: (rom, [(file offset, original hex, new hex)], what it does)
PATCHES = {
    "pce94_debug_menu": ("jp", [(0x3F5B, "898567a99d", "298567a998")],
        "TCRF's patch: the Sound Room code ($DF54 far call) opens the BOMBERMAN94 DEBUG VERSION menu ($12:$9829)"),
    "pce94_debug_pause": ("jp", [(0x3F66, "ff" * (len(STUB1) // 2), STUB1), (0x3F82, "ff" * (len(STUB2) // 2), STUB2),
                                 (0x3891, "a99c85", "4c82df"), (0x389C, "8908d0", "4c66df")],
        "Restores the cut debug pause menu (INV_MODE, MAP_CLEAR, enemy editor): two stubs in free bank $01 space"
        " ($DF66 handler wrapper, $DF82 text printer) hooked into the pause slide-in ($D891) and paused handler ($D89C)"),
}


def ips(recs):
    out = bytearray(b"PATCH")
    for off, data in recs:
        out += off.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    return bytes(out + b"EOF")


def apply(rom, patch):
    rom = bytearray(rom)
    assert patch[:5] == b"PATCH"
    i = 5
    while patch[i:i + 3] != b"EOF":
        off, n = int.from_bytes(patch[i:i + 3], "big"), int.from_bytes(patch[i + 3:i + 5], "big")
        rom[off:off + n] = patch[i + 5:i + 5 + n]
        i += 5 + n
    return bytes(rom)


if __name__ == "__main__":
    for name, (ver, recs, what) in PATCHES.items():
        rom = open(os.path.join(ROOT, "roms", ROMS[ver]), "rb").read()
        r = []
        for off, old, new in recs:
            old, new = bytes.fromhex(old.replace(" ", "")), bytes.fromhex(new.replace(" ", ""))
            assert rom[off:off + len(old)] == old, (name, hex(off), rom[off:off + len(old)].hex())
            r.append((off, new))
        p = ips(r)
        assert apply(rom, p) != rom
        open(os.path.join(ROOT, "patches", name + ".ips"), "wb").write(p)
        print(name, len(p), "bytes:", what)
