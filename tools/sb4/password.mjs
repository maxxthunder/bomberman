// Super Bomberman 4 (Japan) passwords. No algorithm: the game compares the 4-digit number with a
// table of 50 words at $C2:AE9A (loop $C2:A916); the index goes to $92 and the compare chain at
// $C2:A9E3 gives twelve of them a special effect. Checked against the game for all 10,000 codes.
export const TABLE = [7352, 8831, 7255, 5714, 5289, 1352, 6892, 6722, 7793, 6428, 8492, 7490, 4370, 6682, 4677, 4692,
  4680, 2247, 5725, 7821, 5890, 7258, 3379, 6009, 5389, 4080, 2501, 5736, 3211, 5589, 8902, 721,
  3703, 2679, 2479, 4792, 6790, 1574, 7777, 4622, 520, 903, 1019, 1222, 1107, 827, 107, 1009, 5656, 164];
export const SPECIAL = {
  7777: 'Battle: the winner of a single-match round turns gold next round',
  4622: 'Battle: start-position/block set 1',
  520: 'Battle: start-position/block set 2',
  903: 'Battle: start-position/block set 3',
  1019: 'Normal game: 1-1 with full power-ups',
  1222: 'Normal game: 2-1 with full power-ups',
  1107: 'Normal game: 3-1 with full power-ups',
  827: 'Normal game: 4-1 with full power-ups',
  107: 'Normal game: 5-1 with full power-ups',
  1009: 'Ending',
  5656: 'Battle: super attacks without the tired wait',
  164: 'Battle: wider random item pool',
};
const pad = v => String(v).padStart(4, '0');
const stageName = i => `${Math.floor(i / 8) + 1}-${i % 8 + 1}`;

// '7352' -> {code, index, kind:'stage', stage:'1-1'} | {code, index, kind:'special', effect} | null
export function decode(code) {
  const s = String(code);
  if (!/^\d{4}$/.test(s)) return null;
  const v = Number(s), i = TABLE.indexOf(v);
  if (i < 0) return null;
  return v in SPECIAL ? { code: s, index: i, kind: 'special', effect: SPECIAL[v] }
    : { code: s, index: i, kind: 'stage', stage: stageName(i) };
}
export const validate = code => decode(code) !== null;

// '3-4' or index 0-37 -> code. Slots 38/39 (5-7, 5-8) hold 7777/4622, which the special check catches first.
export function encode(stage) {
  const i = typeof stage === 'number' ? stage : (Number(stage[0]) - 1) * 8 + Number(stage[2]) - 1;
  if (!(i >= 0 && i < 38)) throw new RangeError('stage passwords exist only for 1-1 .. 5-6');
  return pad(TABLE[i]);
}
// every accepted code, in table order
export const all = () => TABLE.map(v => decode(pad(v)));
