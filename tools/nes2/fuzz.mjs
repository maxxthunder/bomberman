// node tools/nes2/fuzz.mjs <us|jp> : build the decoder fuzz set, run fuzz.lua in Mesen (run.sh; MESEN, SCRATCH set)
// and compare every result with password.mjs. The RAM the decoder sets is zeroed before each code.
import { ALPHABET, encode, decode, SECRETS, secretCode } from './password.mjs';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const here = dirname(fileURLToPath(import.meta.url)), reg = process.argv[2] || 'us';
let seed = 2;
const rnd = n => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return (seed >>> 16) % n; };
const codes = [];
for (let a = 1; a <= 6; a++) for (let s = 1; s <= 8; s++) for (let b = 1; b <= 8; b++) for (let f = 1; f <= 5; f++)
  codes.push(encode({ area: a, stage: s, bombs: b, fire: f, key: rnd(16), free: [rnd(16), rnd(16)] }, reg));  // all 1,920 states
for (let k = 0; k < 4000; k++) codes.push([...Array(8)].map(() => ALPHABET[reg][rnd(16)]).join(''));        // random
const base = encode({ area: 3, stage: 5, bombs: 4, fire: 2, key: 9, free: [1, 2] }, reg);
for (let i = 0; i < 8; i++) for (const c of ALPHABET[reg]) codes.push(base.slice(0, i) + c + base.slice(i + 1));
for (const s of SECRETS) codes.push(secretCode(s[2], reg));
// out-of-range fields with a good checksum: v1 = 6..15 etc.
for (let x = 0; x < 16; x++) for (const k of [1, 2, 4, 6]) {
  const v = [0, 0, 0, 0, 0, 0, 0, 0]; v[k] = x; v[3] = (v[1] + v[2] + v[4] + v[5] + v[6] + v[7]) & 15;
  codes.push(v.map(n => ALPHABET[reg][n]).join(''));
}
const dir = join(process.env.SCRATCH, 'fuzz');
mkdirSync(dir, { recursive: true });
const hex = codes.map(c => [...c].map(x => ALPHABET[reg].indexOf(x).toString(16)).join('')).join('');
writeFileSync(join(dir, 'fuzz.lua'), `CODES="${hex}"\n` + readFileSync(join(here, 'fuzz.lua'), 'utf8'));
const out = execFileSync('sh', [join(here, 'run.sh'), join(dir, 'fuzz.lua'), reg], { encoding: 'utf8', maxBuffer: 1 << 28 });
const res = out.split('\n').find(l => l.startsWith('RES ')).trim().split(' ').slice(1);
if (res.length !== codes.length) throw new Error(`${res.length} results for ${codes.length} codes`);
const T = { short: 0x2d, normal: 0x4b, long: 0x69 };
let bad = 0, ok = 0;
codes.forEach((c, k) => {
  const d = decode(c, reg);
  let want = 'X';
  if (d && !d.secret) want = [d.area - 1, d.stage - 1, d.bombs - 1, d.fire - 1, 0, 0, 0, 0, 0].map(x => x.toString(16)).join(',');
  if (d && d.secret) {
    const v = [0, 0, 0, 0, T[d.secret] || 0, d.secret === 'remote' ? 1 : d.secret === 'semi' ? 2 : 0,
      ['remote', 'semi', 'short', 'normal', 'long'].includes(d.secret) ? 1 : 0, d.secret === 'sound' ? 1 : 0, d.secret === 'bonus' ? 1 : 0];
    want = v.map(x => x.toString(16)).join(',');
  }
  ok += res[k] !== 'X';
  if (res[k] !== want) { bad++; if (bad < 20) console.log('MISMATCH', c, res[k], want); }
});
console.log(`${reg}: ${codes.length} codes, ${ok} accepted by the game, ${bad} mismatches`);
