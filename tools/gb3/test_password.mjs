// node tools/gb3/test_password.mjs : password.mjs round trip over every area / stage / extra / cleared / shop
// combination it can encode, plus the codes typed in Mesen (tools/gb3/test_codes.py) and the GameFAQs lists.
import { decode, encode, validate, stageCode, BOSS_ATTACK } from './password.mjs';
import assert from 'node:assert';
const seen = new Set();
for (let a = 0; a < 7; a++) for (let s = 1; s <= 6; s++) for (const x of s === 6 ? [0, 1, 2] : [0])
  for (let cl = 0; cl < 128; cl++) for (let shop = 0; shop < 256; shop++) {
    const cleared = [0, 1, 2, 3, 4, 5, 6].map(i => (cl >> i) & 1);
    const c = encode(a, s, cleared, shop, x);
    if (!c) continue;
    const d = decode(c);
    assert.equal(d.area, a); assert.equal(d.stage, s); assert.equal(d.extra, x); assert.equal(d.shop, shop);
    assert.equal(encode(d.area, d.stage, d.cleared, d.shop, d.extra), c);
    seen.add(c);
  }
assert.equal(stageCode(0, 1), '0986400');
assert.deepEqual(decode('F775818'), { area: 6, areaName: 'Evil', stage: 6, extra: 0, cleared: [1, 1, 1, 1, 1, 1, 0], shop: 255, check: 0 });
assert.deepEqual(decode(BOSS_ATTACK), { special: 'boss' });
assert.ok(!validate('CEBFCC6') && !validate('0000000') && !validate('098640'));   // GameFAQs "maxed" Aqua 1: check fails
assert.equal(seen.size + 1, 20329);   // + DEB1F7F: every code the game takes (counted over all 2^28 in password.mjs's terms)
console.log('ok', seen.size, 'distinct codes');
