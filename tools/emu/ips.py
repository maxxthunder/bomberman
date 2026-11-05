"""Minimal IPS writer and reader, shared by the patch makers."""


def ips(records):
    """[(file offset, bytes), ...] -> IPS: 'PATCH', then 3-byte offset, 2-byte length, data, then 'EOF'."""
    out = bytearray(b"PATCH")
    for off, data in records:
        out += off.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    return bytes(out + b"EOF")


def apply(rom, patch):
    rom, i = bytearray(rom), 5
    assert patch[:5] == b"PATCH"
    while patch[i:i + 3] != b"EOF":
        off, n = int.from_bytes(patch[i:i + 3], "big"), int.from_bytes(patch[i + 3:i + 5], "big")
        rom[off:off + n] = patch[i + 5:i + 5 + n]
        i += 5 + n
    return bytes(rom)

