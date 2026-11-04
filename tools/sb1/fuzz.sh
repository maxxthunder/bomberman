#!/bin/sh
# Exhaustive decoder check in Mesen: tools/sb1/fuzz.sh <us|eu|jp|beta> <outdir>; prints the RES line.
# H = password-screen input handler, OK = STA $00A4 of a valid code, INV = the invalid path after the 5656 test.
here=$(cd "$(dirname "$0")" && pwd); mkdir -p "$2"
case $1 in
  us|eu) a="H=0xC571F3 OK=0xC57326 INV=0xC572A7";;
  jp)    a="H=0xC570D5 OK=0xC57208 INV=0xC57189";;
  beta)  a="H=0xC571E8 OK=0xC5731B INV=0xC5729C";;
esac
{ echo "$a"; cat "$here/fuzz_decoder.lua"; } > "$2/fz.lua"
sh "$here/run.sh" "$2/fz.lua" "$1" | grep RES
