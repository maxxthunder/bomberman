// node tools/pce90/test_password.mjs : password.mjs round trip over every state, plus codes typed in Mesen
import { decode, encode, validate, gameCodes } from './password.mjs';
import assert from 'node:assert';
let n = 0;
for (let r = 1; r <= 8; r++) for (let s = 1; s <= 8; s++) for (let b = 1; b <= 10; b++) for (let f = 1; f <= 15; f++)
  for (let sp = 0; sp < 2; sp++) {
    for (const c of gameCodes(r, s, b, f, sp)) {
      const d = decode(c);
      assert.deepEqual([d.round, d.stage, d.bombs, d.fire, d.speed], [r, s, b, f, sp], c);
    }
    n++;
  }
assert.equal(n, 19200);
assert.equal(encode(1, 1), 'MUVWLNPC');
assert.equal(encode(8, 8, 10, 15, 1), 'MUOEPHLA');
assert.deepEqual(decode('CUVYVPNP'), { round: 1, stage: 3, bombs: 3, fire: 14, speed: 0, flip: 0, shift: 7 });
assert.ok(!validate('BOMSOUND') && !validate('MUVWLNPU') && !validate('MUVWLNP'));
console.log('ok', n, 'states');
