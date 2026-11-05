#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/pce90/run.sh script.lua [us|jp] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" pce90 "$@"
