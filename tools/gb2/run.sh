#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/gb2/run.sh script.lua [jp|us] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" gb2 "$@"
