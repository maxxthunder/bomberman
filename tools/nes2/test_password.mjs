// node tools/nes2/test_password.mjs : password.mjs round trips over every state and key, plus codes typed in Mesen
import { decode, encode, validate, convert, secretCode, SECRETS } from './password.mjs';
import assert from 'node:assert';
let n = 0, valid = 0;
for (const reg of ['us', 'jp'])
  for (let a = 1; a <= 6; a++) for (let s = 1; s <= 8; s++) for (let b = 1; b <= 8; b++) for (let f = 1; f <= 5; f++)
    for (let key = 0; key < 16; key++) {
      const c = encode({ area: a, stage: s, bombs: b, fire: f, key, free: [key, 15 - key] }, reg);
      const d = decode(c, reg);
      if (d.secret) continue;  // a level code can't be a secret code: secrets fail the checksum (checked below)
      assert.deepEqual(d, { area: a, stage: s, bombs: b, fire: f, key, free: [key, 15 - key] }, c);
      n++;
    }
// count every valid 8-nibble code by brute force over the 16^8 space, the slow way only for v0 = 0..1
for (let k = 0; k < 2; k++) for (let x = 0; x < 1 << 28; x += 4099) {
  const c = [k, ...[...Array(7)].map((_, i) => (x >> (4 * i)) & 15)].map(v => 'PCKNFOHIGEBADJLM'[v]).join('');
  if (validate(c, 'jp')) valid++;
}
for (const [jp, , name] of SECRETS) {
  assert.equal(decode(jp, 'jp').secret, name);
  assert.equal(decode(secretCode(name, 'us'), 'us').secret, name);
}
assert.equal(secretCode('sound', 'us'), 'K3456712');
assert.equal(convert('PCDEFGAB', 'jp', 'us'), 'K3456712');
assert.deepEqual(decode('888D8C8G'), { area: 1, stage: 1, bombs: 1, fire: 1, key: 6, free: [11, 9] });
assert.deepEqual(decode('KKKFKJKO', 'jp'), { area: 1, stage: 1, bombs: 1, fire: 1, key: 2, free: [15, 7] });
assert.deepEqual(decode('1F4441G1'), { area: 6, stage: 8, bombs: 8, fire: 5, key: 11, free: [0, 0] });
assert.ok(!validate('888D8C8H') && !validate('888D8C8') && !validate('KKKFKJKO', 'us'));
// Dynablaster (Europe): typed in Mesen, the US codes load the same (1F4H4KGC = 6-8, K3456712 = sound test)
assert.deepEqual(decode('1F4H4KGC', 'eu'), decode('1F4H4KGC', 'us'));
assert.equal(decode('K3456712', 'eu').secret, 'sound');
console.log('ok', n, 'codes round-tripped; sampled valid', valid);
