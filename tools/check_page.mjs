// Check the built index.html: pull out its data script (codecs, code lists, game setup), run it, and assert
// known round-trips for each game plus that every password-shaped code in every docs/<g>_codes.json is accepted.
//   node tools/check_page.mjs
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const src = html.match(/<script id="data">([\s\S]*?)<\/script>/)?.[1];
assert.ok(src, 'no <script id="data"> in index.html');
const { SB1, SB2, SB3, SB4, SB5, MEGA, PCE90, PCE93, PCE94, CODES, GAMES } =
  new Function(src + '\nreturn { SB1, SB2, SB3, SB4, SB5, MEGA, PCE90, PCE93, PCE94, CODES, GAMES };')();

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

// SB4 (if the build has it): two codes from its JSON
if (SB4) {
  for (const code of ['7352', '1574']) {
    const e = CODES.sb4.find(x => x.code === code);
    ok(e, 'SB4 ' + code + ' in the JSON');
    const d = SB4.decode(code);
    ok(d && e.effect.includes(d.stage), `SB4 ${code} is ${d && d.stage} (${e.effect})`);
    eq(SB4.encode(d.stage), code, 'SB4 re-encodes ' + code);
  }
} else console.log('SB4 not in the build: skipped');

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

// Every password-shaped code in every code list is accepted by the page's checker (which calls the codec), in each
// version it is listed for; the ones the list itself marks "Rejected" must be rejected.
for (const g of GAMES) {
  let k = 0, r = 0;
  for (const e of CODES[g.id]) {
    if (!g.shape.test(e.code) || e.section === 'patch') continue;   // patch-only codes need patches/*.ips
    if (/^Rejected/i.test(e.effect)) { ok(!g.check(e.code) || g.check(e.code).type === 'special', `${g.id}: ${e.code} should be rejected`); r++; continue; }
    for (const v of e.versions.length ? e.versions : ['']) {
      const res = g.check(e.code, v.toLowerCase());
      ok(res && !res.bad, `${g.id}: ${e.code} (${e.effect}) is rejected by the codec in ${v || 'any version'}`);
    }
    k++;
  }
  console.log(`${g.id}: ${k} passwords in the code list, all accepted${r ? `; ${r} listed as rejected, rejected` : ''}`);
}
eq(GAMES.map(g => g.id), ['sb1', 'sb2', 'sb3', SB4 && 'sb4', 'sb5', 'mega', 'pce90', 'pce93', 'pce94'].filter(Boolean), 'every built game has a setup');
console.log(`ok: ${n} checks passed`);
