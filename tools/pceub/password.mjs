// Bomberman: Users Battle (PC Engine, 1990) password codec: the 1990 Bomberman's system, still in this card but unreachable.
// Decoder $C8AB, encoder $C73D (bank 2 at $C000). No dependencies.
// 8 letters; letters 2k, 2k+1 are byte k (low nibble, high nibble) as indexes into that pair's 16-letter row ($CA88).
// Byte 0: bits 0-2 = shift n, bit 3 = 0, bit 4 = 1, bits 5/6/7 invert bytes 1/2/3.
// Bytes 1-3 (big-endian), shifted right by n, hold round, stage, bombs, fire, speed and a 5-bit count of their 1 bits,
// each field's bits scattered by the tables $CA5C (masks) / $CA72 (byte indexes).

export const ROWS = ['MUROYAGCQXSKIWHB', 'WRECKFVBYHOZNAGL', 'NEWSLOGIMPHJTVBQ', 'NUCLEARHPSTVZYGK'];
// [byte 1-3, mask], most significant bit first
export const FIELDS = {
  round: [[1, 0x08], [3, 0x04], [2, 0x10], [2, 0x04]],  // 1-8 (stored +1; $2849 = round-1)
  stage: [[3, 0x40], [2, 0x40], [1, 0x01], [3, 0x08]],  // 1-8 ($284A = stage-1)
  bombs: [[2, 0x80], [1, 0x10], [2, 0x01], [3, 0x20]],  // 1-10 ($284B)
  fire: [[3, 0x10], [2, 0x08], [3, 0x02], [1, 0x02]],   // 1-15 ($284C)
  speed: [[1, 0x20]],                                    // 0-1 ($284D, roller skate)
};
export const CHECK = [[2, 0x02], [3, 0x01], [1, 0x04], [3, 0x80], [2, 0x20]];
export const SPECIAL = { BOMSOUND: 'Rejected, but sets $341B = $FF: the next valid password opens the sound test' };

const ones = v => v.toString(2).split('1').length - 1;
const gather = (b, spec) => spec.reduce((v, [i, m]) => (v << 1) | (b[i] & m ? 1 : 0), 0);

// -> {round, stage, bombs, fire, speed, flip, shift} or null if the game rejects it.
export function decode(code) {
  code = String(code).trim().toUpperCase();
  if (code.length !== 8) return null;
  const v = [...code].map((c, i) => ROWS[i >> 1].indexOf(c));
  if (v.includes(-1)) return null;
  let b = [0, 1, 2, 3].map(k => v[2 * k] | (v[2 * k + 1] << 4));
  for (let k = 1; k <= 3; k++) if ((b[0] >> (4 + k)) & 1) b[k] ^= 0xff;
  if ((b[0] & 0x18) !== 0x10) return null;
  const x = ((b[1] << 16) | (b[2] << 8) | b[3]) >>> (b[0] & 7);
  b = [b[0], (x >> 16) & 255, (x >> 8) & 255, x & 255];
  const f = {};
  let n = 0;
  for (const k in FIELDS) { f[k] = gather(b, FIELDS[k]); n += ones(f[k]); }
  if (!(f.round >= 1 && f.round <= 8 && f.stage >= 1 && f.stage <= 8 && f.bombs >= 1 && f.bombs <= 10 && f.fire >= 1)) return null;
  if (gather(b, CHECK) !== n) return null;
  return { ...f, flip: b[0] >> 5, shift: b[0] & 7 };
}

export function validate(code) { return decode(code) !== null; }

// round 1-8, stage 1-8, bombs 1-10, fire 1-15, speed 0/1; flip 0-7, shift 0-7 (the game itself uses shift 0-2).
// Returns null when the shift pushes a set bit out of the 24 bits.
export function encode(round, stage, bombs = 1, fire = 1, speed = 0, flip = 0, shift = 0) {
  if (!(round >= 1 && round <= 8 && stage >= 1 && stage <= 8 && bombs >= 1 && bombs <= 10 && fire >= 1 && fire <= 15 &&
    (speed === 0 || speed === 1) && flip >= 0 && flip <= 7 && shift >= 0 && shift <= 7)) throw new RangeError('bad value');
  const f = { round, stage, bombs, fire, speed };
  let b = [0, 0, 0, 0], n = 0;
  const put = (spec, val) => spec.forEach(([i, m], j) => { if ((val >> (spec.length - 1 - j)) & 1) b[i] |= m; });
  for (const k in FIELDS) { put(FIELDS[k], f[k]); n += ones(f[k]); }
  put(CHECK, n);
  const x = ((b[1] << 16) | (b[2] << 8) | b[3]) * 2 ** shift;
  if (x >= 2 ** 24) return null;
  b = [(flip << 5) | 0x10 | shift, (x >> 16) & 255, (x >> 8) & 255, x & 255];
  for (let k = 1; k <= 3; k++) if ((flip >> (k - 1)) & 1) b[k] ^= 0xff;
  return b.map((v, k) => ROWS[k][v & 15] + ROWS[k][v >> 4]).join('');
}

// The 24 codes the game can show for a state (it picks flip 0-7 and shift 0-2 at random, $CB15).
export function gameCodes(round, stage, bombs = 1, fire = 1, speed = 0) {
  const out = [];
  for (let s = 0; s < 3; s++) for (let fl = 0; fl < 8; fl++) out.push(encode(round, stage, bombs, fire, speed, fl, s));
  return out;
}
