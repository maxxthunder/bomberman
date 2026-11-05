// Check the built index.html: pull out its data script (codecs, code lists, game setup), run it, and assert
// known round-trips for each game plus that every password-shaped code in every docs/<g>_codes.json is accepted.
//   node tools/check_page.mjs
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import assert from 'node:assert/strict';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const src = html.match(/<script id="data">([\s\S]*?)<\/script>/)?.[1];
assert.ok(src, 'no <script id="data"> in index.html');
const { SB1, SB2, SB3, SB4, SB5, MEGA, PCE90, PCE93, PCE94, GB1, GB2, GB3, NES1, NES2, POCKET, MAX, QUEST, CODES, GAMES, defaultVer, logoFor, patchLinks, PATCH_ROM, LOGOS } =
  new Function(src + '\nreturn { SB1, SB2, SB3, SB4, SB5, MEGA, PCE90, PCE93, PCE94, GB1, GB2, GB3, NES1, NES2, POCKET, MAX, QUEST, CODES, GAMES, defaultVer, logoFor, patchLinks, PATCH_ROM, LOGOS };')();

let n = 0;
const ok = (cond, msg) => { assert.ok(cond, msg); n++; };
const eq = (a, b, msg) => { assert.deepEqual(a, b, msg); n++; };

// SB1
eq([SB1.decode('7632').world, SB1.decode('7632').stage], [6, 7], 'SB1 7632 is 6-7');
for (const c of SB1.codesFor(6, 7)) eq(SB1.decode(c).index, 46, 'SB1 codesFor(6,7) round-trips ' + c);
ok(SB1.decode('8000') === null, 'SB1 rejects 8000');

// SB2
const s2 = SB2.decode('1111');
ok(s2 && s2.world === 1 && s2.fullPower, 'SB2 1111 is full power stage 1');
eq(SB2.encode({ world: 1, fullPower: true }), '1111', 'SB2 encode full power 1');
ok(SB2.decode('0000') === null, 'SB2 rejects 0000');

// SB3
eq(SB3.decode('6514').kind, 'special', 'SB3 6514 is special');
ok(/hard mode/i.test(SB3.decode('6514').effect), 'SB3 6514 is hard mode');
eq(SB3.decode('5358').name, '1-1', 'SB3 5358 is 1-1');
eq(SB3.encode(0x0B), '5358', 'SB3 encode 1-1');

// SB4: two codes from its JSON
for (const code of ['7352', '1574']) {
  const e = CODES.sb4.find(x => x.code === code);
  ok(e, 'SB4 ' + code + ' in the JSON');
  const d = SB4.decode(code);
  ok(d && e.effect.includes(d.stage), `SB4 ${code} is ${d && d.stage} (${e.effect})`);
  eq(SB4.encode(d.stage), code, 'SB4 re-encodes ' + code);
}

// SB5
const f = SB5.decode('D24GJN');
ok(f, 'SB5 D24GJN decodes');
eq(SB5.encode(f), 'D24GJN', 'SB5 D24GJN re-encodes');
ok(SB5.decode('UO4GJL') === null, 'SB5 UO4GJL is rejected (no O on the grid)');
ok(SB5.option('0719', 'retail') === null && SB5.option('0719', 'caravan'), 'SB5 0719 is Caravan only');

// Mega
eq(MEGA.decode('0515').world, 6, 'Mega 0515 is the final area');
const m = MEGA.decode('2200');
ok(m && m.world === 1 && m.cleared.length === 0, 'Mega 2200 is area 1 stage 1');
eq(MEGA.encode(1, []), '2200', 'Mega encode 1-1');

// Bomberman (PC Engine, 1990)
const game = id => GAMES.find(x => x.id === id);
const p0 = PCE90.decode('MUVWLNPC');
ok(p0 && p0.round === 1 && p0.stage === 1, 'pce90 MUVWLNPC is round 1 stage 1');
ok(PCE90.gameCodes(1, 1).includes('MUVWLNPC'), 'pce90 gameCodes(1,1) includes MUVWLNPC');
for (const c of PCE90.gameCodes(3, 5, 4, 2, 1)) eq(PCE90.decode(c).stage, 5, 'pce90 gameCodes round-trip ' + c);
ok(PCE90.decode('BOMSOUND') === null && game('pce90').check('BOMSOUND').type === 'special', 'pce90 BOMSOUND is rejected by the decoder and shown as special');

