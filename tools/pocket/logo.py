"""Title logo from a title-screen screenshot taken in Game Boy Color mode (shot() in Mesen, Gameboy.Model
"GameboyColor"): rows 0-63 (the menu box starts on row 64, Bomberman is sprites), the flat background flood-filled
transparent from the border, cropped. Same as tools/max/logo.py with H = 64.
Usage: python tools/pocket/logo.py <title.png> <out.png>"""
import os, runpy, sys
sys.argv[3:] = ["64"]
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "max", "logo.py"), run_name="__main__")
