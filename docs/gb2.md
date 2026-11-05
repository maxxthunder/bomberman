# Bomberman GB 2 (Japan, 1995) / Bomberman GB (USA, Europe): passwords and secrets

The US/EU "Bomberman GB" is this game, not JP Bomberman GB (that one became Wario Blast, [gb1.md](gb1.md)); see the
dump table there for the comparison. Everything here comes from disassembling the ROMs (`tools/sm83.py`, listings
in `disasm/gb2/`) and checking in Mesen 2 (`tools/gb2/run.sh`, helpers in `tools/gb2/lib.lua`). Addresses are
`bank:address`, US unless JP is named.

Prior art: the GameFAQs "Bomberman GB" codes page and the TCRF "Bomberman GB" article (both in `res/`; both mean
this game: TCRF gives "also known as Bomberman GB 2 (JP)", GameFAQs the 1998 US release). Marks: ★ **New**,
**Fixed**, **Known**. Every code either page lists works as described.

| Dump | Header title | MD5 | vs US |
|---|---|---|---|
| Bomberman GB (USA, Europe) (SGB Enhanced) | `BOMBER MAN GB` | `7e4c9c3620bea7b633394beb67e9680b` | |
| Bomberman GB 2 (Japan) (SGB Enhanced) | `BOMBER MAN GB 2` | `4ab78239e79ba059d0d7aa7a629a9474` | 28,666 bytes differ. Banks 8, 10, 11 are identical; bank 0 code is the same with shifts (the password check is `$00:35F9` in JP, `$00:35CC` in US); banks 5 and 15 hold the text and the table |

Both are 256 KB MBC1, SGB flag `$03`, licensee `18`.

## RAM that matters

| Address | Meaning | Evidence |
|---|---|---|
| `$C100` | world << 4 \| stage (stage 0-4, 7 = the boss) | `$00:250B`, `$00:25B3` |
| `$C103` / `$C104` / `$C105` | stage-end flag / player-dead flag / end countdown | `$00:24E3`, `$01:531E` |
| `$C106` | lives (3 per world start) | `$00:2555`, `$00:2577` |
| `$C11A` | 1 = battle (code 5656) | `$00:3682` |
| `$C125` / `$C126` | power-up bits (per world: `$00,$04,$0C,$4C,$5C,$7C,$7C,$7F`; 4622: `$7F`) | read back after each code |
| `$C1BC` / `$C1BD` / `$C1BE-$C1C1` | password cursor / found value / the 4 digits | `$00:35CC` |
| `$C800-$CB00` | the four player objects (one page each); player 1 X at `$C802` | position search |
| `$FFA0` / `$FFA1` | pad held / newly pressed | `$00:0309`, `$00:3583` |

## The password

Code: `$00:3578` (entry loop), `$00:35CC` (check; JP `$00:35F9`), `$00:3639` (dispatch), `$00:3744` (code for the
current world, shown on the CONTINUE screen by `$00:1FE5`). Table: bank `$0F`, `$7F72` US / `$54C1` JP.

- 4 digits; 12 records of 4 ASCII digits + 1 value are compared; the 12th is `$FF` filler. **No checksum**: 11 codes,
  the same in both versions:

| Code | Value | Effect |
|---|---|---|
| 8566, 9634, 1637, 0320, 6524, 3260, 4783, 5472 | `$80-$87` | start at world 1-8 (`$C100` = world << 4) |
| 2145 | `$88` | sound test |
| 5656 | `$8A` | battle (`$C11A` = 1) |
| 4622 | `$8D` | world 1 with every power-up (`$C125` = `$C126` = `$7F`, `$C11E` = 1) |

- ★ **New: dispatcher cases no code uses.** Values `$00-$7F` would set `$C100` to the value directly (any world and
  stage), `$8B` opens the sound test with `$C11B` = 1, `$8C` jumps to `$00:34E9` (the screen after the staff roll).
- **Fixed: 7824.** TCRF: "inserted among the passwords of the US version is 7824, which only returns invalid". The
  US ROM has a second, older copy of the table at `$0F:5447` that nothing references; it has a 12th record **7824 =
  `$89`**, and `$89` in the dispatcher jumps to `$00:1E3A`, the **ending** (the same routine the game calls after
  world 8, `$00:260E`). The live table lacks it, so it is rejected (typed: the reject exit ran). JP has no copy.

**Codec API** (`tools/gb2/password.mjs`): `decode(code, version = 'us' | 'jp')` returns
`{value, kind: 'world' | 'soundtest' | 'battle' | 'powerup', world?, stage?}` or `null`; `describe(value)` for any
dispatcher value (also `'stage'`, `'ending'`, `'soundtest2'`, `'closing'`, `'title'`); `validate`; `encode(world)`;
`allCodes(version)`; `TABLES`; `UNUSED` (`{us: {'7824': 0x89}}`).

### Verification

