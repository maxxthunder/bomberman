// Bomberman Quest (Game Boy Color): there is no password. The game saves to battery RAM (one file, saved at the Kepo
// statue in the Bomber Shuttle), so the codes here are GameShark codes (type $01, a WRAM write each frame) for the
// item flags in the save block the game plays from, plus a builder and checker for the 244-byte save itself.
//
// Save (cart RAM $A000-$A0F3, the same layout in both versions; copied to WRAM by $00:0B28 and back by $00:0BBC):
//   +$00 checksum = (sum of +$01..+$F2) & $FF   +$01-$0E "DMG SAVE DATA."   +$0F-$F2 the game block   +$F3 checksum again
// The load check ($00:0BEC US, $00:0BF9 Japan) wants the signature, +$00 = +$F3, and the sum; otherwise New Game.
// The game block sits at WRAM $CE81 (US) / $CE80 (Japan), one byte apart, so every GameShark address differs by one:
//   +$00 max HP, +$01 HP ($10 = one heart), +$04/+$05 the weapons on A / B, +$08 armour worn,
//   +$A2 + id weapons 1-28, +$BF + id equipment 1-16, +$D0 + id items 1-16: bit 4 = owned, bits 0-3 = level / count.

export const VERSIONS = { us: 'Bomberman Quest (USA)', jp: 'Bomber Man Quest (Japan)' };
export const BLOCK = { us: 0xCE81, jp: 0xCE80 };
export const SIGNATURE = 'DMG SAVE DATA.';

// names are the US menu's; icon = docs/img/items/quest/<icon>.png
const list = names => names.map((name, i) => ({ id: i + 1, name, icon: name.toLowerCase().replace(/!\?/, 'dance').replace(/[^a-z]+/g, '_').replace(/_$/, '') }));
export const WEAPONS = list(['Wings', 'Jump Shoes', 'Dash Shoes', 'Power Gloves', 'Hammer', 'Remote Control', 'Tackle Belt',
  'Normal Bomb', 'Ice Bomb', 'Poison Bomb', 'Short-fused Bomb', 'Long-fused Bomb', 'Rubber Bomb', 'Wide-range Bomb',
  'Skull Bomb', 'Land Mine', 'Flak Bomb', 'Homing Bomb', 'Speed Bomb', 'Aqua Bomb', 'Robot Bomb', 'Right Bomb',
  'Left Bomb', 'Yo-yo', '!?', 'Shovel', 'Shield', 'Gauntlets']);
export const EQUIPMENT = list(['Silver Armor', 'Gold Armor', 'Platinum Armor', 'Teleport Armor', 'Steel Shoes',
  'Sneakers', 'Rocket Shoes', 'Combat Boots', 'Safety Shoes', 'Glasses', 'Power Bracelets', 'Scuba Gear', 'Helmet',
  'Lamp', 'Full Fire', 'Leather Armor']);
export const ITEMS = list(['Rubber', 'Clock', 'Ice Shard', 'Poison Ivy', 'Boomerang', 'Skull', 'Explosive Core', 'Fire',
  'Armored Jacket', 'Stopwatch', 'Flute', 'Heart', 'Full Heart', 'White Card', 'Black Card', 'Honey Card']);
// kind -> [list, offset of id 0 in the block]; items 1-8 are bomb components and carry a count (bits 0-3)
export const KINDS = { weapon: [WEAPONS, 0xA2], equipment: [EQUIPMENT, 0xBF], item: [ITEMS, 0xD0] };
export const MAX_HEARTS = 10;   // the debug start's $A0

export const CHEATS = { invincible: '018034C2', invincibleGG: '189-26A-6EA' };

const hex = (n, w = 2) => n.toString(16).toUpperCase().padStart(w, '0');
const gs = (v, a) => '01' + hex(v) + hex(a & 0xFF) + hex(a >> 8);

// state: {weapon: [ids], equipment: [ids], item: {id: count 1-15} (or [ids]: count 1), hearts: 1-10} -> GameShark codes
export function encode(state, ver = 'us') {
  const base = BLOCK[ver], out = [];
  if (base === undefined) return null;
  for (const [kind, [names, off]] of Object.entries(KINDS)) {
    const s = state[kind];
    if (!s) continue;
    const ent = Array.isArray(s) ? s.map(id => [id, 1]) : Object.entries(s).map(([k, n]) => [+k, n]);
    for (const [id, n] of ent) {
      if (!names[id - 1] || !(n >= 1 && n <= 15)) return null;
      out.push(gs(0x10 | (kind === 'item' && id <= 8 ? n : 0), base + off + id));
    }
  }
  if (state.hearts !== undefined) {
    const h = state.hearts;
    if (!(h >= 1 && h <= MAX_HEARTS)) return null;
    out.push(gs(h * 16, base), gs(h * 16, base + 1));
  }
  return out;
}

// one GameShark code -> {kind, id, name, value} ('hearts' / 'hp': {kind, value: hearts}), else null
export function decode(code, ver = 'us') {
  const m = /^01([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})$/.exec(String(code).toUpperCase().replace(/[\s-]/g, ''));
  const base = BLOCK[ver];
  if (!m || base === undefined) return null;
  const v = parseInt(m[1], 16), o = parseInt(m[3] + m[2], 16) - base;
  if ((o === 0 || o === 1) && v % 16 === 0 && v >= 16 && v <= MAX_HEARTS * 16) return { kind: o ? 'hp' : 'hearts', value: v / 16 };
  for (const [kind, [names, off]] of Object.entries(KINDS)) {
    const id = o - off, e = names[id - 1];
    if (!e) continue;
    const n = v & 15, counted = kind === 'item' && id <= 8;
    if (v >> 4 !== 1 || (counted ? n === 0 : n !== 0)) return null;
    return { kind, id, name: e.name, value: counted ? n : 1 };
  }
  return null;
}

export function validate(code, ver) { return decode(code, ver) !== null; }

// the game's own load check on a 244-byte cart RAM image ($00:0BEC / $00:0BF9)
export function checkSave(bytes) {
  if (!bytes || bytes.length < 0xF4) return false;
  for (let i = 0; i < 14; i++) if (bytes[1 + i] !== SIGNATURE.charCodeAt(i)) return false;
  let s = 0;
  for (let i = 1; i <= 0xF2; i++) s += bytes[i];
  return bytes[0] === bytes[0xF3] && bytes[0] === (s & 0xFF);
}

// a 228-byte game block -> the 244-byte cart RAM image the game accepts (what $00:0BBC writes)
export function makeSave(block) {
  if (!block || block.length !== 0xE4) return null;
  const b = new Uint8Array(0xF4);
  for (let i = 0; i < 14; i++) b[1 + i] = SIGNATURE.charCodeAt(i);
  b.set(block, 0x0F);
  let s = 0;
  for (let i = 1; i <= 0xF2; i++) s += b[i];
  b[0] = b[0xF3] = s & 0xFF;
  return b;
}
