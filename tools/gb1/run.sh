#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/gb1/run.sh script.lua [jp|wario] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" gb1 "$@"
