"""Charabom art (the 32 x 32 picture on the Charabom Select card) from cards.lua screenshots: c<k>.png shows id k on the
right card (k = 1-29) and id 0 (Draco, the current one) on the left. Background grey (240,240,240) and the frame row
made transparent. Usage: python tools/max/items.py <shot dir> <out dir>   (names: password.mjs CHARABOMS order)"""
import os, sys
from PIL import Image
NAMES = ['draco', 'shell', 'pommy', 'elephan', 'seadran', 'marine_eel', 'knuckle_pommy', 'panther_fang', 'twin_dragon',
         'sea_balloon', 'beast_pommy', 'big_ox', 'puteladon', 'sharkin', 'hammer_pommy', 'unicornos', 'iron_dragon',
         'iron_squid', 'animal_pommy', 'mecha_kong', 'aqua_dragon', 'pommy_dragon', 'thunder_kong', 'thunder_shark',
         'rock_snakey', 'fire_force', 'shardra', 'ox_battra', 'heat_rock', 'oct_kong']
os.makedirs(sys.argv[2], exist_ok=True)
for i, n in enumerate(NAMES):
    x = 24 if i == 0 else 104
    c = Image.open(os.path.join(sys.argv[1], 'c%d.png' % max(i, 1))).convert('RGBA').crop((x, 24, x + 32, 56))
    px = c.load()
    for yy in range(32):
        for xx in range(32):
            if yy == 31 or px[xx, yy][:3] == (240, 240, 240):
                px[xx, yy] = (0, 0, 0, 0)
    c.save(os.path.join(sys.argv[2], n + '.png'))
