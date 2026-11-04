// node tools/pce93/test_password.mjs : password.mjs against every state the decoder accepts and the codes in docs/pce93.md
import { decode, encode, validate, convert, encodeValues, decodeValues } from './password.mjs';
import assert from 'node:assert';
let n = 0;
for (let w = 0; w < 7; w++) for (let s = 0; s < 8; s++) for (let b = 1; b <= 10; b++) for (let f = 1; f <= 5; f++)
  for (let c = 0; c < 16; c++) for (let e = 0; e < 16; e++) {
    const d = [w, s, b, f, c, e], p = encodeValues(d);
    assert.ok(Math.max(...p) <= 19); assert.deepEqual(decodeValues(p), d);
    assert.equal(decodeValues(p, 'sp') !== null, c < 15 && e < 15); n++;
  }
assert.equal(n, 716800);
assert.equal(encode({ world: 1, stage: 1 }), 'CBCCBBDB');
assert.equal(encode({ world: 1, stage: 1 }, 'jp'), 'BABBAACA');
assert.deepEqual(decode('PMPHTZNF'), { world: 7, stage: 8, bombs: 10, fire: 5, cleared: 63, speed: 3 });
assert.equal(convert('PMPHTZNF', 'us', 'jp'), 'LJLFPTKD');
assert.ok(validate('LJLFPTKD', 'jp') && !validate('LJLFPTKD', 'sp') && !validate('BBBBBBBB') && !validate('AEIOUAEI'));
console.log('ok', n);
