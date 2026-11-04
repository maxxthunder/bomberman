// Super Bomberman (SNES) password codec. Same in US, EU, JP and the 1993-05-11 beta.
// Decoder $C5:72B0, encoder $C5:7FB9 (US addresses). No dependencies.
// A password is 4 digits 0-7. DEC maps each digit to a 3-bit value t0 t1 t2 t3:
//   t1 = world-1, t2 = stage-1, t3 = salt (even; random when the game makes a code), t0 = (t1+t2+t3) & 7.
// Valid iff t3 is even, t0 matches and t1*8+t2 < 48: 48 stages x 4 salts = 192 codes.

export const DEC = [1, 3, 4, 6, 2, 0, 5, 7];               // $C3:0D40, digit -> value
export const ENC = [5, 0, 4, 1, 2, 6, 3, 7];               // $C3:0D30, value -> digit
export const SALTS = [0, 2, 4, 6];
export const SPECIAL = { '5656': 'Small Bomberman in Normal Game (sets $0C90; returns to the title)' };

// -> {world, stage, salt, index} or null if the game rejects it. index = (world-1)*8 + stage-1, the value stored in $00A4.
export function decode(code) {
  code = String(code).trim();
  if (!/^[0-7]{4}$/.test(code)) return null;
  const t = [...code].map(c => DEC[+c]);
  if (t[3] & 1 || ((t[1] + t[2] + t[3]) & 7) !== t[0] || t[1] * 8 + t[2] >= 48) return null;
  return { world: t[1] + 1, stage: t[2] + 1, salt: t[3], index: t[1] * 8 + t[2] };
}

export function validate(code) { return decode(code) !== null; }

// world 1-6, stage 1-8, salt 0/2/4/6
export function encode(world, stage, salt = 0) {
  if (!(world >= 1 && world <= 6 && stage >= 1 && stage <= 8 && SALTS.includes(salt))) throw new RangeError('bad world/stage/salt');
  const t1 = world - 1, t2 = stage - 1;
  return [(t1 + t2 + salt) & 7, t1, t2, salt].map(v => ENC[v]).join('');
}

// All 4 codes for one stage, in salt order.
export function codesFor(world, stage) { return SALTS.map(s => encode(world, stage, s)); }

// What the game shows on the CONTINUE screen after a game over: a boss stage (x-8) is stepped back to x-7 first ($C5:6F23).
export function continueCodes(world, stage) { return codesFor(world, stage === 8 ? 7 : stage); }

export function allCodes() {
  const out = [];
  for (let i = 0; i < 4096; i++) { const c = i.toString(8).padStart(4, '0'); if (decode(c)) out.push(c); }
  return out;
}
