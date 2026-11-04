// Super Bomberman 3 (SNES) password codec, no dependencies. Mirrors the game's decoder ($C2:67DB) and
// encoder ($C2:67FD); same in the EU, JP and EU beta ROMs. See docs/sb3.md.
//   decode("5358") -> {kind:"stage", stage:0x0B, name:"1-1", area:1} | {kind:"special", effect} | null
//   encode(0x0B, spare=0) -> "5358"   (spare 0-3 fills the two bits the decoder ignores)
//   validate(code) -> true/false

// $C2:6984: stage id ($0346) -> area ($0349). Anything else is rejected.
export const STAGES = [[0x0B,1],[0x0C,1],[0x0D,1],[0x0F,1],[0x11,1],[0x12,2],[0x13,2],[0x15,2],[0x18,2],[0x1A,2],
  [0x1B,3],[0x1D,3],[0x1F,3],[0x22,3],[0x24,3],[0x25,4],[0x27,4],[0x2A,4],[0x2D,4],[0x30,4],
  [0x31,5],[0x34,5],[0x37,5],[0x3A,5],[0x3E,5],[0x3F,6]];
const AREA = new Map(STAGES);
export const NAMES = new Map();
for (let a = 1; a <= 5; a++) STAGES.filter(s => s[1] === a).forEach(([s], i) => NAMES.set(s, i < 4 ? `${a}-${i + 1}` : `${a}-boss`));
NAMES.set(0x3F, "6-1");

// $C2:6A08: special codes, checked before the normal decode.
export const SPECIAL = {
  "4622": "Battle mode, arena layout 1 of 0-3 for every stage ($542E=1)",
  "1616": "Battle mode, arena layout 2 of 0-3 ($542E=2)",
  "3194": "Battle mode, arena layout 3 of 0-3 ($542E=3)",
  "1511": "Battle mode, COM level 4 ($6C6F=4)",
  "5656": "Battle mode; sets $4C0C=$7F, which no code uses",
  "0704": "1-1 with full equipment",
  "3200": "2-1 with full equipment",
  "2711": "3-1 with full equipment",
  "3870": "4-1 with full equipment",
  "4501": "5-1 with full equipment",
  "0606": "6-1 with full equipment",
  "3104": "Final boss (stage $46) with full equipment",
  "6514": "Hard mode: new game from the intro, every enemy takes one more hit",
  "0803": "Ending",
};

// $C2:68B6: XOR $0DDE, swap bits 0<->5 and 9<->12. Its own inverse.
function swap(v) {
  v ^= 0x0DDE;
  for (const [a, b] of [[0, 5], [9, 12]]) if (((v >> a) & 1) !== ((v >> b) & 1)) v ^= (1 << a) | (1 << b);
  return v;
}
// $C2:693B
const check = lo => ((((lo & 0x7F) >> 4) + lo) & 0x0F);

export function decode(code) {
  code = String(code).trim();
  if (!/^\d{4}$/.test(code)) return null;
  if (SPECIAL[code]) return { kind: "special", effect: SPECIAL[code] };
  const v = swap((Number(code) - 0x0710) & 0xFFFF);
  if (v >= 0x2000 || check(v & 0xFF) !== ((v >> 9) & 0x0F)) return null;
  const stage = (v & 0x7F) + 0x0B;
  if (!AREA.has(stage)) return null;
  return { kind: "stage", stage, name: NAMES.get(stage), area: AREA.get(stage) };
}

export function encode(stage, spare = 0) {
  if (stage >= 0x40) stage = 0x3F;  // the game clamps this too ($C2:68FA)
  let v = ((stage - 0x0B) & 0x7F) | ((spare & 1) << 7) | (((spare >> 1) & 1) << 8);
  v |= check(v & 0xFF) << 9;
  return String(swap(v) + 0x0710).padStart(4, "0");
}

export const validate = code => decode(code) !== null;

export function allCodes() {
  const out = [];
  for (let n = 0; n < 10000; n++) { const c = String(n).padStart(4, "0"), d = decode(c); if (d) out.push([c, d]); }
  return out;
}
