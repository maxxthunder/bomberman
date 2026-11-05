// node tools/max/test_password.mjs: encode -> decode round trip for every Charabom and level, and a few rejects.
import { CHARABOMS, encode, decode, validate } from './password.mjs';
let n = 0;
for (const c of CHARABOMS) for (const ver of ['blue', 'hikari']) {
  const [own] = encode({ own: [c.id] }, ver), d = decode(own, ver);
  if (d.id !== c.id || d.field !== 'owned' || d.value !== 1) throw new Error(own);
  for (let lv = 1; lv <= 99; lv++) {
    const [l] = encode({ level: { [c.id]: lv } }, ver), e = decode(l, ver);
    if (e.id !== c.id || e.field !== 'level' || e.value !== lv) throw new Error(l);
    n++;
  }
}
for (const bad of ['0101F0A1', '8001F1A1', '80010FA1', '8001ffa2', 'C32-EBA-C41', ''])
  if (validate(bad)) throw new Error('accepted ' + bad);
if (encode({ own: [30] }) !== null || encode({ level: { 0: 0 } }) !== null) throw new Error('range');
console.log(`ok: ${CHARABOMS.length} Charaboms, ${n} level codes round-trip`);
