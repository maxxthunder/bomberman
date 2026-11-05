#!/bin/sh
# Exhaustive check of the game's password decoder in Mesen: tools/pce93/fuzz.sh <us|jp|sp> <outdir> [nrand]
# then: python tools/pce93/check_fuzz.py <outdir>/out.txt <ver>
# ENTRY = decoder entry, OK/BAD = its CLC / SEC exits, BUF = the 8 entered letters, ST = first stored byte ($3895 / $388C).
here=$(cd "$(dirname "$0")" && pwd); mkdir -p "$2"; n=${3:-300000}
case $1 in
  us) a="ENTRY=0xDCAC OK=0xDD47 BAD=0xDD4A BUF=0x3C62 ST=0x3895 BANK=1 SLOT=6 NL=20";;
  jp) a="ENTRY=0x9A3C OK=0x9AD7 BAD=0x9ADA BUF=0x3C62 ST=0x3895 BANK=6 SLOT=4 NL=26";;
  sp) a="ENTRY=0x979B OK=0x9836 BAD=0x9839 BUF=0x3C4D ST=0x388C BANK=6 SLOT=4 NL=26";;
esac
{ echo "VER='$1' NRAND=$n $a"; cat "$here/fuzz.lua"; } > "$2/fz.lua"
sh "$here/run.sh" "$2/fz.lua" "$1" > "$2/out.txt"; grep -c '^F' "$2/out.txt"; tail -2 "$2/out.txt"
