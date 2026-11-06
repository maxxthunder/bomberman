// Super Bomberman: Panic Bomber W (Super Famicom, Japan, 1995) password table. No dependencies.
// 4 digits looked up in a table at file $4AB5 ($00:CAB5): one row of 8 per difficulty, 000d (round 1) then rounds
// 2-6, then 000d again; the Hardest row's last slots hold the character codes and the cheats (L and R held).
// Checked in Mesen 2.
export const LEVELS = ['Easiest', 'Easy', 'Normal', 'Hard', 'Hardest'];
export const ROWS = [['0001', '1706', '2158', '7839', '0285', '1694'], ['0002', '3248', '2516', '0927', '1439', '6218'],
  ['0003', '7154', '1386', '2473', '4890', '3105'], ['0004', '5746', '9510', '4715', '6532', '1974'],
  ['0005', '9650', '3825', '7431', '5792', '0819']];
export const CHARACTERS = { '4622': 'Baby Bombermen', '5656': 'Balloons', '1993': 'Funya', '8111': 'Takahashi Meijin' };
// with L and R held
export const CHEATS = { '4404': 'Four bombs needed to clear a line', '2200': 'Bombs explode at once', '0901': 'Stage select',
  '3445': 'Sound test', '5963': 'The ending' };

// -> {kind: 'round', level, round (1-6)} | {kind: 'character', name} | {kind: 'cheat', name} (needs L+R) | null
export function decode(code) {
  code = String(code).trim();
  for (let l = 0; l < 5; l++) { const r = ROWS[l].indexOf(code); if (r >= 0) return { kind: 'round', level: l, round: r + 1 }; }
  if (CHARACTERS[code]) return { kind: 'character', name: CHARACTERS[code] };
  if (CHEATS[code]) return { kind: 'cheat', name: CHEATS[code] };
  return null;
}
export function encode(level, round) { return ROWS[level][round - 1]; }
