#!/bin/sh
# Type the codes in docs/pce93.md ("Verified codes") in Mesen: tools/pce93/test_passwords.sh <us|jp|sp> <outdir>
# Each code is a separate Mesen run (emu.reset() ends the test runner). Letters are given as grid indices.
here=$(cd "$(dirname "$0")" && pwd); v=$1; mkdir -p "$2"; e=22; [ "$v" = us ] || e=28
codes="s0:1,0,1,1,0,0,2,0 s1:1,0,1,1,0,1,3,0 s2:2,1,1,1,0,2,4,0 s3:2,1,1,1,0,3,5,0 max:11,9,11,5,15,19,10,3 w3s5:2,4,4,2,3,5,0,1 w7s1:10,2,2,1,0,0,8,0 w2:2,0,10,5,1,6,3,1 bad:0,0,0,0,0,0,0,0"
[ "$v" = sp ] && codes="s0:1,0,1,1,0,0,2,0"
for c in $codes; do t=${v}_${c%%:*}; mkdir -p "$2/$t"
  { echo "VER='$v' TAG='$t' END=$e CODE={${c#*:}}"; cat "$here/test_password.lua"; } > "$2/$t/t.lua"
  sh "$here/run.sh" "$2/$t/t.lua" "$v" | grep -v '^wrote'; done
