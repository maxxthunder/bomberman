#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/pceub/run.sh script.lua [ub|pce90] (pce90 = the 1990 JP card) (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" pceub "$@"
