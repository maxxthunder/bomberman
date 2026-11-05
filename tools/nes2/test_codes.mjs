// node tools/nes2/test_codes.mjs <us|jp> CODE [CODE...] : type the codes in Mesen with the pad (test_codes.lua via
// run.sh; MESEN and SCRATCH set) and check the decoder's verdict and RAM against password.mjs.
// Screenshots: $SCRATCH/test_codes_<reg>/<code>.png
import { decode } from './password.mjs';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const here = dirname(fileURLToPath(import.meta.url)), [reg, ...codes] = process.argv.slice(2);
const dir = join(process.env.SCRATCH, 'tc');
mkdirSync(dir, { recursive: true });
writeFileSync(join(dir, 'test_codes.lua'), `CODES={${codes.map(c => `"${c}"`).join(',')}} SHOTAT=${process.env.SHOTAT || 200}\n` +
  readFileSync(join(here, 'test_codes.lua'), 'utf8'));
const out = execFileSync('sh', [join(here, 'run.sh'), join(dir, 'test_codes.lua'), reg], { encoding: 'utf8' });
const SECRET = { sound: [6, 0, 1, 0], remote: [4, 1, 0, 0], semi: [4, 2, 0, 0], bonus: [4, 0, 0, 1], short: [5, 0, 0, 0], normal: [5, 0, 0, 0], long: [5, 0, 0, 0] };
let bad = 0;
for (const c of codes) {
  const l = (out.split('\n').find(x => x.startsWith(`CODE ${c} `)) || `CODE ${c} none`).trim();
  const d = decode(c, reg), f = l.split(' '), ram = (f[3] || 'ram=').slice(4).split(',').map(Number);
  let ok = f[2] === (d ? 'ok' : 'bad');
  if (ok && d && !d.secret) ok = [d.area - 1, d.stage - 1, d.bombs - 1, d.fire - 1].every((v, k) => ram[k] === v);
  if (ok && d && d.secret) {
    const t = { short: 45, normal: 75, long: 105 }[d.secret];
    ok = (t ? ram[4] === t : true) && (d.secret === 'remote' ? ram[5] === 1 : d.secret === 'semi' ? ram[5] === 2 : true) &&
      (d.secret === 'sound' ? ram[7] === 1 : true) && (d.secret === 'bonus' ? ram[8] === 1 : true);
  }
  bad += !ok;
  console.log(ok ? 'ok ' : 'BAD', l, d ? JSON.stringify(d) : 'rejected');
}
console.log(codes.length, 'codes,', bad, 'bad');
