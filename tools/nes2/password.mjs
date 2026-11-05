// Bomberman II (NES / Famicom, 1991) password codec. Same values in the USA and Japan carts; only the letters differ.
// Decoder $05:9619, encoder $05:9562 (bank 5 at $8000; US and JP at the same addresses). No dependencies.
// 8 characters; character k is the nibble ALPHABET[region].indexOf(char) (grid table $05:94BE, display $05:9609).
// v0 is a key: v1-v7 are XORed with it ($05:966C). Then v3 must equal (v1 + v2 + v4 + v5 + v6 + v7) & 15 ($05:967D),
// v1 = area - 1 (< 6), v2 = stage - 1 (< 8), v4 = bombs - 1 (< 8), v6 = fire - 1 (< 5) ($05:969A). v5 and v7 are
// only in the checksum. Before that the raw code is compared with seven secret codes ($05:96C6, table $05:9703).

export const ALPHABET = { us: 'K3DH6J8B75214CFG', jp: 'PCKNFOHIGEBADJLM' };
// The secret codes, as stored (JP letters) and their effect ($05:974B). The US cart matches the same nibbles.
export const SECRETS = [
  ['PCDEFGAB', 'sound test', 'sound'],
  ['PACHINKO', 'bombs are remote-controlled (detonator) in NORMAL MODE: $03EE = 1', 'remote'],
  ['PANICMAN', 'semi-remote bombs: the detonator, but bombs also go off by themselves: $03EE = 2', 'semi'],
  ['PONEJACK', 'the bonus stage, then back to the title: $0550 = 1', 'bonus'],
  ['PBOMBACE', 'short bomb fuse: $03ED = 45 (normal 75)', 'short'],
  ['PBOMBMAN', 'normal bomb fuse: $03ED = 75', 'normal'],
  ['PBOMBOLD', 'long bomb fuse: $03ED = 105', 'long'],
];

const nib = (code, region) => {
  code = String(code).replace(/\s+/g, '').toUpperCase();
  if (code.length !== 8) return null;
  const v = [...code].map(c => ALPHABET[region].indexOf(c));
  return v.includes(-1) ? null : v;
};
const sum = v => (v[1] + v[2] + v[4] + v[5] + v[6] + v[7]) & 15;

// region 'us' or 'jp'. -> {area, stage, bombs, fire, key, free:[v5, v7]} for a level code,
// {secret: 'sound'|'remote'|..., effect} for a secret code, or null if the game rejects it.
// The empty password (END with no characters) is not a code here; the game takes it as a new game.
export function decode(code, region = 'us') {
  const r = nib(code, region);
  if (!r) return null;
  const jp = r.map(x => ALPHABET.jp[x]).join('');
  const s = SECRETS.find(x => x[0] === jp);
  if (s) return { secret: s[2], effect: s[1] };
  const v = r.map((x, k) => (k ? x ^ r[0] : x));
  if (sum(v) !== v[3] || v[1] >= 6 || v[2] >= 8 || v[4] >= 8 || v[6] >= 5) return null;
  return { area: v[1] + 1, stage: v[2] + 1, bombs: v[4] + 1, fire: v[6] + 1, key: r[0], free: [v[5], v[7]] };
}

export function validate(code, region = 'us') { return decode(code, region) !== null; }

// area 1-6, stage 1-8, bombs 1-8, fire 1-5; key 0-15 (the game picks 1-15), free = [v5, v7] 0-15 (random in the game).
export function encode({ area = 1, stage = 1, bombs = 1, fire = 1, key = 1, free = [0, 0] } = {}, region = 'us') {
  const ok = (x, lo, hi) => Number.isInteger(x) && x >= lo && x <= hi;
  if (!(ok(area, 1, 6) && ok(stage, 1, 8) && ok(bombs, 1, 8) && ok(fire, 1, 5) && ok(key, 0, 15) && ok(free[0], 0, 15) && ok(free[1], 0, 15)))
    throw new RangeError('bad value');
  const v = [key, area - 1, stage - 1, 0, bombs - 1, free[0], fire - 1, free[1]];
  v[3] = sum(v);
  return v.map((x, k) => ALPHABET[region][k ? x ^ key : x]).join('');
}

// The same code in the other cart's letters.
export function convert(code, from = 'us', to = 'jp') {
  const r = nib(code, from);
  return r && r.map(x => ALPHABET[to][x]).join('');
}

// A secret code in a region's letters.
export function secretCode(name, region = 'us') {
  const s = SECRETS.find(x => x[2] === name);
  return s && convert(s[0], 'jp', region);
}
