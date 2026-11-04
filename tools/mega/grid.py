"""Grid of PNGs, scaled to 256x224 cells, 6 per row: python grid.py out.png a.png b.png ..."""
import sys
from PIL import Image
fs = sys.argv[2:]; c = 6; m = Image.new('RGB', (256 * min(c, len(fs)), 224 * ((len(fs) + c - 1) // c)))
for i, f in enumerate(fs): m.paste(Image.open(f).convert('RGB').resize((256, 224)), ((i % c) * 256, (i // c) * 224))
m.save(sys.argv[1])
