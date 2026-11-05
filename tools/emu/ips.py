"""Write a tiny IPS patch: python tools/emu/ips.py <out.ips> <rom offset hex>:<bytes hex> [...]  (shared by tools/gb1-gb3)"""
import sys
out = bytearray(b"PATCH")
for a in sys.argv[2:]:
    o, b = a.split(":")
    o, b = int(o, 16), bytes.fromhex(b)
    out += o.to_bytes(3, "big") + len(b).to_bytes(2, "big") + b
open(sys.argv[1], "wb").write(out + b"EOF")
