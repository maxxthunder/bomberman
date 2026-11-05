// Bomberman Max (Game Boy Color): there is no password. The game saves to battery RAM, and the Charabom roster is a
// table in it, so the "codes" here are GameShark codes for the cart RAM (type $80, bank 0): one per Charabom to own.
// Layout (the same in all five versions): $A110 + 8 * id: [owned, id, level, attack, defense, speed, 0, 0], read by
// $02:65AD ("owned?") and written by $02:653E (a rescue); the game reads it in place, so a code takes effect at once
// and stays after a save. Verified in Mesen 2's cheat engine: every id 0-29 shows on the Charabom Select screen.

export const VERSIONS = {
  blue: 'Blue Champion (USA)', red: 'Red Challenger (USA)',
  hikari: 'Hikari no Yuusha (Japan)', yami: 'Yami no Senshi (Japan)', ain: 'Ain Version (Japan)',
};

// id = table index; icon = docs/img/items/max/<icon>.png. home: where the game gives it ('blue' = Blue / Hikari / Ain stages, 'red' = Red / Yami / Ain,
// 'combo' = made by combining two, 'legend' = the two legendary ones, 'unused' = never given). lv = starting level.
export const CHARABOMS = [
  ['Draco', 'ドラコ', 'red', 3], ['Shell', 'シェル', 'blue', 4], ['Pommy', 'ポミュ', 'blue', 3],
  ['Elephan', 'エレファン', 'red', 4], ['Seadran', 'シードラン', 'blue', 8], ['Marine Eel', 'マリンイール', 'red', 8],
  ['Knuckle Pommy', 'ナックルポミュ', 'red', 12], ['Panther Fang', 'パンサーファング', 'blue', 12],
  ['Twin Dragon', 'ツインドラゴン', 'red', 16], ['Sea Balloon', 'シーバルーン', 'blue', 16],
  ['Beast Pommy', 'アニマルポミュ', 'blue', 20], ['Big Ox', 'ビッグオックス', 'red', 20],
  ['Puteladon', 'プテラドン', 'blue', 24], ['Sharkin', 'シャークン', 'red', 24],
  ['Hammer Pommy', 'ハンマーポミュ', 'red', 28], ['Unicornos', 'ユニコルノス', 'blue', 28],
  ['Iron Dragon', 'アイアンドラゴン', 'red', 32], ['Iron Squid', 'クラーケン', 'blue', 32],
  ['Animal Pommy', 'ビーストポミュ', 'blue', 36], ['Mecha Kong', 'メカコング', 'red', 36],
  ['Aqua Dragon', 'アクアドラゴン', 'combo', 5], ['Pommy Dragon', 'ポミュドラゴン', 'combo', 5],
  ['Thunder Kong', 'サンダーコング', 'combo', 5], ['Thunder Shark', 'サンダーシャーク', 'combo', 5],
  ['Rock Snakey', 'ロックスネーキー', 'combo', 5], ['Fire Force', 'ファイアーフォース', 'combo', 5],
  ['Shardra', 'シャードラ', 'legend', 40], ['Ox Battra', 'オックスバトラー', 'legend', 40],
  ['Heat Rock', 'ヒートロック', 'unused', 50], ['Oct Kong', 'タッコング', 'unused', 50],
].map(([us, jp, home, lv], id) => ({ id, us, jp, home, lv, icon: us.toLowerCase().replace(/ /g, '_') }));

// the other codes (button code on the title menu; cheats checked in Mesen)
export const SOUND_TEST = 'Right, Left, Right, Right, Left, Left, Right, Left, Right, Left, Left, Right';
export const CHEATS = { invincible: 'C32-EBA-C41', lives: '0103F7C2' };

const hex = (n, w = 2) => n.toString(16).toUpperCase().padStart(w, '0');
const JP = new Set(['hikari', 'yami', 'ain']);

export function name(id, ver) { const c = CHARABOMS[id]; return c && (JP.has(ver) ? c.jp : c.us); }

// state: {own: [ids], level: {id: 1-99}} -> GameShark codes. Owning writes 01 to the entry's first byte; a level
// writes the entry's third byte (the card's Lv; the other stats stay as they are).
export function encode(state, ver) {
  const out = [];
  for (const id of state.own || []) {
    if (!CHARABOMS[id]) return null;
    const a = 0xA110 + 8 * id;
    out.push('8001' + hex(a & 0xFF) + hex(a >> 8));
  }
  for (const [k, lv] of Object.entries(state.level || {})) {
    const id = +k, a = 0xA112 + 8 * id;
    if (!CHARABOMS[id] || !(lv >= 1 && lv <= 99)) return null;
    out.push('80' + hex(lv) + hex(a & 0xFF) + hex(a >> 8));
  }
  return out;
}

// one GameShark code -> {id, name, field: 'owned' | 'level', value} for a Charabom-table code, else null
export function decode(code, ver) {
  const m = /^80([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})$/.exec(String(code).toUpperCase().replace(/[\s-]/g, ''));
  if (!m) return null;
  const v = parseInt(m[1], 16), a = parseInt(m[3] + m[2], 16) - 0xA110, id = a >> 3, f = a & 7;
  if (a < 0 || id >= CHARABOMS.length || (f !== 0 && f !== 2)) return null;
  return { id, name: name(id, ver), field: f ? 'level' : 'owned', value: v };
}

export function validate(code, ver) { return decode(code, ver) !== null; }
