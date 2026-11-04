"""Write patches/sb1_debug_menu_<us|eu|jp|beta>.ips: restores the debug menu (Select during a stage).

What is missing in every dump, and what the patch adds (hook code in the zero-filled $C6:7F00-$C6:7F5F):
  1. Nothing opens the menu. The pause object's Start check $C6:0081 already accepts Select ($0CF9 & $30);
     the hook sends Select to the uncalled toggle $C6:00D2 (open/close) and Start to the normal pause $C6:001B.
  2. Nothing runs the menu's input handler $C6:01B9 (also uncalled); the hook calls it every frame the menu is open.
  3. Nothing uploads the menu: the main loop's VRAM step (JSL $C6:2460) is extended with the uncalled
     $C4:0B6F, which DMAs $7E:2180 to VRAM $58C0 while $0314 bit 0 is set.
  4. NO DEATH sets player +$2E, which nothing reads any more. This part is a reconstruction, not original code:
     both hit branches of the player routine (JML to the death routine, $C4:138B and $C4:13F3 in US) go through
     a 14-byte check that drops the hit ($2F = 0) and carries on as after a heart-shield save while +$2E is set.
Each patch is checked against its ROM first. Also prints the patch as Pro Action Replay ROM codes (AAAAAADD).
Usage: python tools/sb1/make_debug_ips.py [roms_dir] [patches_dir] [patched_rom_dir]"""
import os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
ROMS = {"us": "Super Bomberman (USA).sfc", "eu": "Super Bomberman (Europe).sfc", "jp": "Super Bomberman (Japan).sfc",
        "beta": "Super Bomberman (USA) (Beta) (1993-05-11).sfc"}
# main-loop JSL $C62460 and the VRAM upload routine move with the multitap library; bank $C6 is identical in all four
MAIN = {"us": 0xC4035D, "eu": 0xC4035D, "jp": 0xC401D4, "beta": 0xC401CF}
UPLOAD = {"us": 0xC40B6F, "eu": 0xC40B6F, "jp": 0xC40965, "beta": 0xC40960}
HOOK, VHOOK, NDHOOK = 0xC67F00, 0xC67F30, 0xC67F40
HIT = bytes.fromhex("b539 8980 d004 5c")  # LDA $39,X / BIT #$80 (heart shield) / BNE / JML die ... 24 bytes to the code after
UPLOAD_CODE = bytes.fromhex("e220ad1403 29df 8d1403 2901 f021 c220a9c058 8d1621")  # $C4:0B6F, first 22 bytes


def long(a):
    return bytes([a & 255, a >> 8 & 255, a >> 16])


def hook():  # entered by JML from $C6:0011 (pause object, A 8-bit, X = object, index 16-bit)
    c = bytes.fromhex("ad1403 8901 f006") + b"\x22" + long(0xC601B9) + bytes.fromhex("e220")  # menu open: run its input handler
    c += b"\x22" + long(0xC60081)  # A = new presses of the first player who pressed Start or Select, Y = player*$40, carry
    rest = bytes.fromhex("8920 d00b ad1403 8901 d008") + b"\x5c" + long(0xC6001B) + b"\x5c" + long(0xC600D2) + b"\x6b"
    return c + bytes.fromhex("90%02x" % (len(rest) - 1)) + rest  # BCC -> RTL; Select -> toggle menu; Start (menu shut) -> pause


def records(ver, rom):
    o = lambda a: a - 0xC00000
    assert rom[o(0xC60011):o(0xC60019)] == bytes.fromhex("22810 0c6 b004".replace(" ", "")) + b"\x5c\x44", ver
    assert rom[o(MAIN[ver]):o(MAIN[ver]) + 4] == b"\x22" + long(0xC62460), ver
    assert rom[o(UPLOAD[ver]):o(UPLOAD[ver]) + len(UPLOAD_CODE)] == UPLOAD_CODE, ver
    assert not any(rom[o(HOOK):o(HOOK) + 0x40]), ver
    vh = b"\x22" + long(0xC62460) + b"\x22" + long(UPLOAD[ver]) + b"\x6b"
    recs = [(o(0xC60011), b"\x5c" + long(HOOK)), (o(MAIN[ver]), b"\x22" + long(VHOOK)), (o(HOOK), hook()), (o(VHOOK), vh)]
    sites = [i for i in range(o(0xC40000), o(0xC50000)) if rom[i:i + 7] == HIT]
    assert len(sites) == 2, ver
    for k, i in enumerate(sites):
        die, cont, nd = rom[i + 7] | rom[i + 8] << 8 | rom[i + 9] << 16, 0xC00000 + i + 24, NDHOOK + 16 * k
        assert rom[i + 10:i + 24] == bytes.fromhex("297f 9539 742f a9a0 9536 a902 9537"), ver
        # LDA $2E,X / BNE +4 / JML die / STZ $2F,X / JML cont
        recs += [(i + 7, long(nd)), (o(nd), bytes.fromhex("b52e d004") + b"\x5c" + long(die) + bytes.fromhex("742f") + b"\x5c" + long(cont))]
    return recs


def ips(recs):
    out = b"PATCH"
    for off, data in recs:
        out += off.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    return out + b"EOF"


def apply(rom, patch):  # minimal IPS reader, for the self-check
    rom, i = bytearray(rom), 5
    while patch[i:i + 3] != b"EOF":
        off, n = int.from_bytes(patch[i:i + 3], "big"), int.from_bytes(patch[i + 3:i + 5], "big")
        rom[off:off + n] = patch[i + 5:i + 5 + n]
        i += 5 + n
    return bytes(rom)


def par(recs):
    return [f"{0xC00000 + off + k:06X}{b:02X}" for off, data in recs for k, b in enumerate(data)]


if __name__ == "__main__":
    roms = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "roms")
    outd = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "patches")
    romd = sys.argv[3] if len(sys.argv) > 3 else None
    assert hook()[-1] == 0x6B and len(hook()) <= 0x30
    for ver, name in ROMS.items():
        rom = open(os.path.join(roms, name), "rb").read()
        recs = records(ver, rom)
        p = ips(recs)
        out = apply(rom, p)
        assert sum(a != b for a, b in zip(rom, out)) <= sum(len(d) for _, d in recs)
        path = os.path.join(outd, f"sb1_debug_menu_{ver}.ips")
        open(path, "wb").write(p)
        if romd:
            open(os.path.join(romd, f"sb1_debug_{ver}.sfc"), "wb").write(out)
        print(path, len(p), "bytes; PAR:", " ".join(par(recs)))