- **Fuzz**: all 10,000 codes through the game's own check (`tools/gb2/fuzz.py`, savestate at the check's entry, result
  at its exits): US 11 accepted, JP 11, **0 mismatches**.
- **Typed with the pad** (`tools/gb2/test_codes.py`): all 11 codes plus `0000` and `7824`, US and JP; `$C1BD`,
  `$C100`, `$C11A`, `$C125/$C126` read back as predicted. Entering: Up/Down step the digit (wraps), Left/Right move
  the cursor, A or Start checks, B leaves.

![8566, 2145, 5656, 4622, 7824 (US)](img/gb2/codes_us.png)

## Secrets

- **2145 sound test** (Known: GameFAQs, TCRF). MUSIC / EFFECT / EXIT; Left/Right change the number, A plays.
- **5656 battle** (Known). The plain-GB title has only STORY / LESSON / PASSWORD; this code is the way into battle.
  The battle setup shows 1P-4P; the game asks the SGB for 4 players at boot (MLT_REQ `89 03`), so with a multitap
  four people can play (SGB-only content; the multitap itself couldn't be emulated).
- **4622 power-ups**, **8566-5472 world codes** (Known, GameFAQs "Level 1-8", "All Power-Ups").

### Cheats (★ New)

Verified with `tools/gb2/test_cheats.lua` (world 1 MODE-A, random-input bot, 6,000 frames), both versions share
the addresses.

| Code | Effect | Verified |
|---|---|---|
| `C92-96A-6EB` + `C92-ACA-6EB` + `C93-03A-6EB` (Game Genie) | invincible: RET over the three death handlers in the hit table `$01:4913` | 0 deaths; 5 and a game over without |
| `010306C1` | infinite lives (`$C106` = 3) | 10 deaths, no game over |
| `010103C1` + `010004C1` | every stage ends cleared | `$C100` 00, 01, 02, 03, 04, 07 (boss), 10 in 5,000 frames |

Patch: `patches/gb2_invincible.ips` (`$5296`, `$52AC`, `$5303` = `$C9`, both versions).

## Hidden-content sweep

Coverage (`tools/gb2/cov.sh`): intro and title, LESSON, the sound test with every number, battle, 4622, MODE-A and
MODE-B through the ending with the cheats, a game over. Executed: **28,498 bytes** (US), **28,702** (JP).

- **Dead code** (`disasm/gb2/dead_<ver>.txt`): branch-reachable never-run 3,742 (US) / 3,636 (JP) bytes, dead
  516 / 572, no reference 67 / 17 (data mistaken for code and the interrupt RETIs). The `$89`/`$8B`/`$8C` cases above
  are the notable ones.
- **Unset flags**: none (direct-address scan; the game's objects are written through HL).
- **Input codes** (`disasm/gb2/pad_<ver>.txt`, 43 / 21 hits): the joypad reader itself (`$00:081E`-`$00:0B11`,
  `$FF00`), menu and password cursors (`$00:0309`, `$00:0339`), world-map scrolling (`$00:17E0`), A/Start
  confirmations. No hidden pad code; no soft-reset combination was found either.
- **Text** (`tools/gb2/textdump.py`, `disasm/gb2/text_us.tsv`, `text_jp.tsv`): `$00` space, `$01-$0A` digits, `$0B-$24`
  A-Z; JP `$30-$5D` katakana, `$60-$8D` hiragana, `$9x` small kana, stored as (mark, character) pairs with `$25` ゛,
  `$26` ゜. Story, rules, item help and the staff roll (`$06:7AF9` US) are all read in the runs. Unread: the JP mode
  name "?かくれアジト" (hidden hideout, MODE-A of one world, `$02:4053`); its US counterpart was read.
- **Stage format**: not decoded.
- **Debug features**: none found.

### Super Game Boy

Packets (`tools/emu/sgb.lua`): MLT_REQ 2 then 4 players, DATA_SND x8, ATTR_TRN, PAL_TRN, PAL_SET, CHR_TRN (both
halves), PCT_TRN, then PAL_SET fades. The border is the "BOMBER THEATER" stage in both versions.

![US border](img/gb2/sgb_border_us.png) ![JP border](img/gb2/sgb_border_jp.png)

## Regions

| | JP | US/EU |
|---|---|---|
| Title | BOMBERMAN GB 2 | BOMBERMAN GB, ™ (TCRF, Known) |
| Text | kana | English |
| Passwords | 11 | the same 11; plus the unused 12-record copy with 7824 |

![](img/gb2/title_jp.png) ![](img/gb2/title_us.png)

Logos: `docs/img/logos/gb2_jp.png`, `gb2_us.png` (`tools/gb2/logo.py`: the logo shares the window map with clouds
and trees, so everything outside its black outline is cut away).

Item icons: the password stores no items (a table index; the power-ups come from a per-world table), so none ripped.

## Open

- Stage format not decoded; SGB multitap battle not played.
