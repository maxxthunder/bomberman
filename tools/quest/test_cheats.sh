#!/bin/sh
# All cheat checks of test_cheats.lua and the IPS patches, both versions: tools/quest/test_cheats.sh (MESEN, SCRATCH set)
here=$(cd "$(dirname "$0")" && pwd); S=${SCRATCH:?set SCRATCH}/quest/_t; mkdir -p "$S"
for v in us jp; do
  for t in none inv invgg; do f=$S/tc_$t.lua; { echo "TEST='$t'"; cat "$here/test_cheats.lua"; } > $f; OUT=$S/tc_${t}_$v sh "$here/run.sh" $f $v | grep "^$t"; done
  r=$S/quest_$v.gbc; case $v in us) src="Bomberman Quest (USA) (SGB Enhanced).gbc";; jp) src="Bomber Man Quest (Japan) (SGB Enhanced).gbc";; esac
  python - "$here/../../roms/$src" "$here/../../patches/quest_invincible_$v.ips" "$r" <<'PY'
import sys
rom = bytearray(open(sys.argv[1], "rb").read()); p = open(sys.argv[2], "rb").read(); i = 5
while p[i:i + 3] != b"EOF":
    o, n = int.from_bytes(p[i:i + 3], "big"), int.from_bytes(p[i + 3:i + 5], "big"); rom[o:o + n] = p[i + 5:i + 5 + n]; i += 5 + n
open(sys.argv[3], "wb").write(rom)
PY
  f=$S/tc_ips.lua; { echo "TEST='ips'"; cat "$here/test_cheats.lua"; } > $f; ROM=$(cd "$S" && pwd -W)/quest_$v.gbc OUT=$S/tc_ips_$v sh "$here/run.sh" $f $v | grep "^ips"
done
