#!/bin/sh
# Run a Lua script headless: tools/emu/run.sh <game> script.lua [ver] [...]; each tools/<game>/run.sh script.lua
# [ver] [...] is this for its game. Mesen 2: MESEN = a portable Mesen.exe (a settings.json beside it keeps saves,
# states and CDLs in its own folder, off C:). mega, mega8: BizHawk (EMUHAWK). tools/<game>/lib.lua is prepended
# (after the VER/REG/MODE/GAME/STATES lines; sb3-sb5en run the script as is). Output lands next to the script (pce90,
# pce93, pceub, sb1, sb3-sb5en), in $OUT or $SCRATCH/<game>/<script>_<ver>/ (gb1-gb3, max, pocket, quest), or in
# $SCRATCH/<script>_<ver>/. ROM overrides the ROM (gb, max, pocket, quest, sb4); sb1 takes it as a third argument, sb5/sb5en
# as the second.
g=$1; s=$2; shift 2; T=$(cd "$(dirname "$0")/.." && pwd); here=$T/$g; R=$(cd "$T/../roms" && pwd -W); n=$(basename "$s" .lua)
pick() { v=${1:-$2}; shift 2; while [ $# -gt 1 ]; do [ "$1" = "$v" ] && r=$2; shift 2; done; rom=$R/$r; }  # ver default ver file ...
case $g in
  gb1) pick "$1" jp jp "Bomberman GB (Japan) (SGB Enhanced).gb" wario "Wario Blast Featuring Bomberman! (USA, Europe) (SGB Enhanced).gb";;
  gb2) pick "$1" jp jp "Bomberman GB 2 (Japan) (SGB Enhanced).gb" us "Bomberman GB (USA, Europe) (SGB Enhanced).gb";;
  gb3) pick "$1" jp jp "Bomberman GB 3 (Japan) (SGB Enhanced).gb";;
  max) pick "$1" blue blue "Bomberman Max - Blue Champion (USA).gbc" red "Bomberman Max - Red Challenger (USA).gbc" \
    hikari "Bomberman Max - Hikari no Yuusha (Japan).gbc" yami "Bomberman Max - Yami no Senshi (Japan).gbc" ain "Bomberman Max - Ain Version (Japan).gbc";;
  pocket) pick "$1" us us "Pocket Bomberman (USA, Europe) (SGB Enhanced) (GB Compatible).gbc";;
  quest) pick "$1" us us "Bomberman Quest (USA) (SGB Enhanced).gbc" jp "Bomber Man Quest (Japan) (SGB Enhanced).gbc";;
  nes1) pick "$1" us us "Bomberman (USA).nes" jp "Bomberman (Japan).nes";;
  nes2) pick "$1" us us "Bomberman II (USA).nes" jp "Bomberman II (Japan).nes";;
  mega) pick "$1" us us "Mega Bomberman (USA).md" eu "Mega Bomberman (Europe, Korea) (En).md";;
  mega8) pick "$1" tap; rom="$R/Mega Bomberman - Special 8-Player-Demo (Europe) (Proto).md";;
  pce90) pick "$1" us us "Bomberman (USA).pce" jp "Bomberman (Japan) (En).pce";;
  pce93) pick "$1" us us "Bomberman '93 (USA).pce" jp "Bomberman '93 (Japan).pce" sp "Bomberman '93 - Special Version (Japan).pce";;
  pce94) pick "$1" card card "Bomberman '94 (Japan).pce" demo "Bomberman '94 (Japan) (Demo).cue";;
  pceub) pick "$1" ub ub "Bomberman - Users Battle (Japan).pce" pce90 "Bomberman (Japan) (En).pce";;
  sb1) pick "$1" us us "Super Bomberman (USA).sfc" eu "Super Bomberman (Europe).sfc" jp "Super Bomberman (Japan).sfc" \
    beta "Super Bomberman (USA) (Beta) (1993-05-11).sfc"; rom=${2:-$rom};;
  sb3) pick "$1" eu eu "Super Bomberman 3 (Europe).sfc" jp "Super Bomberman 3 (Japan).sfc" beta "Super Bomberman 3 (Europe) (Beta).sfc";;
  sb4) rom=${ROM:-$R/Super Bomberman 4 (Japan).sfc};;
  sb4en) rom=${ROM:-$R/Super Bomberman 4 (English)[Official Localization].sfc};;
  sb5) rom=${1:-$R/Super Bomberman 5 (Japan).sfc}; [ "$1" = caravan ] && rom="$R/Super Bomberman 5 (Japan) (Caravan Event Ban).sfc";;
  sb5en) rom=${1:-$R/Super Bomberman 5 (English)[Official Localization].sfc}; [ "$1" = jp ] && rom="$R/Super Bomberman 5 (Japan).sfc";;
  *) echo "unknown game $g" >&2; exit 1;;
