// Bomberman GB 3 (Japan, 1996) password codec. No dependencies.
// 7 hex digits d0-d6 ($D200-$D206, 0-F), checked by $0D:68EC. Every one of the 28 bits is used:
//   stage s (3 bits)   d0:1 d0:0 d1:3          1-6 = stage 1-6; 7 = stage 6 with $C38E = b + 1; 0 rejects
//   b (1 bit)          d4:2                    must equal s & 1 unless s = 7
//   s check (4 bits)   d2:2 d3:1 = s & 3, d5:0 d6:3 = (s >> 1) & 3
//   group x (2 bits)   d1:0 d2:3               3 -> areas 0-2, 1 -> areas 3-5, 2 -> area 6; 0 rejects
//   y (2 bits)         d3:3 d3:2               area = 3 * group + y - 1 ($C362, must be < 7); 0 rejects
//   group cleared (3)  d6:2 d6:1 d6:0          cleared flags of the 3 areas of the group ($C383 + 3 * group);
//                                              the current area's own bit must be 0, area 6 takes none
//   shop (8 bits)      d0:2 d0:3 d1:1 d1:2 d2:0 d2:1 d4:3 d3:0 = $C38D bits 0-7 (techniques bought)
//   check (5 bits)     d4:1 d4:0 d5:3 d5:2 d5:1 = $C38C, 0-18
// Entering group 1 marks areas 0-2 cleared, group 2 areas 0-5 ($0D:6A2D). The check: $C38C + the sum of SHOP_W over
// the shop bits set = the sum of AREA_W over the cleared areas ($0D:6AA4-$6ADA).
// DEB1F7F is compared first ($0D:6AE3) and taken as is: $C1B8 = 1 (boss attack).

export const AREAS = ['Wood', 'City', 'Ice', 'Sand', 'Lava', 'Aqua', 'Evil'];
export const AREA_W = [2, 2, 3, 4, 3, 4, 0];          // $0D:6AF2
export const SHOP_W = [1, 1, 1, 7, 1, 2, 2, 3];       // $0D:6AEA
export const BOSS_ATTACK = 'DEB1F7F';                 // $0D:6AE3
const HEX = '0123456789ABCDEF';
const bit = (v, n) => (v >> n) & 1;

// -> {area, areaName, stage, extra ($C38E), cleared[7], shop (8-bit $C38D), check} | {special: 'boss'} | null
export function decode(code) {
  code = String(code).trim().toUpperCase();
  if (!/^[0-9A-F]{7}$/.test(code)) return null;
  if (code === BOSS_ATTACK) return { special: 'boss' };
  const d = [...code].map(c => HEX.indexOf(c));
  const shop = ((d[0] >> 2) & 3) | ((d[1] & 6) << 1) | (((d[2] & 3) | ((d[3] & 1) << 3) | ((d[4] & 8) >> 1)) << 4);
  let s = ((d[0] & 3) << 1) | ((d[1] & 8) >> 3);
  const b = bit(d[4], 2);
  let extra = 0;
  if (s === 7) extra = b + 1; else if ((s & 1) !== b) return null;
  const c0 = ((d[2] & 4) >> 1) | ((d[3] & 2) >> 1), c1 = ((d[5] & 1) << 1) | ((d[6] & 8) >> 3);
  if (s === 0 || c0 !== (s & 3) || c1 !== ((s >> 1) & 3)) return null;
  const stage = s === 7 ? 6 : s;
  const x = ((d[1] & 1) << 1) | ((d[2] & 8) >> 3);
  if (x === 0) return null;
  const group = x === 3 ? 0 : x;
  const y = (d[3] >> 2) & 3;
  if (y === 0) return null;
  const area = 3 * group + y - 1;
  if (area >= 7) return null;
  const cleared = [0, 0, 0, 0, 0, 0, 0];
  for (let i = 0; i < (area >= 6 ? 6 : area >= 3 ? 3 : 0); i++) cleared[i] = 1;
  const g = d[6] & 7;
  if (g === 7 || g & [4, 2, 1][y - 1] || (area === 6 && g)) return null;
  for (let i = 0; i < 3; i++) if (bit(g, 2 - i)) cleared[3 * group + i] = 1;
  const check = ((d[4] & 3) << 3) | ((d[5] & 14) >> 1);
  if (check >= 19) return null;
  const want = cleared.reduce((t, f, i) => t + f * AREA_W[i], 0);
  const have = check + SHOP_W.reduce((t, w, i) => t + bit(shop, i) * w, 0);
  if ((have & 255) !== want) return null;
  return { area, areaName: AREAS[area], stage, extra, cleared, shop, check };
}

export function validate(code) { return decode(code) !== null; }

// area 0-6, stage 1-6, cleared[7] (flags of areas before the current group are forced on, the rest of the
// current group are free), shop 0-255, extra 0-2 (stage 6 only: 1/2 = the s = 7 form). Returns null when the check
// can't balance (the shop weights exceed the cleared-area weights, or the difference is over 18).
export function encode(area, stage, cleared = [], shop = 0, extra = 0) {
  if (!(area >= 0 && area < 7 && stage >= 1 && stage <= 6 && shop >= 0 && shop < 256 && extra >= 0 && extra <= 2 &&
    (extra === 0 || stage === 6))) throw new RangeError('bad value');
  const group = Math.floor(area / 3), y = area - 3 * group + 1;
  const fl = [0, 1, 2, 3, 4, 5, 6].map(i => i < 3 * group ? 1 :
    group < 2 && i < 3 * group + 3 && i !== area && cleared[i] ? 1 : 0);
  let g = 0;
  for (let i = 0; i < 3 && group < 2; i++) if (fl[3 * group + i]) g |= 4 >> i;
  const want = fl.reduce((t, f, i) => t + f * AREA_W[i], 0);
  const check = want - SHOP_W.reduce((t, w, i) => t + bit(shop, i) * w, 0);
  if (check < 0 || check > 18) return null;
  const s = extra ? 7 : stage, b = extra ? extra - 1 : s & 1, x = group === 0 ? 3 : group;
  const d = [0, 0, 0, 0, 0, 0, 0];
  d[0] = ((s >> 1) & 3) | ((shop & 3) << 2);
  d[1] = (bit(s, 0) << 3) | (((shop >> 2) & 3) << 1) | (x >> 1);
  d[2] = ((x & 1) << 3) | (bit(s, 1) << 2) | ((shop >> 4) & 3);
  d[3] = (y << 2) | (bit(s, 0) << 1) | bit(shop, 7);
  d[4] = (bit(shop, 6) << 3) | (b << 2) | (check >> 3);
  d[5] = ((check & 7) << 1) | bit(s, 2);
  d[6] = (bit(s, 1) << 3) | g;
  return d.map(v => HEX[v]).join('');
}

// the shortest way to a stage: nothing bought, only the areas the game requires cleared
export function stageCode(area, stage) { return encode(area, stage); }
