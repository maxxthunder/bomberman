"""Write patches/sb3_soft_reset_<version>.ips: hooks up the unreferenced soft-reset check at $C0:013A
(LDA $4E / CMP #$33 / BNE / JML $80F000 = Select+Start+L+R on pad 1 jumps to the reset routine).
Nothing calls it in any dump. The patch rewrites the tail of the per-frame pad routine $C0:0094
(PLX / PLY / RTL at $C0:0137) so the check runs right after it:
    $C0:0137  PLX / PLY / LDA $4E / CMP #$33 / BNE +4 / JML $80F000 / RTL
Same offset in EU, JP and the beta; each patch is checked against its ROM first.
Usage: python tools/sb3/make_ips.py [roms_dir] [patches_dir]"""
import os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
ROMS = {"eu": "Super Bomberman 3 (Europe).sfc", "jp": "Super Bomberman 3 (Japan).sfc", "beta": "Super Bomberman 3 (Europe) (Beta).sfc"}
OFF = 0x137
OLD = bytes.fromhex("fa7a6b" "a54e" "c933" "d004" "5c00f080" "60")
NEW = bytes.fromhex("fa7a" "a54e" "c933" "d004" "5c00f080" "6b")


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
        assert rom[OFF:OFF + len(OLD)] == OLD, f"{ver}: pad routine tail not found at ${OFF:05X}"
        p = ips([(OFF, NEW)])
        out = apply(rom, p)
        assert out[OFF:OFF + len(OLD)] == NEW + OLD[-1:] and len(out) == len(rom)
        path = os.path.join(outd, f"sb3_soft_reset_{ver}.ips")
        open(path, "wb").write(p)
        print(path, len(p), "bytes")
