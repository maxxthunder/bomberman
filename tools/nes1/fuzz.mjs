// node tools/nes1/fuzz.mjs <us|jp> : build the decoder fuzz set, run fuzz.lua in Mesen (run.sh; MESEN, SCRATCH set)
// and compare every result with password.mjs.
import { ALPHABET, encode, decode, values } from './password.mjs';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const here = dirname(fileURLToPath(import.meta.url)), reg = process.argv[2] || 'us';
const ADDR = { us: [0xDB7A, 0xDBF8, 0xDBCC], jp: [0xDB72, 0xDBF0, 0xDBC4] }[reg];
let seed = 87;
const rnd = n => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return (seed >>> 16) % n; };
const randState = () => ({ stage: rnd(256), digits: [...Array(7)].map(() => rnd(16)), fire: rnd(16), bombs: 1 + rnd(16),
  speed: rnd(16), wallPass: rnd(16), detonator: rnd(16), flamePass: rnd(16), reveal: rnd(16) });
const codes = [];
for (let s = 0; s < 256; s++) codes.push(encode({ stage: s }));                         // every stage
for (let k = 0; k < 3000; k++) codes.push(encode(randState()));                         // random states, all nibbles
for (let k = 0; k < 3000; k++) codes.push([...Array(20)].map(() => ALPHABET[rnd(16)]).join(''));  // random letters
const base = encode({ stage: 23, score: 456700, fire: 3, bombs: 4, speed: 1, detonator: 1 });
for (let i = 0; i < 20; i++) for (const c of ALPHABET) codes.push(base.slice(0, i) + c + base.slice(i + 1));  // every letter everywhere
const dir = join(process.env.SCRATCH, 'fuzz');
mkdirSync(dir, { recursive: true });
const hex = codes.map(c => [...c].map(x => ALPHABET.indexOf(x).toString(16)).join('')).join('');
writeFileSync(join(dir, 'fuzz.lua'), `CODES="${hex}" A0=${ADDR[0]} OK=${ADDR[1]} BAD=${ADDR[2]}\n` + readFileSync(join(here, 'fuzz.lua'), 'utf8'));
const out = execFileSync('sh', [join(here, 'run.sh'), join(dir, 'fuzz.lua'), reg], { encoding: 'utf8', maxBuffer: 1 << 28 });
const res = out.split('\n').find(l => l.startsWith('RES ')).trim().split(' ').slice(1);
if (res.length !== codes.length) throw new Error(`${res.length} results for ${codes.length} codes`);
let bad = 0, ok = 0;
codes.forEach((c, k) => {
  const d = decode(c), v = values(c);
  const want = d ? [d.stage, ...d.digits, d.fire << 4, d.bombs - 1, d.speed, d.wallPass, d.detonator, d.flamePass, d.reveal].map(x => x.toString(16)).join(',') : 'X';
  ok += res[k] !== 'X';
  if (res[k] !== want) { bad++; if (bad < 20) console.log('MISMATCH', c, res[k], want, v); }
});
console.log(`${reg}: ${codes.length} codes, ${ok} accepted by the game, ${bad} mismatches`);
