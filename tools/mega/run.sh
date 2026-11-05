#!/bin/sh
# Run a Lua script in BizHawk (Genesis): tools/mega/run.sh script.lua [us|eu] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" mega "$@"
