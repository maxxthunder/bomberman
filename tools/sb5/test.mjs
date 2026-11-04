// node tools/sb5/test.mjs : checks password.mjs against codes verified in Mesen.
import assert from "assert";
import { encode, decode, validate, option } from "./password.mjs";
assert.deepStrictEqual(decode("U04GJL"), { body: 0, color: 5, bomb: 7, fire: 6, speed: 7, items: 0b101110001 });
assert.deepStrictEqual(decode("23D830"), { body: 9, color: 2, bomb: 7, fire: 15, speed: 7, items: 511 });
assert.strictEqual(decode("kr3mt9").body, 8);
for (const c of ["UO4GJL", "XROPLG", "D24GJA", "ABCDE"]) assert(!validate(c), c);
for (let i = 0; i < 4096; i++) {
  const f = { body: i & 15, color: i >> 4 & 7, bomb: i % 8, fire: i % 16, speed: (i >> 3) % 8, items: (i * 37) % 512 };
  assert.deepStrictEqual(decode(encode(f)), f);
}
assert.strictEqual(option("0719"), null);
assert(option("0719", "caravan") && option("5656") && !option("1234"));
console.log("ok");
