// Super Bomberman 2 password codec (USA, Europe, Japan, USA beta and Caravan all share it).
// No checksum: the game compares the 4 digits with an 11-entry table at $CC:0000 (check at $CC:1926 USA)
// and keeps the matching index in $1C6A. 0-4: world 1-5; 5-9: world 1-5 with full power;
// 10: sudden-death flag $1C68. The 12th table entry (0000) is never reached by the loop.

export const CODES = ["4361", "6442", "3903", "9564", "7735", "1111", "5462", "6763", "8784", "6925", "5656"];
export const FULL_POWER = { speed: 2, bombs: 6, fire: 5, remote: true, glove: true }; // $80E0 $80E1 $80E2 $80F3 $80FE
export const NORMAL = { speed: 1, bombs: 1, fire: 0, remote: false, glove: false };

/** '4361' -> { index, world, stage, fullPower, kit, suddenDeath } or null if the game rejects it. */
export function decode(code) {
  code = String(code);
  const i = /^\d{4}$/.test(code) ? CODES.indexOf(code) : -1;
  if (i < 0) return null;
  if (i === 10) return { index: 10, suddenDeath: true };
  const world = (i % 5) + 1;
  return { index: i, world, stage: 0x10 * world, fullPower: i >= 5, kit: i >= 5 ? FULL_POWER : NORMAL, suddenDeath: false };
}

/** encode({ world: 1-5, fullPower }) or encode({ suddenDeath: true }) -> '6763' */
export function encode({ world, fullPower = false, suddenDeath = false } = {}) {
  if (suddenDeath) return CODES[10];
  if (!Number.isInteger(world) || world < 1 || world > 5) throw new RangeError("world must be 1-5");
  return CODES[world - 1 + (fullPower ? 5 : 0)];
}

export function validate(code) {
  return decode(code) !== null;
}
