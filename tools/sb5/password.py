"""Super Bomberman 5 passwords.
Config Battle character password: 6 symbols, 30 bits, decoder $C5:6530, encoder $C5:6545.
Option passwords: 4 digits, table $C5:6875 (retail) / $C5:688D (Caravan).
Usage: python password.py CODE...   (6-symbol or 4-digit)
       python password.py -e body color bomb fire speed items   (items as 9 bits, item 0 first, e.g. 100011101)"""
import sys

ALPHA = "0123456789ABCDEFGHJKLMNPQRTUVWXY"  # value order; the entry grid shows A-Y first, then 1-9, 0
BODY = ["Bomberman", "Bomber Woof", "Dave Bomber", "Gary Bomber", "Pirate Bomber", "Muscle Bomber",
        "Iron Mask Bomber", "Baron Bombano", "Plunder Bomber", "Subordinate Bomber"]


ITEMS = ["Remote control", "Pierce bomb", "Land mine", "Homing bomb", "Bomb pass", "Soft-block pass", "Power glove", "Kick", "Punch"]
COLORS = ["white", "black", "red", "blue", "green", "yellow", "burnt (unused)", "boss (unused)"]
# option passwords: code -> effect, per version ("retail", "caravan")
OPTION = {
    "4622": "battle: start positions moved in to the centre ($6246=1)",
    "0413": "battle: alternate hard-block / item layouts ($6246=2)",
    "0926": "battle: start positions moved in, less open space ($6246=3)",
    "1103": "battle: adds SUPER to COM LEVEL ($6247=4, saved to SRAM)",
    "0110": "battle: every soft block holds a power-up",
    "2657": "normal: start with 8 bombs, 8 fire and max speed",
    "5656": "normal: 9 lives and an 8:00 timer",
    "3879": "boss rush (normal mode bosses back to back)",
    "1999": "watch the good ending",
    "0803": "watch the bad ending",
}
OPTION_CARAVAN = dict(OPTION, **{
    "0719": "boss rush, starting fully powered ($6272=1)",
    "4737": "battle: everyone starts fully powered ($6293=1)",
})


def option(code, version="retail"):
    """Effect of a 4-digit option password, or None if the game rejects it."""
    return (OPTION_CARAVAN if version == "caravan" else OPTION).get(code)


def checksum(b):  # $C5:6759: sum of all nibbles of the 26 data bits, mod 16
    s = 0
    for x in b:
        s = (s + x + (x >> 4)) & 15
    return s


def encode(body, color, bomb, fire, speed, items):
    """Fields as the game stores them ($62DE $62DF $62E6 $62E7 $62E8, items $62E9-$62F1 as a 9-bit int)."""
    v = (body & 15) | (color & 7) << 4 | (bomb & 7) << 7 | (fire & 15) << 10 | (speed & 7) << 14 | (items & 0x1FF) << 17
    b = [v >> (8 * i) & 255 for i in range(4)]
    b[3] |= checksum(b) << 2
    w = sum((x ^ 0xCB) << (8 * i) for i, x in enumerate(b))
    return "".join(ALPHA[w >> (5 * i) & 31] for i in range(6))


def decode(code):
    """-> dict of fields, or None if the game rejects it (bad symbol or checksum)."""
    code = code.upper()
    if len(code) != 6 or any(c not in ALPHA for c in code):
        return None
    w = sum(ALPHA.index(c) << (5 * i) for i, c in enumerate(code))
    b = [(w >> (8 * i) & 255) ^ 0xCB for i in range(4)]
    ck, b[3] = b[3] >> 2 & 15, b[3] & 3
    if checksum(b) != ck:
        return None
    v = b[0] | b[1] << 8 | b[2] << 16 | b[3] << 24
    return dict(body=v & 15, color=v >> 4 & 7, bomb=v >> 7 & 7, fire=v >> 10 & 15, speed=v >> 14 & 7, items=v >> 17 & 0x1FF)


if __name__ == "__main__":
    assert decode("D24GJN") == dict(body=6, color=0, bomb=7, fire=6, speed=7, items=0b101110001)
    assert decode("UO4GJL") is None and decode("U04GJL")["color"] == 5 and option("0719") is None and option("0719", "caravan")
    assert all(decode(encode(*f)) == dict(zip("body color bomb fire speed items".split(), f))
               for f in [(9, 7, 7, 15, 7, 511), (0, 0, 0, 0, 0, 0), (15, 3, 1, 8, 2, 0x155)])
    if sys.argv[1:2] == ["-e"]:
        a = sys.argv[2:]
        print(encode(*map(int, a[:5]), int(a[5][::-1], 2)))
    else:
        for c in sys.argv[1:]:
            if len(c) == 4 and c.isdigit():
                print(c, "retail:", option(c), "| caravan:", option(c, "caravan"))
            else:
                d = decode(c)
                print(c, d and dict(d, body=BODY[d["body"]] if d["body"] < 10 else d["body"],
                                    color=COLORS[d["color"]], items=[ITEMS[i] for i in range(9) if d["items"] >> i & 1]))
