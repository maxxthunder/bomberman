// Bomberman GB 2 (Japan, 1995) / Bomberman GB (USA, Europe) password codec. No dependencies.
// The password is 4 digits, compared with a fixed table of 5-byte records (4 ASCII digits + a value) in bank $0F:
// US $0F:7F72, JP $0F:54C1, 12 records tried ($00:35CC US / $00:35F9 JP). Nothing is computed; the two versions
// take the same 11 codes. The value goes to $C1BD and is dispatched at $00:3639 (US):
//   $00-$7F  $C100 = value (world << 4 | stage), $C101 = 0, start   - handler only, no code in the table
//   $80-$87  $C100 = (value & 7) << 4: start at world 1-8, stage 1
//   $88      sound test ($00:2146)
//   $89      the ending ($00:1E3A)                                  - US: only in an unused copy of the table (7824)
//   $8A      $C11A = 1, battle ($00:2AE8)
//   $8B      $C11B = 1, sound test                                  - handler only
//   $8C      the closing screen after the staff roll ($00:34E9)     - handler only
//   $8D      $C100 = 0, $C125 = $C126 = $7F, $C11E = 1: world 1 with every power-up maxed
// Anything else ($8E-$FF) returns to the title ($00:367F).

const CODES = [['8566', 0x80], ['9634', 0x81], ['1637', 0x82], ['0320', 0x83], ['6524', 0x84], ['3260', 0x85],
  ['4783', 0x86], ['5472', 0x87], ['2145', 0x88], ['5656', 0x8A], ['4622', 0x8D]];
export const TABLES = { jp: Object.fromEntries(CODES), us: Object.fromEntries(CODES) };
// US only: the unreferenced older copy of the table at $0F:5447 has one more record. The game never reads it.
export const UNUSED = { us: { '7824': 0x89 } };
export const KINDS = { 0x88: 'soundtest', 0x89: 'ending', 0x8A: 'battle', 0x8B: 'soundtest2', 0x8C: 'closing', 0x8D: 'powerup' };

// value -> what the dispatcher does with it
export function describe(v) {
  if (v < 0x80) return { value: v, kind: 'stage', world: (v >> 4) + 1, stage: (v & 15) + 1 };
  if (v < 0x88) return { value: v, kind: 'world', world: (v & 7) + 1, stage: 1 };
  return { value: v, kind: KINDS[v] || 'title' };
}

// -> describe(value) for a code the game accepts, or null (rejected)
export function decode(code, version = 'us') {
  const v = TABLES[version][String(code).trim()];
  return v === undefined ? null : describe(v);
}

export function validate(code, version = 'us') { return decode(code, version) !== null; }

// world 1-8 -> its code (the table has no stage codes; the game shows these after each world)
export function encode(world) {
  if (!(world >= 1 && world <= 8)) throw new RangeError('bad world');
  return CODES[world - 1][0];
}

export function allCodes(version = 'us') { return Object.keys(TABLES[version]).map(c => [c, decode(c, version)]); }
