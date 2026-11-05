// node tools/nes1/test_password.mjs : password.mjs round trips, plus codes typed in Mesen (US and JP)
import { decode, encode, validate, values, stageCode, maxCode, ALPHABET } from './password.mjs';
import assert from 'node:assert';
let n = 0;
for (let st = 0; st < 256; st++) for (let f = 0; f < 16; f++) for (let b = 1; b <= 16; b++) {
  const s = { stage: st, fire: f, bombs: b, speed: st & 1, wallPass: f & 1, detonator: b & 1, flamePass: (st >> 1) & 1, reveal: (st >> 2) & 1, score: (st * 7919 % 10000000) * 100 };
  const d = decode(encode(s));
  for (const k in s) assert.equal(d[k], s[k], k);
  n++;
}
// every code is the only code for its state: 16 data nibbles, 4 checks
assert.equal(encode(), 'BAHIMNJDJNMNMNMNMNMF');
assert.equal(stageCode(1), encode());
assert.equal(encode({ stage: 1, score: 12345600 }), 'IHABEEKBAFECPPEGKGKA');
assert.deepEqual(decode('NMIHPPBPCAFHABDPCPCH'), { stage: 1, score: 3591500, digits: [0, 0, 3, 5, 9, 1, 5], fire: 5, bombs: 10, speed: 1, wallPass: 0, detonator: 0, flamePass: 0, reveal: 0 });
assert.equal(decode('NMIHPPBPCAFHABDPPCCH').reveal, 1);              // letters 17/18 swapped: reveal on
assert.equal(decode('BOFEDJJDDJGKEFOLFMIH').stage, 74);
assert.equal(decode('IIIIIJJJJJKKKKKNNNNN').reveal, 3);
assert.equal(decode(maxCode(50)).stage, 50);
assert.ok(!validate('BABABABABABABABABABB') && !validate('BABA') && !validate('BABABABABABABABABABQ'));
assert.equal(values('BABABABABABABABABABA').length, 20);
assert.equal(ALPHABET.length, 16);
console.log('ok', n, 'states');
