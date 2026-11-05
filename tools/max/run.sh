#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/max/run.sh script.lua [blue|red (USA), hikari|yami (Japan), ain] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" max "$@"
