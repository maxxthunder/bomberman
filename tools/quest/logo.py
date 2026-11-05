"""Title logo from a title-screen screenshot taken in Game Boy Color mode (shot() in Mesen, Gameboy.Model
"GameboyColor"): rows 0-62 (PRESS START starts below), the flat background flood-filled transparent from the border,
cropped. Same as tools/max/logo.py with H = 63. The Japanese title has the same logo (identical pixels).
Usage: python tools/quest/logo.py <title.png> <out.png>"""
import os, runpy, sys
sys.argv[3:] = ["63"]
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "max", "logo.py"), run_name="__main__")
