"""Title logo: BG tiles 12-31 x 0-8 of the title (shown with SCX = $60; the menu is the window), colour 0
transparent, cropped. Bomberman beside the menu is part of the window.
Usage: python tools/gb3/logo.py <title.vram> <out.png>   (title.vram: vdump.lua)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "emu"))
import gbvram

im = gbvram.render_map(gbvram.load(sys.argv[1]), 12, 0, 20, 9, transparent=True)
im.crop(im.getbbox()).save(sys.argv[2])
