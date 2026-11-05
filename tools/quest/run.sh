#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/quest/run.sh script.lua [us|jp] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" quest "$@"
