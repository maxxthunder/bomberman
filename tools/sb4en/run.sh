#!/bin/sh
# Run a Lua script in Mesen 2 headless on the English ROM: tools/sb4en/run.sh script.lua (ROM= overrides) (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" sb4en "$@"
