// node tools/sel/test_password.mjs: Bomber Boy codes round-trip, and the codes checked in Mesen decode as logged.
import { decode, encode, validate } from './password.mjs';
const assert = (c, m) => { if (!c) throw new Error(m); };
for (let i = 0; i < 256; i++) for (const g of [0, 1, 100, 255, 256, 9999, 65535]) {
  const c = encode(i, g), d = decode(c);
  assert(d && d.islands === i && d.gold === g, `${i} ${g} ${c}`);
}
assert(encode(0, 100) === 'J6O1JOJ1', 'new game');             // Mesen: stage select, My Town, 100 gold
assert(encode(0x5A, 0x270F) === 'K3RMPEGE', 'game encoder');   // the CONTINUE screen showed it for $5A, 9,999 gold
assert(!validate('J6O1JOJ2') && !validate('J6O1JOJV'), 'rejects');
console.log('ok: every state round-trips');
