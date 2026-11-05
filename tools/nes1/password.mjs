// Bomberman (NES / Famicom, 1987) password codec. Same in the USA and Japan carts.
// Decoder $DB7A, encoder $E2BD (US; 16 KB PRG at $C000). No dependencies.
// 20 letters A-P. Letter k is the nibble ALPHABET.indexOf(letter) (entry $DB51 via $DFA0, display $E32F via $E388).
// Chain: value[k] = (letter[k] + letter[k-1] + 7) & 15, letter[-1] = 0 ($DB7E).
// Values 4, 9, 14 are the 4-bit sums of the four before them; value 19 is the sum of values 15-18 plus twice
// values 4, 9 and 14 ($DB93-$DBCA). Every other value goes straight into RAM with no range check ($DBCF, list $E360).

export const ALPHABET = 'AOFKCPGELBHMJDNI';
// value index -> what it sets. score0 is the top digit ($61), score6 the last ($67); the screen adds a fixed 00.
export const LAYOUT = ['score6', 'detonator', 'stageLo', 'score0', 'check1',
  'score5', 'fire', 'score3', 'flamePass', 'check2',
  'bombs', 'score2', 'speed', 'score1', 'check3',
  'score4', 'reveal', 'stageHi', 'wallPass', 'check4'];
// RAM written by each value (US and JP): fire goes to the high nibble of $73, stage = stageHi<<4 | stageLo in $58,
// bombs is the count minus 1 in $74.
export const RAM = ['$67', '$77', '$58 lo', '$61', '-', '$66', '$73 hi', '$64', '$79', '-',
  '$74', '$63', '$75', '$62', '-', '$65', '$94', '$58 hi', '$76', '-'];

const checks = v => {
  const c1 = (v[0] + v[1] + v[2] + v[3]) & 15, c2 = (v[5] + v[6] + v[7] + v[8]) & 15, c3 = (v[10] + v[11] + v[12] + v[13]) & 15;
  return [c1, c2, c3, (v[15] + v[16] + v[17] + v[18] + 2 * (c1 + c2 + c3)) & 15];
};

// -> the 20 nibble values, or null if the game rejects the code (bad length, a letter outside A-P, a checksum).
export function values(code) {
  code = String(code).replace(/\s+/g, '').toUpperCase();
  if (code.length !== 20) return null;
  const l = [...code].map(c => ALPHABET.indexOf(c));
  if (l.includes(-1)) return null;
  const v = l.map((x, k) => (x + (k ? l[k - 1] : 0) + 7) & 15);
  const c = checks(v);
  return c[0] === v[4] && c[1] === v[9] && c[2] === v[14] && c[3] === v[19] ? v : null;
}

// -> {stage, score, digits, fire, bombs, speed, wallPass, detonator, flamePass, reveal} or null.
// stage is $58 (1-50 in play, 0-255 accepted); bombs is the bomb count ($74 + 1); fire the blast length ($73 >> 4).
// digits are the 7 score digits top first (each 0-15; 10-15 are not real digits); score = digits as a number x 100,
// or null when a digit is over 9. speed / wallPass / detonator / flamePass / reveal are the raw nibbles (0 = off).
export function decode(code) {
  const v = values(code);
  if (!v) return null;
  const f = {};
  LAYOUT.forEach((n, k) => { f[n] = v[k]; });
  const digits = [0, 1, 2, 3, 4, 5, 6].map(k => f['score' + k]);
  return {
    stage: f.stageHi << 4 | f.stageLo, score: digits.every(d => d < 10) ? Number(digits.join('')) * 100 : null, digits,
    fire: f.fire, bombs: f.bombs + 1, speed: f.speed, wallPass: f.wallPass, detonator: f.detonator,
    flamePass: f.flamePass, reveal: f.reveal,
  };
}

export function validate(code) { return values(code) !== null; }

// The code the game shows for a state (it is the only code for it). Takes the decode() shape; missing fields are
// the new-game values (stage 1, score 0, fire 1, 1 bomb, everything else off). score must be a multiple of 100
// below 1,000,000,000; give digits instead for digits over 9. Booleans count as 1/0.
export function encode(s = {}) {
  const n = (x, d, lo, hi, name) => {
    x = x === undefined ? d : +x;
    if (!(Number.isInteger(x) && x >= lo && x <= hi)) throw new RangeError('bad ' + name);
    return x;
  };
  const stage = n(s.stage, 1, 0, 255, 'stage');
  let digits = s.digits;
  if (!digits) {
    const sc = n(s.score, 0, 0, 999999900, 'score');
    if (sc % 100) throw new RangeError('score must end in 00');
    digits = String(sc / 100).padStart(7, '0').split('').map(Number);
  }
  if (digits.length !== 7) throw new RangeError('7 digits');
  const f = {
    stageLo: stage & 15, stageHi: stage >> 4, fire: n(s.fire, 1, 0, 15, 'fire'), bombs: n(s.bombs, 1, 1, 16, 'bombs') - 1,
    speed: n(s.speed, 0, 0, 15, 'speed'), wallPass: n(s.wallPass, 0, 0, 15, 'wallPass'),
    detonator: n(s.detonator, 0, 0, 15, 'detonator'), flamePass: n(s.flamePass, 0, 0, 15, 'flamePass'),
    reveal: n(s.reveal, 0, 0, 15, 'reveal'),
  };
  digits.forEach((d, k) => { f['score' + k] = n(d, 0, 0, 15, 'digit'); });
  const v = LAYOUT.map(k => f[k] ?? 0);
  [v[4], v[9], v[14], v[19]] = checks(v);
  let prev = 0;
  return v.map(x => ALPHABET[prev = (x - prev - 7) & 15]).join('');
}

// Codes for the start of each stage with the new-game power-ups and score 0, plus a maxed-out set.
export function stageCode(stage, extra = {}) { return encode({ stage, ...extra }); }
export function maxCode(stage = 50) {
  return encode({ stage, fire: 5, bombs: 10, speed: 1, wallPass: 1, detonator: 1, flamePass: 1 });
}
