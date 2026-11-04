// Bomberman '94 (PC Engine) password codec: a port of tools/pce94/password.py (encoder $1AF48, checker $1B27C, bank $0D).
// Same algorithm as Mega Bomberman's (tools/mega/password.mjs).
// Codes are 4-digit strings as shown on screen, left to right; the leftmost digit is the ones digit of the number.
// No dependencies. decode(code) -> state or null; encode(area, cleared, last, alias) -> code or null.

export const STAGES = [3, 4, 4, 4, 4, 0]; // normal stages per area; area 6 is the final area

const toN = (c) => +c[0] + 10 * c[1] + 100 * c[2] + 1000 * c[3];
const toCode = (n) => [0, 1, 2, 3].map((i) => Math.floor(n / 10 ** i) % 10).join('');

export function decode(code) {
  if (!/^\d{4}$/.test(code)) return null;
  const n = toN(code), lo = n & 0xff, h = (n >> 6) & 0xff, flag = (n >> 5) & 1;
  if ((h & 0x3e) !== (((lo << 1) ^ 0xac) & 0x3e)) return null;
  const w = (h >> 4) & 7;
  if (w >= 6 || (w === 5 && h & 0xf) || (w === 0 && h & 8)) return null;
  const full = w === 0 ? 7 : 0xf;
  let d;
  if (flag) {
    const x = ~h & full;
    if (x === 0 || x & (x - 1)) return null;
    d = ((h & 0xf) << 4) | 0xf;
  } else {
    if ((h & full) === full) return null;
    d = (h & 0xf) * 0x11;
  }
  const st = [0, 1, 2, 3].filter((s) => s < STAGES[w]);
  const cleared = st.filter((s) => d & (1 << s)).map((s) => s + 1);
  const last = flag ? st.filter((s) => !(h & (1 << s))).map((s) => s + 1)[0] : null;
  return { area: w + 1, cleared, last, ramB3: w, ramB5: d, alias: !!(n & 0x2000) };
}

export function encode(area, cleared = [], last = null, alias = false) {
  const w = area - 1;
  if (!(w >= 0 && w < 6)) return null;
  let m = cleared.reduce((a, s) => a | (1 << (s - 1)), 0), flag = 0;
  const full = w ? (1 << STAGES[w]) - 1 : 7;
  if (w < 5 && m === full) { m &= ~(1 << ((last || STAGES[w]) - 1)); flag = 0x20; }
  const h = (w << 4) | m;
  const n = (h << 6) + ((((h ^ 0xac) & 0x3e) >> 1) + flag) + (alias ? 0x2000 : 0);
  return n <= 9999 ? toCode(n) : null;
}

export const validate = (code) => decode(code) !== null;

export function validCodes() {
  const out = [];
  for (let n = 0; n < 10000; n++) if (decode(toCode(n))) out.push(toCode(n));
  return out;
}

export function label(st) {
  if (st.area === 6) return 'Final area';
  const k = st.cleared.length;
  if (k === STAGES[st.area - 1]) return `Area ${st.area} boss (last cleared: stage ${st.last})`;
  if (st.cleared.every((s, i) => s === i + 1)) return `Area ${st.area} stage ${k + 1}`;
  return `Area ${st.area}, stages ${st.cleared.join(',')} cleared`;
}
