"""Write the nes1 IPS patches: python tools/nes1/mkpatch.py  -> patches/nes1_invincible_us.ips, _jp.ips
Invincible: `LDA $7A` (A5 7A, the invincibility timer) -> `LDA #$7A` (A9 7A) in the fire check and the enemy-contact
check, so both always take the 'invincible' branch. Same bytes as the Game Genie codes in docs/nes1_codes.json."""
import os

PATCH = {"us": [0xC6E9, 0xD06F], "jp": [0xC6E1, 0xD067]}
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


def ips(records):
    out = b"PATCH"
    for off, data in records:
        out += off.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    return out + b"EOF"


for reg, addrs in PATCH.items():
    rom = open(os.path.join(root, "roms", "Bomberman (%s).nes" % ("USA" if reg == "us" else "Japan")), "rb").read()
    recs = []
    for a in addrs:
        off = 16 + a - 0xC000
        assert rom[off:off + 4] == b"\xa5\x7a\xd0\x18", (reg, hex(a))
        recs.append((off, b"\xa9"))
    open(os.path.join(root, "patches", "nes1_invincible_%s.ips" % reg), "wb").write(ips(recs))
    print(reg, [hex(16 + a - 0xC000) for a in addrs])
