// Bomberman Selection (Korea, 2003): the Bomber Boy password codec. No dependencies. Addresses are in the Bomber Boy
// slot of the cart (ROM $40000-$7FFFF, its own banks 0-7). Bomber Man mode's 20-letter code is NES Bomberman's
// (tools/nes1/password.mjs): same letters, chain, checks and fields, checked at $02:452C.
// 8 symbols from the entry grid, 5 bits each ($C480-$C487, 0-31). Byte k ($C490 + k) collects bit k of every symbol,
// symbol 0 in bit 7 ($01:47BB). Bytes 5-7 must be 0. Then b1 + b2 + b3 = b0 and b1 ^ b2 ^ b3 ^ $CA = b4, and
//   b1 -> $C0E9  islands cleared, one bit each (ISLANDS; My Town, the hub, has none)
//   b2 -> $C0E0  gold, low byte      b3 -> $C0E1  gold, high byte (the game caps gold at 9,999, $00:3663)
// The game's own encoder ($01:4979) writes the same symbols. Faria opens once the other seven are cleared ($00:0F21);
// with all eight set ($FF) the game goes straight to the ending ($00:0D07).

export const SYMBOLS = '12345678ABCDEFGHJKLMNOPQRSTUWXYZ';
export const ISLANDS = ['Cuolece', 'Windria', 'Thulia', 'Hevol', 'Jagoraz', 'Grad', 'Faria', 'Wather'];   // $00:1013

// -> {islands (8-bit mask), gold (0-65535)} | null
export function decode(code) {
  code = String(code).trim().toUpperCase();
  if (!/^[1-8A-HJ-UW-Z]{8}$/.test(code)) return null;
  const v = [...code].map(c => SYMBOLS.indexOf(c));
  const b = [0, 1, 2, 3, 4].map(k => v.reduce((t, x, j) => t | ((x >> k) & 1) << (7 - j), 0));
  if (((b[1] + b[2] + b[3]) & 255) !== b[0] || (b[1] ^ b[2] ^ b[3] ^ 0xCA) !== b[4]) return null;
  return { islands: b[1], gold: b[2] | b[3] << 8 };
}

export function validate(code) { return decode(code) !== null; }

export function encode(islands = 0, gold = 100) {
  if (!(islands >= 0 && islands < 256 && gold >= 0 && gold < 65536)) throw new RangeError('bad value');
  const c = islands, d = gold & 255, e = gold >> 8, b = [(c + d + e) & 255, c, d, e, c ^ d ^ e ^ 0xCA];
  return [0, 1, 2, 3, 4, 5, 6, 7].map(j => SYMBOLS[b.reduce((t, x, k) => t | ((x >> (7 - j)) & 1) << k, 0)]).join('');
}