esac
case $g in
  gb*|max|pocket|quest)
    : "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN
    case $g in max|pocket|quest) : "${SCRATCH:?set SCRATCH to a scratch folder}";; esac
    o=${OUT:-${SCRATCH:-/d/tmp/bomberman/gb}/$g/${n}_$v}; mkdir -p "$o"
    { echo "VER=\"$v\""; cat "$here/lib.lua" "$s"; } > "$o/body.lua"
    # max, quest: battery saves and CDLs persist in the Mesen folder between runs, so each run starts clean (KEEP=1 keeps them)
    case $g in max|quest) [ -n "$KEEP" ];; *) true;; esac || rm -f "$(dirname "$MESEN")"/Saves/*.srm "$(dirname "$MESEN")"/Debugger/*.cdl
    python "$T/emu/mesen_gb.py" "$o/body.lua" "${ROM:-$rom}";;
  nes*)
    : "${MESEN:?set MESEN to a portable Mesen.exe}"; : "${SCRATCH:?set SCRATCH to a scratch directory}"; export MESEN
    o=$SCRATCH/${n}_$v; mkdir -p "$o"
    { echo "REG=\"$v\""; cat "$here/lib.lua" "$s"; } > "$o/body.lua"
    python "$T/emu/mesen_nes.py" "$o/body.lua" "$rom";;
  mega*)  # mega8: tap (default) = a Sega Team Player in each port (GPGX ControlType 4, P1-P8), tap1 = one in port 1
    # and a pad in port 2, pad = plain pads, set in a copy of BizHawk's config.ini (--config; the user's stays untouched)
    export EMUHAWK="${EMUHAWK:-K:/Emulators/Bizhawk/EmuHawk.exe}"; k=REG; py=$T/emu/bizhawk.py
    if [ $g = mega ]; then S=${SCRATCH:-/d/tmp/bomberman/mega}
    else S=${SCRATCH:?set SCRATCH to a scratch directory}; mkdir -p "$S"; k=MODE; py=$here/bizhawk8.py
      case $v in tap) ct="4 4";; tap1) ct="4 1";; *) ct="1 1";; esac
      python "$here/mkconfig.py" "$(dirname "$EMUHAWK")/config.ini" "$S/config_$v.ini" $ct
      export CONFIG="$(cd "$S" && pwd -W)/config_$v.ini"; fi
    o=$S/${n}_$v; mkdir -p "$o"
    { echo "$k=\"$v\""; echo "STATES=\"$(cd "$S" && pwd -W)/\""; cat "$here/lib.lua" "$s"; } > "$o/body.lua"
    python "$py" "$o/body.lua" "$rom";;
  pce94)  # [VAR=value ...] lines go before lib.lua; the demo CD wants a System Card at $SCRATCH/mesen/Firmware/syscard3.pce
    S=${SCRATCH:?set SCRATCH}; [ $# -gt 0 ] && shift; export MESEN=${MESEN:-$S/mesen/Mesen.exe}
    o=$S/${n}_$v; mkdir -p "$o"
    { echo "STATES=\"$(cd "$S" && pwd -W)/\""; echo "GAME=\"$v\""; for x in "$@"; do echo "$x"; done; cat "$here/lib.lua" "$s"; } > "$o/body.lua"
    python "$T/emu/mesen.py" "$o/body.lua" "$rom" "$o";;
  sb3)  # portable Mesen in SB3_MESEN_DIR, built on first use when MESEN is not set
    P=${SB3_MESEN_DIR:?set SB3_MESEN_DIR to a scratch folder for the portable Mesen (off C:)}
    if [ -z "$MESEN" ]; then [ -f $P/Mesen.exe ] || { mkdir -p $P; cp /k/Emulators/Mesen/Mesen.exe $P/; echo "{}" > $P/settings.json; }; MESEN=$P/Mesen.exe; fi
    export MESEN; python "$T/emu/mesen.py" "$s" "$rom";;
  pce9[03]|pceub|sb1)
    : "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN
    d=$(dirname "$s"); cat "$here/lib.lua" "$s" > "$d/_full.lua"
    python "$T/emu/mesen.py" "$d/_full.lua" "$rom";;
  *) : "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN; python "$T/emu/mesen.py" "$s" "$rom";;
esac
