"""Write patches/sb2_debug_menu_<version>.ips: turns on the disabled debug-menu switch at $C1:5B3E
(LDA #$0000 / BNE -> LDA #$0100), i.e. ROM offset $15B40 = $01, the same byte as PAR code C15B4001.
The switch is at the same offset in all five dumps; each patch is checked against its ROM first.
Usage: python tools/sb2/make_ips.py [roms_dir] [patches_dir]"""
import os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
ROMS = {"us": "Super Bomberman 2 (USA).sfc", "eu": "Super Bomberman 2 (Europe).sfc", "jp": "Super Bomberman 2 (Japan) (En).sfc",
        "beta": "Super Bomberman 2 (USA) (Beta).sfc", "caravan": "Super Bomberman 2 (Japan) (Caravan You Taikenban).sfc"}
OFF, WANT = 0x15B3E, bytes.fromhex("a90000d0016b")  # LDA #$0000 / BNE +1 / RTL


def ips(records):
    out = b"PATCH"
    for off, data in records:
        out += off.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    return out + b"EOF"


def apply(rom, patch):  # minimal IPS reader, for the self-check
    rom, i = bytearray(rom), 5
    while patch[i:i + 3] != b"EOF":
        off, n = int.from_bytes(patch[i:i + 3], "big"), int.from_bytes(patch[i + 3:i + 5], "big")
        rom[off:off + n] = patch[i + 5:i + 5 + n]
        i += 5 + n
    return bytes(rom)


if __name__ == "__main__":
    roms = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "roms")
    outd = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "patches")
    os.makedirs(outd, exist_ok=True)
    for ver, name in ROMS.items():
        rom = open(os.path.join(roms, name), "rb").read()
        assert rom[OFF:OFF + 6] == WANT, f"{ver}: switch not found at ${OFF:05X}"
        p = ips([(OFF + 2, b"\x01")])
        out = apply(rom, p)
        assert out[OFF:OFF + 6] == bytes.fromhex("a90001d0016b") and sum(a != b for a, b in zip(rom, out)) == 1
        path = os.path.join(outd, f"sb2_debug_menu_{ver}.ips")
        open(path, "wb").write(p)
        print(path, len(p), "bytes")
