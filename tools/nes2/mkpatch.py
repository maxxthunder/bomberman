"""Write the nes2 IPS patches: python tools/nes2/mkpatch.py  -> patches/nes2_invincible_us.ips, _jp.ips
Invincible: RTS over the two kill routines in the fixed bank (US $CEA4 fire / $CEC4 enemy contact; JP $CE10 / $CE30),
which start `LDA $04E6` (AD E6 04, the invincibility timer). Same bytes as the Game Genie codes in docs/nes2_codes.json."""
import os

PATCH = {"us": [0xCEA4, 0xCEC4], "jp": [0xCE10, 0xCE30]}
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
for reg, addrs in PATCH.items():
    rom = open(os.path.join(root, "roms", "Bomberman II (%s).nes" % ("USA" if reg == "us" else "Japan")), "rb").read()
    out = b"PATCH"
    for a in addrs:
        off = 16 + 7 * 0x4000 + a - 0xC000
        assert rom[off:off + 3] == b"\xad\xe6\x04", (reg, hex(a))
        out += off.to_bytes(3, "big") + b"\x00\x01\x60"
    open(os.path.join(root, "patches", "nes2_invincible_%s.ips" % reg), "wb").write(out + b"EOF")
    print(reg, [hex(16 + 7 * 0x4000 + a - 0xC000) for a in addrs])
