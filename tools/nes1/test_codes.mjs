// node tools/nes1/test_codes.mjs <us|jp|fds> CODE [CODE...] : type the codes in Mesen with the pad (test_codes.lua via
// run.sh; MESEN and SCRATCH set) and check the RAM the game set against password.mjs. Screenshots: $SCRATCH/test_codes_<reg>/<code>.png
import { decode } from './password.mjs';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const here = dirname(fileURLToPath(import.meta.url)), [reg, ...codes] = process.argv.slice(2);
const dir = join(process.env.SCRATCH, 'tc');
mkdirSync(dir, { recursive: true });
writeFileSync(join(dir, 'test_codes.lua'), `CODES={${codes.map(c => `"${c}"`).join(',')}} REJ=${({ jp: 0xDBC4, fds: 0xBBC4 })[reg] || 0xDBCC} SHOTAT=${process.env.SHOTAT || 200}\n` +
  readFileSync(join(here, 'test_codes.lua'), 'utf8'));
const out = execFileSync('sh', [join(here, 'run.sh'), join(dir, 'test_codes.lua'), reg], { encoding: 'utf8' });
let bad = 0;
for (const c of codes) {
  const l = out.split('\n').find(x => x.startsWith(`CODE ${c} `));
  const d = decode(c);
  const want = d ? `ok=1 ram=${[d.stage, ...d.digits, d.fire << 4, d.bombs - 1, d.speed, d.wallPass, d.detonator].join(',')},` : 'ok=0';
  const ok = l && (d ? l.includes(want) && l.endsWith(`,${d.flamePass},${d.reveal}`.trimEnd()) || l.trimEnd().endsWith(`,${d.flamePass},${d.reveal}`) && l.includes(want) : l.includes('ok=0'));
  bad += !ok;
  console.log(ok ? 'ok ' : 'BAD', l ? l.trim() : `CODE ${c} none`);
}
console.log(codes.length, 'codes,', bad, 'bad');
