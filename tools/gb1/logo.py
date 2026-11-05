"""Title logo: BG tiles 0-19 x 0-7 (JP) / 0-19 x 0-11 (Wario Blast) of the title (the menu is the window), colour 0
transparent, cropped. The bombs beside the menu are sprites, not part of the logo.
Usage: python tools/gb1/logo.py <title.vram> <out.png> <jp|wario>   (title.vram: vdump.lua)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "emu"))
import gbvram

im = gbvram.render_map(gbvram.load(sys.argv[1]), 0, 0, 20, 8 if sys.argv[3] == "jp" else 12, transparent=True)
im.crop(im.getbbox()).save(sys.argv[2])
