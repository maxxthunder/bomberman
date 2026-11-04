"""Write the character-password fuzz cases (one per line) used by fuzz.lua."""
import random, sys
from password import ALPHA, encode
random.seed(5)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 400
c = set()
for _ in range(N):
    c.add("".join(random.choice(ALPHA) for _ in range(6)))
for i in range(6):
    for a in ALPHA:
        c.add("D24GJN"[:i] + a + "D24GJN"[i + 1:])
for body in range(16):
    for color in range(8):
        c.add(encode(body, color, random.randrange(8), random.randrange(16), random.randrange(8), random.randrange(512)))
for _ in range(100):
    c.add(encode(random.randrange(16), random.randrange(8), random.randrange(8), random.randrange(16), random.randrange(8), random.randrange(512)))
open(sys.argv[1], "w").write("\n".join(sorted(c)) + "\n")
print(len(c))
