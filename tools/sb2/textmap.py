"""Character map of the SB2 debug-menu font (tilemap words, attribute byte after each character), for
python tools/sb1/text.py <rom> tools/sb2/textmap.py [cdl...]"""
CHARS = {i + 1: chr(65 + i) for i in range(26)}
CHARS.update({0x20 + i: str(i) for i in range(10)})
CHARS.update({0x1C: ".", 0x34: "-", 0x2A: " "})
STRIDE = 2
MIN = 4