// Bomberman '93
const p3 = PCE93.decode('CBCCBBDB', 'us');
ok(p3 && p3.world === 1 && p3.stage === 1, "'93 CBCCBBDB is 1-1 (US)");
eq(PCE93.decode('PMPHTZNF', 'us'), { world: 7, stage: 8, bombs: 10, fire: 5, cleared: 63, speed: 3 }, "'93 PMPHTZNF is 7-8 maxed");
eq(PCE93.encode(PCE93.decode('PMPHTZNF', 'us'), 'us'), 'PMPHTZNF', "'93 PMPHTZNF re-encodes");
ok(PCE93.validate(PCE93.convert('CBCCBBDB', 'us', 'jp'), 'jp'), "'93 US code converts to a valid JP code");
eq(game('pce93').check('BABBAACA').ver, 'jp', "'93 checker finds the JP version for BABBAACA");

// Bomberman '94: the same system as Mega Bomberman
eq(PCE94.decode('0515').area, 6, "'94 0515 is the final area");
eq(game('pce94').check('0515').title, 'Final area', "'94 checker: 0515 final area");
eq(PCE94.validCodes(), MEGA.validCodes(), "'94 and Mega accept the same codes");

// NES
const n1 = NES1.encode({ stage: 12, bombs: 4, fire: 3, detonator: 1 });
eq(game('nes1').check(n1).title, 'Stage 12', 'nes1 encode/check round-trip');
eq(NES1.decode(n1).detonator, 1, 'nes1 keeps the detonator');
ok(!game('nes1').check('A'.repeat(20)), 'nes1 rejects AAAA...');
const n2 = NES2.encode({ area: 3, stage: 5, bombs: 2, fire: 4 }, 'us');
eq(game('nes2').check(n2, 'us').title, 'Stage 3-5', 'nes2 US round-trip');
ok(game('nes2').check(NES2.convert(n2, 'us', 'jp'), 'jp'), 'nes2 converts to a JP code');
eq(game('nes2').check('K3456712', 'us').type, 'special', 'nes2 K3456712 is the sound test');

// Game Boy
eq(game('gb1').check('4696').title, 'Stage 1-1', 'gb1 4696 is 1-1');
eq(game('gb1').check(GB1.encode(2, 4, 'wario', 'wario')).title, 'Stage 2-4 (boss) as Wario', 'gb1 Wario codes');
ok(!game('gb1').check(GB1.encode(1, 1, 'wario', 'wario'), 'jp'), 'gb1 Wario codes are Wario Blast only');
eq(game('gb2').check('5472').title, 'World 8', 'gb2 5472 is world 8');
ok(!game('gb2').check('7824', 'us'), 'gb2 7824 (unused table) is rejected');
eq(game('gb3').check('0986400').title, 'Wood stage 1', 'gb3 0986400 is Wood 1');
eq(GB3.decode(GB3.encode(4, 3, [], 0b101)).shop, 0b101, 'gb3 encode keeps the shop');
ok(GB3.encode(0, 1, [], 0b1000) === null, 'gb3 F costs more than Wood pays');

// Pocket Bomberman: a list of 32
eq(game('pocket').check('7693').title, 'Forest area 1', 'pocket 7693 is Forest 1');
eq(game('pocket').check(POCKET.encode(2, 1, true)).title, 'Wind area 1, fully powered up', 'pocket powered-up Wind start');
eq(game('pocket').check('0278').type, 'special', 'pocket 0278 is the ending');
ok(!game('pocket').check('0000'), 'pocket rejects 0000');

// Bomberman Max: GameShark codes for the Charabom roster
eq(game('max').check('8001F0A1').title, 'Own Heat Rock', 'max 8001F0A1 owns Heat Rock');
eq(game('max').check(MAX.encode({ level: { 3: 50 } }, 'blue')[0]).title.endsWith('level 50'), true, 'max level code round-trip');
ok(!game('max').check('8001F0A2'), 'max rejects a non-roster address');

// Bomberman Quest: GameShark codes for the save block
eq(game('quest').check('01102BCF', 'us').title, 'Own the Normal Bomb', 'quest US Normal Bomb code');
  eq(game('quest').check('01102ACF', 'jp').title, 'Own the Normal Bomb', 'quest Japanese Normal Bomb code (one byte lower)');
  eq(game('quest').check(QUEST.encode({ item: { 1: 9 } }, 'us')[0], 'us').title, 'Rubber x 9', 'quest counted item');
  ok(!game('quest').check('01202BCF', 'us'), 'quest rejects a value that is not an owned item');

