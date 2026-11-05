"""Render the SB2 collision maps dumped by tools/sb2/map_dump.lua.
  python tools/sb2/maps.py <map_dump output> <outdir> [screenshot dir]
Each MAP line holds the even bytes of $7F:C000-$7F:C7FF: the collision code of each 16 x 16 cell (from the BG tile
through the stage's attribute table at $C0:F71B), cell (x, y) at word y*64 + x; 16 x 14 cells cover the screen. Colours: $00 floor (green), $C2 soft block (tan), $C5/$C6 wall (grey/dark), others by
code. Writes map_<stage>.png (tile grid next to the game's own screenshot when given) and sheet.png."""
import os, sys
from PIL import Image, ImageDraw

COL = {0x00: (60, 140, 60), 0xC2: (200, 170, 110), 0xC5: (150, 150, 160), 0xC6: (90, 90, 100)}


def colour(v):
    return COL.get(v, ((v * 53) % 200 + 40, (v * 97) % 200 + 40, (v * 31) % 200 + 40))


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    shots = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(out, exist_ok=True)
    seen, tiles = set(), []
    for line in open(src):
        if not line.startswith("MAP "):
            continue
        _, tag, stage, h = line.split()
        if stage in seen:
            continue
        seen.add(stage)
        b = bytes.fromhex(h)
        img = Image.new("RGB", (256, 224))
        d = ImageDraw.Draw(img)
        for r in range(14):
            for c in range(16):
                d.rectangle([c * 16, r * 16, c * 16 + 15, r * 16 + 15], fill=colour(b[r * 64 + c]), outline=(30, 30, 30))
        if shots and os.path.exists(os.path.join(shots, f"map_{tag}.png")):
            s = Image.open(os.path.join(shots, f"map_{tag}.png")).convert("RGB")
            both = Image.new("RGB", (512 + 4, 224), (255, 255, 255))
            both.paste(img, (0, 0)); both.paste(s.crop((0, 0, 256, 224)), (260, 0))
            img = both
        name = f"{int(stage[0])}-{int(stage[1], 16) + 1}" if stage[0] != "6" else "ending"
        img.save(os.path.join(out, f"map_{stage}.png"))
        tiles.append((img, f"${stage} = {name}"))
    cols = 4
    w, h = tiles[0][0].width // 2 + 6, tiles[0][0].height // 2 + 18
    sheet = Image.new("RGB", (cols * w, ((len(tiles) + cols - 1) // cols) * h), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for k, (im, lab) in enumerate(tiles):
        x, y = (k % cols) * w, (k // cols) * h
        sheet.paste(im.resize((im.width // 2, im.height // 2)), (x + 3, y + 15))
        d.text((x + 3, y + 2), lab, fill=(0, 0, 0))
    sheet.save(os.path.join(out, "sheet.png"))
    print(len(tiles), "maps")
