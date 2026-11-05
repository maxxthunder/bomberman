#!/bin/sh
# test_debug.lua for both versions: the Game Genie and GameShark codes, the patch and retail, Select menu and debug start (MESEN, SCRATCH set)
here=$(cd "$(dirname "$0")" && pwd); S=${SCRATCH:?set SCRATCH}/quest/_t; mkdir -p "$S"
for v in us jp; do
  case $v in us) src="Bomberman Quest (USA) (SGB Enhanced).gbc";; jp) src="Bomber Man Quest (Japan) (SGB Enhanced).gbc";; esac
  python -c "
import sys
rom = bytearray(open(sys.argv[1], 'rb').read()); p = open(sys.argv[2], 'rb').read(); i = 5
while p[i:i + 3] != b'EOF':
    o, n = int.from_bytes(p[i:i + 3], 'big'), int.from_bytes(p[i + 3:i + 5], 'big'); rom[o:o + n] = p[i + 5:i + 5 + n]; i += 5 + n
open(sys.argv[3], 'wb').write(rom)" "$here/../../roms/$src" "$here/../../patches/quest_debug_$v.ips" "$S/quest_debug_$v.gbc"
  for t in none gg gs ips; do for sc in menu start; do
    f=$S/td_${t}_$sc.lua; { echo "TEST='$t' SCEN='$sc'"; cat "$here/test_debug.lua"; } > $f
    if [ $t = ips ]; then ROM=$(cd "$S" && pwd -W)/quest_debug_$v.gbc OUT=$S/td_${t}_${sc}_$v sh "$here/run.sh" $f $v | grep -v "^wrote\|^rc"
    else OUT=$S/td_${t}_${sc}_$v sh "$here/run.sh" $f $v | grep -v "^wrote\|^rc"; fi
  done; done
done
