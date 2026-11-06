// node tools/sel/test_password.mjs: Bomber Boy codes round-trip, and the codes checked in Mesen decode as logged.
import { decode, encode, validate, SYMBOLS_US, toUS, fromUS } from './password.mjs';
const assert = (c, m) => { if (!c) throw new Error(m); };
for (let i = 0; i < 256; i++) for (const g of [0, 1, 100, 255, 256, 9999, 65535]) {
  const c = encode(i, g), d = decode(c);
  assert(d && d.islands === i && d.gold === g, `${i} ${g} ${c}`);
}
assert(encode(0, 100) === 'J6O1JOJ1', 'new game');             // Mesen: stage select, My Town, 100 gold
assert(encode(0x5A, 0x270F) === 'K3RMPEGE', 'game encoder');   // the CONTINUE screen showed it for $5A, 9,999 gold
assert(!validate('J6O1JOJ2') && !validate('J6O1JOJV'), 'rejects');
// Atomic Punk: guide codes typed in Mesen
assert(JSON.stringify(decode('!!HH!H!G', SYMBOLS_US)) === '{"islands":0,"gold":65535}', 'US max gold');
assert(decode('TL77S.3=', SYMBOLS_US).islands === 0xBF && encode(0xBF, 1469, SYMBOLS_US) === 'TL77S.3=', 'US round trip');
assert(toUS('BOHIDJFEKJGKEFOLFHAC') === 'B3H2DJF1KJGK1F3LFH0C' && fromUS('B3H2DJF1KJGK1F3LFH0C') === 'BOHIDJFEKJGKEFOLFHAC', 'Game B letters');
console.log('ok: every state round-trips');
