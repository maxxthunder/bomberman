// Pocket Bomberman (USA, Europe, GBC, 1998) password codec. No dependencies.
// 4 digits 0-9 ($C1C4-$C1C7). The check ($01:6565) compares them with a fixed table of 32 codes ($01:65AA); the
// index ($C35A) picks what the code does ($01:662E):
//   0-24   world (index / 5) and stage (index % 5) from the table at $01:668D; stage 5 is the world's boss
//   25-29  the same five worlds at stage 1 with power: $C352 = 1, $C353-$C356 = 6, 4, 4, 3 (player $0E, bombs, fire,
//          lives), and at the stage start the player's ability bits ($52) |= $0A ($02:45EB)
//   30     boss rush: Forest stage 5 with power; $C352 = 2, then 3 at the stage start ($02:45F3), and while it is 3 every
//          stage starts as stage 5 ($02:45FE)
//   31     $C352 = 3 straight from the password screen: the ending ($01:6A2D -> state 7)
// Everything else is rejected ($C1BD = 1). Checked against the game for all 10,000 codes (tools/pocket/fuzz.lua).
export const WORLDS = ['Forest', 'Ocean', 'Wind', 'Cloud', 'Evil'];       // $C1DC 0-4
export const TABLE = ['7693', '3905', '2438', '8261', '1893', '2805', '9271', '1354', '4915', '8649',
  '0238', '5943', '6045', '2850', '8146', '9156', '2715', '4707', '7046', '0687',
  '3725', '0157', '5826', '9587', '3752', '5656', '4622', '3790', '5294', '8906', '9437', '0278'];   // $01:65AA
export const BOSS_RUSH = '9437', ENDING = '0278';
const POWER = { bombs: 4, fire: 4, lives: 3 };      // $C354, $C355, $C356 for indexes 25-30
const NORMAL = { bombs: 1, fire: 1, lives: 3 };     // new game ($02:5570)
// -> {index, kind: 'stage' | 'power' | 'boss' | 'ending', world, worldName, stage 1-5, bombs, fire, lives} | null
export function decode(code) {
  code = String(code).trim();
  const i = TABLE.indexOf(code);
  if (i < 0) return null;
  if (i === 31) return { index: i, kind: 'ending' };
  const kind = i < 25 ? 'stage' : i < 30 ? 'power' : 'boss';
  const world = i < 25 ? Math.floor(i / 5) : i < 30 ? i - 25 : 0;
  const stage = i < 25 ? i % 5 + 1 : i < 30 ? 1 : 5;
  return { index: i, kind, world, worldName: WORLDS[world], stage, ...(kind === 'stage' ? NORMAL : POWER) };
}
export function validate(code) { return decode(code) !== null; }
// world 0-4, stage 1-5; power: the powered-up start (stage 1 only, null otherwise)
export function encode(world, stage = 1, power = false) {
  if (!(world >= 0 && world < 5 && stage >= 1 && stage <= 5)) throw new RangeError('bad value');
  if (power) return stage === 1 ? TABLE[25 + world] : null;
  return TABLE[world * 5 + stage - 1];
}
// The unused second decoder at $01:66CD (no caller; patches/pocket_debug_password.ips calls it when the table check
// fails): digit 1 = 0/1 invincible ($C2CC), digit 2 = world 0-4, digit 3 = 0/1 Start stops the clock instead of
// pausing ($C2CD), digit 4 = stage 0-4 (0 = stage 1). -> {invincible, world, clockStop, stage 1-5} | null
export function debugDecode(code) {
  const d = [...String(code).trim()].map(Number);
  if (d.length !== 4 || d.some(x => !(x >= 0 && x <= 9)) || d[0] > 1 || d[1] > 4 || d[2] > 1 || d[3] > 4) return null;
  return { invincible: !!d[0], world: d[1], worldName: WORLDS[d[1]], clockStop: !!d[2], stage: d[3] + 1 };
}
