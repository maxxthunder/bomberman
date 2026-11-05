#!/bin/sh
# Run a Lua script in BizHawk on the 8-player demo: SCRATCH=dir tools/mega8/run.sh script.lua [tap|tap1|pad] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" mega8 "$@"
