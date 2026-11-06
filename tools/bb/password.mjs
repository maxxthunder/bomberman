// Atomic Punk (USA, 1991) / Bomber Boy (Japan, 1990) password codec (Game Boy). No dependencies. Addresses are the same
// in both carts unless both are given (US / JP). Game B's 20-letter code is NES Bomberman's (tools/nes1/password.mjs):
// same letters, chain, checks and fields ($02:451D).
// Game A: 8 symbols from the entry grid, 5 bits each ($C480-$C487, 0-31). Byte k ($C490 + k) collects bit k of every
// symbol, symbol 0 in bit 7 ($01:44B2 / $01:4497). Bytes 5-7 must be 0. Then b1 + b2 + b3 = b0 and
// b1 ^ b2 ^ b3 ^ $CA = b4, and
//   b1 -> $C0E9  islands cleared, one bit each (ISLANDS; My Town, the hub, has none)
//   b2 -> $C0E0  gold, low byte      b3 -> $C0E1  gold, high byte (the game caps gold at 9,999, $00:34E6)
// The game's own encoder ($01:4670 / $01:4655) writes the same symbols. Faria opens once the other seven are cleared
// ($00:0EB7); with all eight set ($FF) the game goes straight to the ending ($00:0CA5).

export const SYMBOLS = '12345678ABCDEFGHJKLMNOPQRSTUWXYZ';      // Bomber Boy: no I, V, 9 or 0
export const SYMBOLS_US = '12345678BCDFGHJKLMNPQRSTVWXZ?!.=';   // Atomic Punk: the same 32 places, no vowels
// Atomic Punk's Game B is NES Bomberman's code with A E I O shown as 0 1 2 3 (its letter table, $02:44D5)
export const toUS = nes => nes.replace(/[AEIO]/g, c => 'AEIO'.indexOf(c));
export const fromUS = us => us.replace(/[0-3]/g, d => 'AEIO'[d]);
export const ISLANDS = ['Cuolece', 'Windria', 'Thulia', 'Hevol', 'Jagoraz', 'Grad', 'Faria', 'Wather'];   // names at $00:0F79

// -> {islands (8-bit mask), gold (0-65535)} | null
export function decode(code, symbols = SYMBOLS) {
  code = String(code).trim().toUpperCase();
  const v = [...code].map(c => symbols.indexOf(c));
  if (v.length !== 8 || v.includes(-1)) return null;
  const b = [0, 1, 2, 3, 4].map(k => v.reduce((t, x, j) => t | ((x >> k) & 1) << (7 - j), 0));
  if (((b[1] + b[2] + b[3]) & 255) !== b[0] || (b[1] ^ b[2] ^ b[3] ^ 0xCA) !== b[4]) return null;
  return { islands: b[1], gold: b[2] | b[3] << 8 };
}

export function validate(code, symbols = SYMBOLS) { return decode(code, symbols) !== null; }

export function encode(islands = 0, gold = 100, symbols = SYMBOLS) {
  if (!(islands >= 0 && islands < 256 && gold >= 0 && gold < 65536)) throw new RangeError('bad value');
  const c = islands, d = gold & 255, e = gold >> 8, b = [(c + d + e) & 255, c, d, e, c ^ d ^ e ^ 0xCA];
  return [0, 1, 2, 3, 4, 5, 6, 7].map(j => symbols[b.reduce((t, x, k) => t | ((x >> (7 - j)) & 1) << k, 0)]).join('');
}
