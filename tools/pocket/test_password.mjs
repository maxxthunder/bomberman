// node tools/pocket/test_password.mjs : password.mjs round trip over every world / stage / power choice, the GameFAQs
// codes and the debug decoder's ranges.
import { decode, encode, validate, debugDecode, TABLE, BOSS_RUSH, ENDING } from './password.mjs';
import assert from 'node:assert';
const seen = new Set();
for (let w = 0; w < 5; w++) for (let s = 1; s <= 5; s++) for (const p of [false, true]) {
  const c = encode(w, s, p);
  if (p && s > 1) { assert.equal(c, null); continue; }
  const d = decode(c);
  assert.deepEqual([d.world, d.stage, d.kind], [w, s, p ? 'power' : 'stage']);
  seen.add(c);
}
assert.equal(decode(BOSS_RUSH).kind, 'boss');
assert.equal(decode(ENDING).kind, 'ending');
seen.add(BOSS_RUSH).add(ENDING);
assert.equal(seen.size, 32);
let n = 0;
for (let i = 0; i < 10000; i++) n += validate(String(i).padStart(4, '0'));
assert.equal(n, TABLE.length);
const faq = { '7693': 'Forest 1', '1893': 'Forest 5', '2805': 'Ocean 1', '8649': 'Ocean 5', '0238': 'Wind 1',
  '8146': 'Wind 5', '9156': 'Cloud 1', '0687': 'Cloud 5', '3725': 'Evil 1', '3752': 'Evil 5' };
for (const [c, l] of Object.entries(faq)) { const d = decode(c); assert.equal(`${d.worldName} ${d.stage}`, l); }
assert.deepEqual(debugDecode('1213'), { invincible: true, world: 2, worldName: 'Wind', clockStop: true, stage: 4 });
assert.equal(debugDecode('2000'), null);
assert.equal(TABLE.filter(debugDecode).length, 0);   // no table code is also a debug code
console.log('ok: 32 codes, 10000 checked');
