"""Copy BizHawk's config.ini with GPGX ControlTypeLeft/Right set: mkconfig.py src dst left right (1 pad, 4 Team Player)."""
import json, sys
c = json.load(open(sys.argv[1], encoding="utf-8-sig"))
s = c["CoreSyncSettings"]["BizHawk.Emulation.Cores.Consoles.Sega.gpgx.GPGX"]
s["ControlTypeLeft"], s["ControlTypeRight"] = int(sys.argv[3]), int(sys.argv[4])
json.dump(c, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
