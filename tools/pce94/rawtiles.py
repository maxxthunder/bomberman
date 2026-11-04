"""Render raw 4bpp PC Engine graphics: python rawtiles.py <file> <start> <end> <outbase> [tiles per row]
Writes <outbase>_bg.png (8x8 BG tiles, 32 bytes each: planes 0/1 then 2/3) and <outbase>_spr.png (16x16 sprite
cells, 128 bytes: 4 planes of 16 words), grey levels 0-15, 2x. Used for the demo CD's unread sectors 19-25:
rawtiles.py disasm/pce94/demo/data.bin 0x9800 0xD000 out 16."""
import sys
from PIL import Image
d=open(sys.argv[1],'rb').read()[int(sys.argv[2],0):int(sys.argv[3],0)]
w=[d[2*i]|d[2*i+1]<<8 for i in range(len(d)//2)]
g=[(i*17,i*17,i*17) for i in range(16)]
n=len(w)//16
cols=int(sys.argv[5]) if len(sys.argv)>5 else 32
im=Image.new('RGB',(cols*8,((n+cols-1)//cols)*8))
px=im.load()
for t in range(n):
    for y in range(8):
        a,b=w[t*16+y],w[t*16+8+y]
        for x in range(8):
            c=(a>>(7-x)&1)|(a>>(15-x)&1)<<1|(b>>(7-x)&1)<<2|(b>>(15-x)&1)<<3
            px[(t%cols)*8+x,(t//cols)*8+y]=g[c]
im=im.resize((im.width*2,im.height*2),Image.NEAREST); im.save(sys.argv[4]+'_bg.png')
n=len(w)//64; cols=16
im=Image.new('RGB',(cols*16,((n+cols-1)//cols)*16)); px=im.load()
for t in range(n):
    for y in range(16):
        p=[w[t*64+16*k+y] for k in range(4)]
        for x in range(16):
            px[(t%cols)*16+x,(t//cols)*16+y]=g[sum((p[k]>>(15-x)&1)<<k for k in range(4))]
im=im.resize((im.width*2,im.height*2),Image.NEAREST); im.save(sys.argv[4]+'_spr.png')
