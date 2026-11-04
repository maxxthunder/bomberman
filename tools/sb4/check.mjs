// node tools/sb4/check.mjs [rom]: password.mjs self-check (and its table against the ROM's $C2:AE9A)
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { TABLE, decode, encode, validate } from './password.mjs';
let n = 0; for (let i = 0; i < 10000; i++) n += validate(String(i).padStart(4, '0'));
assert.equal(n, 50);
assert.equal(encode('1-1'), '7352'); assert.equal(encode('5-2'), '2679'); assert.equal(decode('2609'), null);
for (let i = 0; i < 38; i++) assert.equal(decode(encode(i)).index, i);
if (process.argv[2]) {
  const r = readFileSync(process.argv[2]);
  assert.deepEqual(TABLE, [...Array(50)].map((_, i) => r.readUInt16LE(0x2AE9A + 2 * i)));
}
console.log('ok');
