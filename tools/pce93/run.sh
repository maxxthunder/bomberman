#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/pce93/run.sh script.lua [us|jp|sp] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" pce93 "$@"
