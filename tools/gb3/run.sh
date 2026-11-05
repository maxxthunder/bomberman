#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/gb3/run.sh script.lua (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" gb3 "$@"
