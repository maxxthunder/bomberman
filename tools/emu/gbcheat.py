"""Game Boy Game Genie / GameShark code builders (shared by tools/gb1-gb3).
python tools/emu/gbcheat.py gg <addr> <new> [old]   ROM patch at a CPU address ($0000-$7FFF); with old, the code only
                                                      applies where the byte reads old (needed for $4000-$7FFF banks)
python tools/emu/gbcheat.py gs <addr> <value>       GameShark RAM write each frame (01vvllhh)"""
import sys


def gg(addr, new, old=None):
    h = "%02X%03X%X" % (new, addr & 0xFFF, (addr >> 12) ^ 0xF)
    code = h[:3] + "-" + h[3:6]
    if old is not None:
        x = old ^ 0xBA
        x = ((x << 2) | (x >> 6)) & 0xFF
        g, i = x >> 4, x & 0xF
        code += "-%X%X%X" % (g, g ^ 8, i)   # H: not part of the compare (Mesen ignores it)
    return code


def gs(addr, value):
    return "01%02X%02X%02X" % (value, addr & 0xFF, addr >> 8)


if __name__ == "__main__":
    a = [int(x, 16) for x in sys.argv[2:]]
    print(gg(*a) if sys.argv[1] == "gg" else gs(*a))
