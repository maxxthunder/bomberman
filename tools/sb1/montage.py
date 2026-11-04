"""Paste PNGs side by side: python montage.py out.png a.png b.png ..."""
import sys
from PIL import Image
ims=[Image.open(n) for n in sys.argv[2:]]
m=Image.new('RGB',(sum(i.width for i in ims),max(i.height for i in ims))); x=0
for i in ims: m.paste(i,(x,0)); x+=i.width
m.save(sys.argv[1])
