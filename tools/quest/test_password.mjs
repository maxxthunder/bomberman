// node tools/quest/test_password.mjs: encode -> decode round trip for every weapon, equipment, item (each count 1-15
// for the bomb components) and heart count in both versions, makeSave -> checkSave, and a few rejects.
import { KINDS, BLOCK, MAX_HEARTS, CHEATS, encode, decode, validate, makeSave, checkSave } from './password.mjs';
let n = 0;
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
for (const ver of Object.keys(BLOCK)) {
  for (const [kind, [names]] of Object.entries(KINDS)) for (const e of names)
    for (let c = 1; c <= (kind === 'item' && e.id <= 8 ? 15 : 1); c++) {
      const [code] = encode({ [kind]: { [e.id]: c } }, ver), d = decode(code, ver);
      if (!same(d, { kind, id: e.id, name: e.name, value: c })) throw new Error(ver + ' ' + code);
      n++;
    }
  for (let h = 1; h <= MAX_HEARTS; h++) {
    const [a, b] = encode({ hearts: h }, ver);
    if (!same(decode(a, ver), { kind: 'hearts', value: h }) || !same(decode(b, ver), { kind: 'hp', value: h })) throw new Error(a);
  }
}
// the two versions' blocks sit one byte apart: a US code is a different (or no) entry in Japan
if (decode(encode({ weapon: [8] }, 'us')[0], 'jp')?.id === 8) throw new Error('version offset');
for (const bad of [CHEATS.invincible, CHEATS.invincibleGG, '0120A3CE', '011FA3CE', '8010A3CE', ''])
  if (validate(bad, 'us')) throw new Error('accepted ' + bad);
if (encode({ weapon: [29] }) !== null || encode({ item: { 1: 16 } }) !== null || encode({ hearts: 11 }) !== null) throw new Error('range');
const blk = Uint8Array.from({ length: 0xE4 }, (_, i) => i * 7);
const sav = makeSave(blk);
if (!checkSave(sav)) throw new Error('makeSave');
sav[0x20] ^= 1;
if (checkSave(sav)) throw new Error('checkSave');
console.log(`ok: ${n} item codes and ${2 * MAX_HEARTS} heart codes round-trip in both versions; save checksum ok`);
