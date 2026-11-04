"""Super Bomberman 4 (Japan) password codec.

There is no algorithm: the game keeps one table of 50 four-digit codes (words at $C2:AE9A, file 0x2AE9A)
and compares the entered number against it (loop at $C2:A916). A hit stores the table index in $92;
then $C2:A9E3 checks twelve values that do something other than start that stage (see SPECIAL).
Usage: python password.py [code ...]   (no args: print the table and run the self-check)"""
import struct, sys

TABLE = [7352, 8831, 7255, 5714, 5289, 1352, 6892, 6722, 7793, 6428, 8492, 7490, 4370, 6682, 4677, 4692,
         4680, 2247, 5725, 7821, 5890, 7258, 3379, 6009, 5389, 4080, 2501, 5736, 3211, 5589, 8902, 721,
         3703, 2679, 2479, 4792, 6790, 1574, 7777, 4622, 520, 903, 1019, 1222, 1107, 827, 107, 1009, 5656, 164]
SPECIAL = {  # value: effect (from the compare chain at $C2:A9E3)
    7777: "battle: the winner of a single-match round turns gold next round ($1F48 = 1)",
    4622: "battle: start-position/block set 1 ($024A = 1)",
    520: "battle: start-position/block set 2 ($024A = 2)",
    903: "battle: start-position/block set 3 ($024A = 3)",
    1019: "normal game: world 1 (1-1) with full power-ups ($7F70B5 = 1)",
    1222: "normal game: world 2 (2-1) with full power-ups ($7F70B5 = 2)",
    1107: "normal game: world 3 (3-1) with full power-ups ($7F70B5 = 3)",
    827: "normal game: world 4 (4-1) with full power-ups ($7F70B5 = 4)",
    107: "normal game: world 5 (5-1) with full power-ups ($7F70B5 = 5)",
    1009: "ending",
    5656: "battle: super attacks without the tired wait ($7F70B7 = 1)",
    164: "battle: wider random item pool ($7F70BD = 1)",
}


def stage_name(i):
    return f"{i // 8 + 1}-{i % 8 + 1}"


def decode(code):
    """'7352' -> dict, or None if the game rejects it."""
    s = str(code)
    if len(s) != 4 or not s.isdigit():
        return None
    v = int(s)
    if v not in TABLE:
        return None
    i = TABLE.index(v)
    if v in SPECIAL:
        return {"code": s, "index": i, "kind": "special", "effect": SPECIAL[v]}
    return {"code": s, "index": i, "kind": "stage", "stage": stage_name(i)}


def validate(code):
    return decode(code) is not None


def encode(stage):
    """'3-4' (or table index 0-37) -> the code that starts that normal-game stage."""
    i = stage if isinstance(stage, int) else (int(stage[0]) - 1) * 8 + int(stage[2]) - 1
    if not 0 <= i < 38:
        raise ValueError("stage passwords exist only for 1-1 .. 5-6")
    return f"{TABLE[i]:04d}"


def _check(rom_path=None):
    assert sum(validate(f"{n:04d}") for n in range(10000)) == 50
    assert encode("1-1") == "7352" and encode("5-2") == "2679" and decode("2609") is None
    assert all(decode(encode(i))["index"] == i for i in range(38))
    if rom_path:
        assert list(struct.unpack("<50H", open(rom_path, "rb").read()[0x2AE9A:0x2AE9A + 100])) == TABLE
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].endswith(".sfc"):
        for c in sys.argv[1:]:
            print(c, decode(c) or "rejected")
    else:
        for i, v in enumerate(TABLE):
            d = decode(f"{v:04d}")
            print(f"{i:2d} {v:04d} {d.get('stage') or d['effect']}")
        _check(sys.argv[1] if len(sys.argv) > 1 else None)
