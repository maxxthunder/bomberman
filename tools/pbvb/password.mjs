// Panic Bomber (Virtual Boy, USA, 1995) password table. No dependencies.
// The codes are 4 digits looked up in a table at ROM $27DFE ($0702_7DFE) by $0701_FFDC: one row of 8 per level, then 6
// more codes, then 10 that need buttons held while A is pressed. Each row is d000 (stage 1), the codes for stages 2-4, then d000
// again in the four slots after them, so d000 always means stage 1 of level d. Checked in BizHawk (Virtual Boyee).
export const LEVELS = ['Very Easy', 'Easy', 'Normal', 'Hard'];
export const STAGES = ['The Scary Ruins', 'The Sinister Forest', 'Desert of Desolation', 'Doom Castle'];
export const ROWS = [['1000', '4390', '3281', '5607'], ['2000', '6835', '9081', '2473'], ['3000', '2695', '1038', '6934'],
  ['4000', '8647', '0538', '9316']];
// the row after the levels: 1298 starts the game against Zach the Were-Bomberman; 9782 swaps the block pieces
export const ZACH = '1298';
export const NOHOLD = { '9782': 'Other block pieces in every game' };
// with L and R held ($0702_00D0 checks the pad at $0500_2510); the handlers start at $0702_01EC
export const CHEATS = { '0130': 'Auto play', '1001': 'Sound test', '0720': 'Stage select', '0716': 'The ending',
  '4476': 'Your pad moves both sides', '0911': 'A RESULT screen after every round', '0704': 'Skull blocks in every game',
  '0612': 'Slowest animation in every game' };
// with L, R, Up on the right pad and Left on the left pad held: the DEBUG MENU, then a game with its settings
export const DEBUG = { '0825': 'The DEBUG MENU', '0513': 'The DEBUG MENU, then the CPU plays both sides' };

// -> {kind: 'stage', level, stage} | {kind: 'zach'} | {kind: 'extra', name} | {kind: 'cheat', name} (needs L+R) |
//    {kind: 'debug', name} (needs four buttons) | null
export function decode(code) {
  code = String(code).trim();
  for (let l = 0; l < 4; l++) { const s = ROWS[l].indexOf(code); if (s >= 0) return { kind: 'stage', level: l, stage: s }; }
  if (code === ZACH) return { kind: 'zach' };
  if (NOHOLD[code]) return { kind: 'extra', name: NOHOLD[code] };
  if (CHEATS[code]) return { kind: 'cheat', name: CHEATS[code] };
  if (DEBUG[code]) return { kind: 'debug', name: DEBUG[code] };
  return null;
}
