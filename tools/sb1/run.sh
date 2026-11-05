#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/sb1/run.sh script.lua [us|eu|jp|beta] [rom.sfc] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" sb1 "$@"
