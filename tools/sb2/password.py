"""Super Bomberman 2 password codec (all five dumps: USA, Europe, Japan, USA beta, Caravan).

There is no checksum: the game compares the four digits against a fixed table of 11 codes at
$CC:0000 (routine $CC:1926 in the USA ROM) and keeps the matching index in $1C6A.
  0-4   start world 1-5 normally          ($1A = $10 * world, table $CC:19BE)
  5-9   start world 1-5 with "full power" (index >= 5 at $C1:3BC0)
  10    sudden-death flag $1C68 = $FFFF, back to the title (pressure blocks never stop, $C0:D611)
A 12th entry 0000 follows the table but the loop stops at 11 ($CC:196C), so 0000 is rejected.

Usage: python tools/sb2/password.py            list every valid code
       python tools/sb2/password.py 4361 1234  check codes
"""
import sys

CODES = ["4361", "6442", "3903", "9564", "7735", "1111", "5462", "6763", "8784", "6925", "5656"]
FULL_POWER = {"speed": 2, "bombs": 6, "fire": 5, "remote": True, "glove": True}  # $80E0 $80E1 $80E2 $80F3 $80FE
NORMAL = {"speed": 1, "bombs": 1, "fire": 0, "remote": False, "glove": False}


def decode(code):
    """'4361' -> dict, or None if the game rejects it."""
    code = str(code)
    if len(code) != 4 or not code.isdigit() or code not in CODES:
        return None
    i = CODES.index(code)
    if i == 10:
        return {"index": 10, "sudden_death": True}
    world = i % 5 + 1
    return {"index": i, "world": world, "stage": 0x10 * world, "full_power": i >= 5,
            "kit": FULL_POWER if i >= 5 else NORMAL, "sudden_death": False}


def encode(world=None, full_power=False, sudden_death=False):
    if sudden_death:
        return CODES[10]
    if world not in range(1, 6):
        raise ValueError("world must be 1-5")
    return CODES[world - 1 + (5 if full_power else 0)]


def validate(code):
    return decode(code) is not None


if __name__ == "__main__":
    assert sum(validate(f"{n:04d}") for n in range(10000)) == 11
    assert encode(3, True) == "6763" and decode("6763")["world"] == 3 and not validate("0000")
    assert all(decode(encode(w, f))["world"] == w for w in range(1, 6) for f in (0, 1))
    for c in sys.argv[1:] or CODES:
        print(c, decode(c))
