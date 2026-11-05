// node tools/gb1/test_password.mjs : password.mjs round trip over every stage, both versions, plus the specials
import { decode, encode, validate, allCodes, TABLES } from './password.mjs';
import assert from 'node:assert';
for (const v of ['jp', 'wario'])
  for (const p of v === 'jp' ? ['bomberman'] : ['bomberman', 'wario'])
    for (let r = 1; r <= 8; r++) for (let s = 1; s <= 4; s++) {
      const d = decode(encode(r, s, p, v), v);
      assert.deepEqual([d.kind, d.round, d.stage, d.player], ['stage', r, s, p]);
    }
assert.equal(Object.keys(TABLES.jp).length, 34);
assert.equal(Object.keys(TABLES.wario).length, 68);
assert.equal(new Set(allCodes('wario').map(([c]) => c)).size, 68);
assert.equal(encode(1, 1), '4696');
assert.equal(encode(8, 4, 'wario', 'wario'), '8513');
assert.deepEqual(decode('4622'), { value: 0x20, kind: 'powerup', player: 'bomberman' });
assert.deepEqual(decode('5656'), { value: 0x21, kind: 'battle', player: 'bomberman' });
assert.deepEqual(decode('6565', 'wario'), { value: 0x43, kind: 'battle', player: 'wario' });
assert.deepEqual(decode('2264', 'wario'), { value: 0x42, kind: 'powerup', player: 'wario' });
assert.ok(!validate('6964') && validate('6964', 'wario') && !validate('0000') && !validate('469'));
assert.throws(() => encode(1, 1, 'wario', 'jp'));
console.log('ok');
