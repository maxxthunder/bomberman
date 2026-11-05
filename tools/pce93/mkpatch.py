"""Build the '93 ROM patches as IPS files: python tools/pce93/mkpatch.py  (writes patches/pce93_*.ips)
Each patch is checked against the ROM it is for: the bytes it replaces must be the expected originals.
IPS: 'PATCH', then records of 3-byte offset, 2-byte length, data, then 'EOF'."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
ROMS = {"us": "Bomberman '93 (USA).pce", "jp": "Bomberman '93 (Japan).pce", "sp": "Bomberman '93 - Special Version (Japan).pce"}
# name: (rom, [(file offset, original hex, new hex)], what it does)
PATCHES = {
    "pce93_configration_us": ("us", [(0x4432, "08 20e7ea 9aab06", "00 20e7ea 208608")],
        "US: put back the far call to the CONFIGRATION screen (08:8620) after every planet map (02:8431)"),
    "pce93_normal_game_sp": ("sp", [(0xD84C, "4ea3", "a094")],
        "Special Version: title menu entry 0 opens the leftover password screen (06:94A0); a code starts the Normal Game"),
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
