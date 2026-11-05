// node tools/gb2/test_password.mjs : password.mjs against the table and the codes typed in Mesen
import { decode, encode, validate, allCodes, describe, TABLES, UNUSED } from './password.mjs';
import assert from 'node:assert';
for (let w = 1; w <= 8; w++) for (const v of ['us', 'jp']) assert.deepEqual(decode(encode(w), v), { value: 0x7F + w, kind: 'world', world: w, stage: 1 });
assert.equal(allCodes('us').length, 11);
assert.deepEqual(TABLES.us, TABLES.jp);
assert.equal(decode('2145').kind, 'soundtest');
assert.equal(decode('5656').kind, 'battle');
assert.equal(decode('4622').kind, 'powerup');
assert.ok(!validate('7824') && !validate('7824', 'jp') && UNUSED.us['7824'] === 0x89 && describe(0x89).kind === 'ending');
assert.deepEqual(describe(0x23), { value: 0x23, kind: 'stage', world: 3, stage: 4 });
assert.ok(!validate('0000') && !validate('856') && !validate('85666'));
assert.throws(() => encode(9));
console.log('ok');
