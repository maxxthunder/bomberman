#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/pocket/run.sh script.lua (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" pocket "$@"
