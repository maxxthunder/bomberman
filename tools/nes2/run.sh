#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/nes2/run.sh script.lua [us|jp] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" nes2 "$@"
