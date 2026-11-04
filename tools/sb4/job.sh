#!/bin/sh
# tools/sb4/job.sh <dir> <lua body...>: lib.lua + body -> <dir>/t.lua, run it (one dir per parallel job).
# Prints the script's output; CDLHEX lines go to <dir>/cdl.hex, MEM lines (vdump) to <dir>/<name>.bin.
d=$1; shift; mkdir -p "$d"; here=$(cd "$(dirname "$0")" && pwd)
{ cat "$here/lib.lua"; printf '%s\n' "$@"; } > "$d/t.lua"
sh "$here/run.sh" "$d/t.lua" > "$d/out.txt"
grep '^CDLHEX' "$d/out.txt" | cut -c8- > "$d/cdl.hex"
python -c "import sys
for l in open(sys.argv[1]):
    if l.startswith('MEM '): _,n,h=l.split(); open(sys.argv[2]+'/'+n+'.bin','wb').write(bytes.fromhex(h))" "$d/out.txt" "$d"
grep -v '^CDLHEX\|^MEM ' "$d/out.txt"
