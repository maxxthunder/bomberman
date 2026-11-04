// node tools/pce94/password.test.mjs -- self-check of password.mjs (111 valid codes, encoder round-trip, known codes).
import assert from 'node:assert';
import { decode, encode, validCodes, label } from './password.mjs';
const v = validCodes();
assert.equal(v.length, 111);
for (const c of v) { const s = decode(c); assert.equal(encode(s.area, s.cleared, s.last, s.alias), c); }
assert.equal(label(decode('0515')), 'Final area');
assert.equal(label(decode('6803')), 'Area 4 stage 1');
assert.equal(decode('1234'), null);
console.log('ok');
