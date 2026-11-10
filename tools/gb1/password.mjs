// Bomberman GB (Japan, 1994) / Wario Blast featuring Bomberman! (USA, Europe) password codec. No dependencies.
// The password is 4 digits, checked against a fixed table ($0A:42EE JP, $0A:4315 Wario): 5-byte records, 4 digit
// bytes ($E0 + digit) and a value, $FF ends the list ($0A:4272 JP, $0A:4255 Wario). Nothing is computed: a code
// not in the table is rejected.
// Value $00-$1F: start at stage value (round = v/4 + 1, stage = v%4 + 1, stage 4 = the boss), $C3F0 = v.
// Wario only: $00-$1F also sets $C3D5 = 1 (Bomberman), $20-$3F = the same stages as Wario ($C3D5 = 0, $C3F0 = v & $1F).
// JP $20 / Wario $40, $42: $C3FB = 1, start at 1-1 with every power-up (Wario: $40 Bomberman, $42 Wario).
// JP $21 / Wario $41, $43: the extra battle ($C3F1 = $0C, $34B2 JP / $3457 Wario; $41 Bomberman, $43 Wario).

const JP = ['4696', '7006', '8774', '5141', '9185', '4610', '2630', '3569', '8401', '8264', '0173', '2828', '4152',
  '3451', '4312', '0874', '1909', '5010', '2904', '1726', '3614', '0610', '9867', '9618', '1884', '7702', '6925',
  '7110', '5814', '8136', '0390', '3158'];
const WARIO = ['6964', '6007', '4778', '1415', '5819', '0164', '0362', '9653', '1048', '4628', '3710', '8282', '2514',
  '1543', '2134', '4780', '9091', '0105', '4092', '6271', '4163', '0160', '7689', '8169', '4881', '2077', '5296',
  '0117', '4185', '6318', '0930', '8513'];
// version -> code -> table value
export const TABLES = {
  jp: Object.fromEntries([...JP.map((c, v) => [c, v]), ['4622', 0x20], ['5656', 0x21]]),
  wario: Object.fromEntries([...JP.map((c, v) => [c, v]), ...WARIO.map((c, v) => [c, 0x20 + v]),
    ['4622', 0x40], ['5656', 0x41], ['2264', 0x42], ['6565', 0x43]]),
};
TABLES.col96 = TABLES.jp;   // Bomberman Collection (1996) carries the Japanese cart's banks unchanged

// -> {value, kind: 'stage'|'powerup'|'battle', round?, stage?, boss?, player: 'bomberman'|'wario'} or null (rejected)
export function decode(code, version = 'jp') {
  code = String(code).trim();
  const v = TABLES[version][code];
  if (v === undefined) return null;
  if (TABLES[version] === TABLES.jp) {   // the Japanese cart, and the Collection that carries it
    if (v < 0x20) return { value: v, kind: 'stage', round: (v >> 2) + 1, stage: (v & 3) + 1, boss: (v & 3) === 3, player: 'bomberman' };
    return { value: v, kind: v === 0x20 ? 'powerup' : 'battle', player: 'bomberman' };
  }
  if (v < 0x40) {
    const s = v & 0x1F;
    return { value: v, kind: 'stage', round: (s >> 2) + 1, stage: (s & 3) + 1, boss: (s & 3) === 3, player: v < 0x20 ? 'bomberman' : 'wario' };
  }
  return { value: v, kind: v & 1 ? 'battle' : 'powerup', player: v < 0x42 ? 'bomberman' : 'wario' };
}

export function validate(code, version = 'jp') { return decode(code, version) !== null; }

// round 1-8, stage 1-4 (4 = boss); player 'bomberman' (JP and Wario) or 'wario' (Wario Blast only)
export function encode(round, stage, player = 'bomberman', version = 'jp') {
  if (!(round >= 1 && round <= 8 && stage >= 1 && stage <= 4)) throw new RangeError('bad value');
  if (player === 'wario' && version !== 'wario') throw new RangeError('JP has no Wario');
  return (player === 'wario' ? WARIO : JP)[(round - 1) * 4 + stage - 1];
}

// every code of a version, as [code, decoded]
export function allCodes(version = 'jp') { return Object.keys(TABLES[version]).map(c => [c, decode(c, version)]); }
