# sheet.py out.png cols scale label=path ... : labelled contact sheet
import sys
from PIL import Image, ImageDraw
out, cols, sc = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]); items=[a.split('=',1) for a in sys.argv[4:]]
ims=[(l,Image.open(p).convert('RGB')) for l,p in items]
w,h=ims[0][1].size; w2,h2=int(w*sc),int(h*sc); rows=(len(ims)+cols-1)//cols
S=Image.new('RGB',(cols*w2,rows*(h2+12)),'white'); d=ImageDraw.Draw(S)
for i,(l,im) in enumerate(ims):
    x,y=(i%cols)*w2,(i//cols)*(h2+12); S.paste(im.resize((w2,h2)),(x,y+12)); d.text((x+2,y),l,fill='black')
S.save(out)
