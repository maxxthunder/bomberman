#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/pce94/run.sh script.lua [card|demo] [VAR=value ...] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" pce94 "$@"