// Every password-shaped code in every code list is accepted by the page's checker (which calls the codec), in each
// version it is listed for; the ones the list itself marks "Rejected" must be rejected.
for (const g of GAMES) {
  let k = 0, r = 0;
  for (const e of CODES[g.id]) {
    if (!g.shape.test(e.code) || e.section === 'patch' || e.section === 'cheat') continue;   // patch-only codes need patches/*.ips; Game Genie codes can look like passwords
    if (/^Rejected/i.test(e.effect)) { ok(!g.check(e.code) || g.check(e.code).type === 'special', `${g.id}: ${e.code} should be rejected`); r++; continue; }
    for (const v of e.versions.length ? e.versions : ['']) {
      const res = g.check(e.code, v.toLowerCase());
      ok(res && !res.bad, `${g.id}: ${e.code} (${e.effect}) is rejected by the codec in ${v || 'any version'}`);
    }
    k++;
  }
  console.log(`${g.id}: ${k} passwords in the code list, all accepted${r ? `; ${r} listed as rejected, rejected` : ''}`);
}
eq(GAMES.map(g => g.id), ['sb1', 'sb2', 'sb3', 'sb4', 'sb5', 'mega', 'pce90', 'pce93', 'pce94', 'nes1', 'nes2', 'gb1', 'gb2', 'gb3', 'pocket', 'max', 'quest'], 'every built game has a setup');

// A game with no codec: listed, codes only, no generator
ok(!GAMES.find(g => g.id === 'mega8') && CODES.mega.some(e => e.section === 'demo8'), 'the 8-player demo sits inside Mega Bomberman');

ok(!GAMES.find(g => g.id === 'pceub') && CODES.pce90.some(e => e.section === 'ub'), 'Users Battle sits inside the 1990 Bomberman');

// Version chips start on the main release
const MAIN = { sb1: 'US', sb2: 'us', sb3: 'eu', sb4: 'JP', sb5: 'retail', mega: 'US', pce90: 'US', pce93: 'US', pce94: 'retail', nes1: 'US', nes2: 'US', gb1: 'wario', gb2: 'us', gb3: 'jp', pocket: 'us', quest: 'us' };
for (const [id, v] of Object.entries(MAIN)) eq(defaultVer(GAMES.find(g => g.id === id)), v, `${id} starts on ${v}`);
eq(logoFor(GAMES.find(g => g.id === 'pce93'), 'SP'), 'pce93_sp', "'93 Special Version chip shows its logo");
eq(logoFor(GAMES.find(g => g.id === 'sb4'), 'EN'), 'sb4_jp', 'a game without per-version logos keeps its default');

// Patch links: every link points at a file in patches/, every patch file is linked from some code and has a ROM name
const linked = new Set();
for (const g of GAMES) for (const e of CODES[g.id]) for (const f of patchLinks(e.game || g.id, [e.code, e.effect, e.note].join(' '))) {
  ok(existsSync(new URL('../patches/' + f, import.meta.url)), `${g.id}: patch link ${f} exists`);
  linked.add(f);
}
for (const f of readdirSync(new URL('../patches/', import.meta.url)).filter(f => f.endsWith('.ips'))) {
  ok(linked.has(f), `patches/${f} is linked from a code`);
  ok(PATCH_ROM[f], `patches/${f} names its ROM`);
}
// img fields name real screenshots
for (const g of GAMES) for (const e of CODES[g.id]) if (e.img) ok(existsSync(new URL(`../docs/img/${g.id}/${e.img}`, import.meta.url)), `${g.id}: ${e.img} exists`);
// generator item icons: every ico("<g>", "<name>") and SB5_ICONS entry names a docs/img/items/<g>/<name>.png
const sb5Icons = JSON.parse(html.match(/const SB5_ICONS = (\[[^\]]*\])/)[1]);
eq(sb5Icons.length, SB5.ITEMS.length, 'one SB5 icon per item');
const icons = [...html.matchAll(/ico\("(\w+)", "(\w+)"\)/g)].map(m => m[1] + '/' + m[2]).concat(sb5Icons.map(x => 'sb5/' + x));
ok(icons.length > 12, 'the generators use item icons');
for (const f of icons) ok(existsSync(new URL(`../docs/img/items/${f}.png`, import.meta.url)), `icon docs/img/items/${f}.png exists`);
console.log(`ok: ${n} checks passed`);
