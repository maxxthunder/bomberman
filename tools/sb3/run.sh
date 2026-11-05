#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/sb3/run.sh script.lua [eu|jp|beta] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" sb3 "$@"
