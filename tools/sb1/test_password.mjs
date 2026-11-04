// node tools/sb1/test_password.mjs : checks password.mjs against password.py's rules and the GameFAQs codes
import { decode, encode, allCodes, validate, continueCodes } from './password.mjs';
import assert from 'node:assert';
const all = allCodes();
assert.equal(all.length, 192);
for (const c of all) { const d = decode(c); assert.equal(encode(d.world, d.stage, d.salt), c); }
assert.deepEqual(decode('5555'), { world: 1, stage: 1, salt: 0, index: 0 });
assert.equal(decode('7632').world, 6); assert.equal(decode('7632').stage, 7);
assert.ok(!validate('5656') && !validate('0000') && !validate('8555'));
assert.ok(continueCodes(5, 8).includes('2234'));
console.log('ok', all.length);
