// Super Bomberman 5 (SNES, Japan) passwords. No dependencies.
// Config Battle character password: 6 symbols = 30 bits. Game code: decoder $C5:6530, encoder $C5:6545
// (retail; the Caravan build uses the same routine). Option passwords: 4-digit table at $C5:6875.

/** Symbol values 0-31. The entry grid shows A-Y first, then 1-9 and 0; there is no I, O, S or Z. */
export const ALPHABET = "0123456789ABCDEFGHJKLMNPQRTUVWXY";
export const BODIES = ["Bomberman", "Bomber Woof", "Dave Bomber", "Gary Bomber", "Pirate Bomber", "Muscle Bomber",
  "Iron Mask Bomber", "Baron Bombano", "Plunder Bomber", "Subordinate Bomber"];
export const COLORS = ["white", "black", "red", "blue", "green", "yellow", "burnt (unused)", "boss (unused)"];
export const ITEMS = ["Remote control", "Pierce bomb", "Land mine", "Homing bomb", "Bomb pass", "Soft-block pass", "Power glove", "Kick", "Punch"];

export const OPTION_CODES = {
  "4622": { versions: ["retail", "caravan"], effect: "Battle: start positions moved in towards the centre" },
  "0413": { versions: ["retail", "caravan"], effect: "Battle: alternate hard-block and item layouts" },
  "0926": { versions: ["retail", "caravan"], effect: "Battle: start positions moved in, less open space" },
  "1103": { versions: ["retail", "caravan"], effect: "Battle: adds SUPER to COM LEVEL (kept in the save)" },
  "0110": { versions: ["retail", "caravan"], effect: "Battle: every soft block holds a power-up" },
  "2657": { versions: ["retail", "caravan"], effect: "Normal: start with 8 bombs, 8 fire and max speed" },
  "5656": { versions: ["retail", "caravan"], effect: "Normal: 9 lives and an 8:00 timer" },
  "3879": { versions: ["retail", "caravan"], effect: "Boss rush: the Normal-mode bosses back to back" },
  "1999": { versions: ["retail", "caravan"], effect: "Watch the good ending" },
  "0803": { versions: ["retail", "caravan"], effect: "Watch the bad ending" },
  "0719": { versions: ["caravan"], effect: "Boss rush, starting fully powered" },
  "4737": { versions: ["caravan"], effect: "Battle: every player starts fully powered" },
};

/** Effect of a 4-digit option password in a version ("retail" or "caravan"), or null if rejected. */
export function option(code, version = "retail") {
  const c = OPTION_CODES[code];
  return c && c.versions.includes(version) ? c.effect : null;
}

// $C5:6759: sum of every nibble of the 26 data bits, mod 16
function checksum(b) {
  let s = 0;
  for (const x of b) s = (s + x + (x >> 4)) & 15;
  return s;
}

/**
 * Fields as the game stores them: body 0-15 ($62DE; 0-8 normal, 9 Subordinate Bomber, 10-15 invalid),
 * color 0-7 ($62DF; 0-5 normal), bomb 0-7 / fire 0-15 / speed 0-7 ($62E6-$62E8; shown as +1 / +2 / +1),
 * items: 9-bit mask, bit n = ITEMS[n] ($62E9-$62F1).
 */
export function encode({ body = 0, color = 0, bomb = 0, fire = 0, speed = 0, items = 0 }) {
  const v = (body & 15) | (color & 7) << 4 | (bomb & 7) << 7 | (fire & 15) << 10 | (speed & 7) << 14 | (items & 0x1FF) << 17;
  const b = [v & 255, v >>> 8 & 255, v >>> 16 & 255, v >>> 24 & 255];
  b[3] |= checksum(b) << 2;
  const w = b.reduce((a, x, i) => a + (x ^ 0xCB) * 2 ** (8 * i), 0);
  let s = "";
  for (let i = 0; i < 6; i++) s += ALPHABET[Math.floor(w / 2 ** (5 * i)) & 31];
  return s;
}

/** Decoded fields, or null if the game rejects the code (wrong length, bad symbol, bad checksum). */
export function decode(code) {
  code = String(code).toUpperCase();
  if (code.length !== 6) return null;
  let w = 0;
  for (let i = 0; i < 6; i++) {
    const n = ALPHABET.indexOf(code[i]);
    if (n < 0) return null;
    w += n * 2 ** (5 * i);
  }
  const b = [0, 1, 2, 3].map(i => (Math.floor(w / 2 ** (8 * i)) & 255) ^ 0xCB);
  const ck = b[3] >> 2 & 15;
  b[3] &= 3;
  if (checksum(b) !== ck) return null;
  const v = b[0] | b[1] << 8 | b[2] << 16 | b[3] << 24;
  return { body: v & 15, color: v >> 4 & 7, bomb: v >> 7 & 7, fire: v >> 10 & 15, speed: v >> 14 & 7, items: v >>> 17 & 0x1FF };
}

/** true if the game accepts the code. */
export function validate(code) {
  return decode(code) !== null;
}

/** Notes on fields the game accepts but the editor never makes (what each one does on screen). */
export function warnings(f) {
  const w = [];
  if (f.body === 9) w.push("Subordinate Bomber: no portrait (draws as a red Bomberman), wrong icon in matches; reported to freeze the game if he wins a single match");
  if (f.body > 9) w.push("body " + f.body + " is out of range");
  if (f.color === 6) w.push("color 6: the burnt palette");
  if (f.color === 7) w.push("color 7: boss palette; the color name in the editor draws as junk text");
  if (f.fire > 6) w.push("fire above 8 draws as junk digits in the editor");
  return w;
}
