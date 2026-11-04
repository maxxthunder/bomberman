// Bomberman '93 (PC Engine) password codec, both directions. Same rules as password.py; see docs/pce93.md.
// 8 letters, each an index 0-19 into the entry grid. Values d0-d5 = world-1, stage-1, bombs, fire,
// cleared-planet bits 0-3, (cleared bits 4-5) << 2 | speed. L6/L7 = low/high nibble of d0+...+d5,
// and letter x (0-5) = d[x] + key[x], key from L6 | L7 << 8 rotated right x+1 times, low 3 bits.
export const LETTERS = { us: 'BCDFGHJKLMNPQRSTVWXZ', jp: 'ABCDEFGHIJKLMNOPQRST', sp: 'ABCDEFGHIJKLMNOPQRST' };
export const RANGES = { world: [1, 7], stage: [1, 8], bombs: [1, 10], fire: [1, 5], cleared: [0, 63], speed: [0, 3] };

export function keys(l6, l7) {
  let v = l6 | (l7 << 8);
  const k = [];
  for (let i = 0; i < 6; i++) { v = (v >> 1) | ((v & 1) << 15); k.push(v & 7); }
  return k;
}

const hiLimit = (ver) => (ver === 'sp' ? 14 : 15);   // Special Version: d4, d5 < 15

export function decodeValues(p, ver = 'us') {
  const k = keys(p[6], p[7]);
  const d = [];
  for (let x = 0; x < 6; x++) { if (p[x] < k[x]) return null; d.push(p[x] - k[x]); }
  const s = d.reduce((a, b) => a + b, 0) & 0xff;
  if (p[6] !== (s & 15) || p[7] !== s >> 4) return null;
  const lim = [[0, 6], [0, 7], [1, 10], [1, 5], [0, hiLimit(ver)], [0, hiLimit(ver)]];
  return d.every((v, i) => v >= lim[i][0] && v <= lim[i][1]) ? d : null;
}

export function encodeValues(d) {
  const s = d.reduce((a, b) => a + b, 0) & 0xff;
  const l6 = s & 15, l7 = s >> 4;
  return d.map((v, i) => v + keys(l6, l7)[i]).concat([l6, l7]);
}

export function decode(code, ver = 'us') {
  const a = LETTERS[ver];
  code = String(code).trim().toUpperCase();
  if (code.length !== 8 || [...code].some((c) => !a.includes(c))) return null;
  const d = decodeValues([...code].map((c) => a.indexOf(c)), ver);
  return d && { world: d[0] + 1, stage: d[1] + 1, bombs: d[2], fire: d[3], cleared: d[4] | ((d[5] >> 2) << 4), speed: d[5] & 3 };
}

export function encode({ world, stage, bombs = 1, fire = 1, cleared = 0, speed = 0 }, ver = 'us') {
  const d = [world - 1, stage - 1, bombs, fire, cleared & 15, (((cleared >> 4) & 3) << 2) | speed];
  const st = { world, stage, bombs, fire, cleared, speed };
  for (const [n, [lo, hi]] of Object.entries(RANGES)) if (!(st[n] >= lo && st[n] <= hi)) throw new RangeError(n);
  if (ver === 'sp' && (d[4] > 14 || d[5] > 14)) throw new RangeError('not accepted by the Special Version');
  return encodeValues(d).map((i) => LETTERS[ver][i]).join('');
}

export const validate = (code, ver = 'us') => decode(code, ver) !== null;

// Same letter indices, other alphabet (US B C D F ... <-> JP A B C D ...): codes carry over between versions.
export function convert(code, from, to) {
  return [...String(code).toUpperCase()].map((c) => LETTERS[to][LETTERS[from].indexOf(c)]).join('');
}
