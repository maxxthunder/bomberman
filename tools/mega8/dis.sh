#!/bin/sh
# Print disasm/mega8/demo.asm lines with addresses in [start,end): tools/mega8/dis.sh 3068 3200
awk -v s=$((0x$1)) -v e=$((0x$2)) '{a=strtonum("0x"$1)} a>=s && a<e' "$(dirname "$0")/../../disasm/mega8/demo.asm"
