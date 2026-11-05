# Bomberman GB (Game Boy, 1994) / Wario Blast featuring Bomberman!: passwords and secrets

Everything here comes from disassembling the ROMs (`tools/sm83.py`, a recursive SM83 disassembler that follows MBC1
bank switches and takes every executed code start from Mesen's code/data log; listings in `disasm/gb1/`) and
checking the results in Mesen 2 (`tools/gb1/run.sh` runs a Lua script headless with `tools/gb1/lib.lua` and
`tools/emu/mesen_gb.py`'s helpers prepended). Addresses are `bank:address` (bank 0 at `$0000`, the switched bank at
`$4000`). JP addresses unless Wario is named; most routines sit at the same address in both.

Prior art: the GameFAQs codes page for Wario Blast and the TCRF article on Wario Blast (both saved in `res/`). The
GameFAQs page titled "Bomberman GB" is the US release of JP Bomberman GB 2 ([gb2.md](gb2.md)), but its 4622 and 5656
also work here. Marks: ★ **New** (in neither), **Fixed** (posted wrong or incomplete), **Known**.

## Dumps: which game is which

| Dump | Header title | MD5 | Game |
|---|---|---|---|
| Bomberman GB (Japan) (SGB Enhanced) | `BOMBERMAN GB` | `2cad6ee6df3402aeb8f8ab7921517779` | this game (JP 1994) |
| Wario Blast Featuring Bomberman! (USA, Europe) (SGB Enhanced) | `WARIO BLAST` | `14fe7234ee4bcb14adf20c743f084a35` | this game, US/EU, version tag `wario` |
| Bomberman GB (USA, Europe) (SGB Enhanced) | `BOMBER MAN GB` | `7e4c9c3620bea7b633394beb67e9680b` | **not** this game: it is JP Bomberman GB 2 ([gb2.md](gb2.md)) |

All are 256 KB MBC1 (cart type `$01`), no RAM, SGB flag `$03`, licensee `18` (Hudson). JP and Wario differ in
182,964 bytes, but banks 2, 5 and 7 are nearly equal (740, 1,386, 184 bytes) and the password check, its table
format, the player-hit check (`$01:4837`) and the set logic are the same code at the same or nearby addresses: the
same game, reworked. The US "Bomberman GB" shares only one 32-byte block with JP Bomberman GB and 6,681 with JP
Bomberman GB 2 (three banks identical), so the user's guess holds: **US Bomberman GB = JP Bomberman GB 2; JP
Bomberman GB = Wario Blast.**

## RAM that matters

| Address | Meaning | Evidence |
|---|---|---|
| `$C000` page | player object: `$C000` state (2 alive, 1 dying, 0 gone), `$C006` X | `$01:4861`, write log in Mesen |
| `$C100`, `$C200`, `$C300` | the enemy bombers' objects (same layout) | `$01:487E` |
| `$C3D5` | Wario only: 1 = playing as Bomberman, 0 = as Wario | `$0A:42A0`-`$0A:430E` |
| `$C3F0` | stage 0-31: round = n / 4 + 1, n % 4 = stage 1-3 or the boss | `$00:181F` (INC, `CP $20`) |
| `$C3F1` | music/sound request | `$0A:42CD` |
| `$C3F2-$C3F4`, `$C3F5` | result of sets 1-3 (1 lost, 2 won), set number | `$00:17B8`-`$00:181F` |
| `$C3FB` | 1 = start with every power-up (code 4622) | `$0A:42E0`, readers `$00:10AD`, `$00:2727`, `$01:405B` |
| `$C590` | set result: 2 won, 1 lost, 0 draw | `$01:48C7`-`$01:48EF` |
| `$C597-$C59A` | the 4 password digits (0-9); `$FFD3` cursor, `$FFD1` the digit being edited | `$0A:4258` |
| `$CC60` / `$CC61` | pad held / newly pressed (bit 0 A, 1 B, 2 Select, 3 Start, 4 Right, 5 Left, 6 Up, 7 Down) | `$0A:4194` |

## The game

The normal game is a string of duels: each stage is one or two sets against Black Bombermen in a small arena
(`ROUND1-1 VS ENEMY1`); two sets won clear it, two lost go to the continue screen. 8 rounds of 3 stages and a boss
make 32 stages. There are no lives, so there is no lives cheat: a lost match only costs a continue.

## The password

Code: `$0A:4194` (entry), `$0A:4272` (check; Wario `$0A:4255`), table `$0A:42EE` (Wario `$0A:4315`).
`tools/gb1/password.mjs` holds both tables; `node tools/gb1/test_password.mjs` checks it.

- 4 digits on the title's PASSWORD line. **Nothing is computed**: the check compares the digits with a list of
  5-byte records (4 digit bytes `$E0` + digit, one value), `$FF` ends it. JP has 34 records, Wario 68.
- Values below `$20` set `$C3F0` to the value. Wario uses `$00-$1F` for Bomberman (`$C3D5` = 1) and `$20-$3F` for
  the same 32 stages as Wario (`$C3D5` = 0, `$C3F0` = value & `$1F`).
- JP `$20` / Wario `$40` (Bomberman), `$42` (Wario): `$C3FB` = 1, start at 1-1 with every power-up.
- JP `$21` / Wario `$41`, `$43`: the extra battle (`$C3F1` = `$0C`, `$00:34B2` JP / `$00:3457` Wario).
- The 32 Bomberman stage codes are **the same in both versions** (Wario only added the Wario column and the two
  Wario specials), so every GameFAQs "(Bomberman)" code is also a JP code.

| Round | Stage 1 | Stage 2 | Stage 3 | Boss | Wario: 1 | 2 | 3 | Boss |
|---|---|---|---|---|---|---|---|---|
| 1 | 4696 | 7006 | 8774 | 5141 | 6964 | 6007 | 4778 | 1415 |
| 2 | 9185 | 4610 | 2630 | 3569 | 5819 | 0164 | 0362 | 9653 |
| 3 | 8401 | 8264 | 0173 | 2828 | 1048 | 4628 | 3710 | 8282 |
| 4 | 4152 | 3451 | 4312 | 0874 | 2514 | 1543 | 2134 | 4780 |
| 5 | 1909 | 5010 | 2904 | 1726 | 9091 | 0105 | 4092 | 6271 |
| 6 | 3614 | 0610 | 9867 | 9618 | 4163 | 0160 | 7689 | 8169 |
| 7 | 1884 | 7702 | 6925 | 7110 | 4881 | 2077 | 5296 | 0117 |
| 8 | 5814 | 8136 | 0390 | 3158 | 4185 | 6318 | 0930 | 8513 |

Specials: **4622** every power-up, **5656** extra battle; Wario adds **2264** / **6565**, the same as Wario.

**Codec API** (`tools/gb1/password.mjs`): `decode(code, version = 'jp' | 'wario')` returns
`{value, kind: 'stage' | 'powerup' | 'battle', round, stage, boss, player: 'bomberman' | 'wario'}` (round/stage/boss
only for stages) or `null`; `validate(code, version)`; `encode(round, stage, player, version)` (round 1-8, stage 1-4,
4 = boss); `allCodes(version)`; `TABLES` (version -> code -> table value).

### Verification

- **Fuzz** (`tools/gb1/fuzz.py`, `fuzz.lua`): all 10,000 codes were written into `$C597-$C59A` and run through the
  game's own check from a savestate at its entry, the result read at its two exits. JP: 34 accepted, Wario: 68,
  **0 mismatches** with `password.mjs` in either.
- **Typed with the pad** (`tools/gb1/test_codes.py`, `test_codes.lua`): every code in both versions (36 JP runs, 70
  Wario runs including `0000` and `1234`), Up/Down on the digit, A to the next, Start to check; `$C3F0`, `$C3FB`,
  `$C3D5` and the reject/battle exits read back. All as predicted.

![JP: 4696, 4622, 5656, a rejected code](img/gb1/codes_jp.png)

![Wario: 6964, 2264, 5656, 6565, 8513](img/gb1/codes_wario.png)

Entering: on the title, Down to PASSWORD, Start. Up/Down step the digit (wrapping 0-9), A stores it and moves right
(the next digit starts at 0), B goes back (and from the first digit leaves the entry), Start stores the 4th and checks.

## Secrets

### 5656: the extra battle (Known, mechanism added)

GameFAQs calls it Battle Mode / Extra Battle. It's an elimination run: the JP intro text (GREAT BATTLE) reads
"how many Black Bombermen can you defeat before you go down? The elimination battle begins!"; Wario's is THE
BATTLE. In JP it is reachable only by password; the title has no battle entry.

![Extra battle intro (SGB colours)](img/gb1/battle_intro_sgb.png)

### Cheats (★ New)

All in `docs/gb1_codes.json` (`section: "cheat"`), verified with `tools/gb1/test_cheats.lua` (random-input bot).

| Code | Effect | Verified |
|---|---|---|
| `C98-37B-D5D` (Game Genie) | invincible: RET over the hit check `$01:4837` (same in both) | 6,000 frames: 0 hits; 7 without |
| `010000C1` + `010000C2` + `010000C3` (GameShark) | every set won at once (enemy states 0) | 6 sets won, 1-1 to the 1-boss in 6,000 frames; used to reach the ending |

Patch: `patches/gb1_invincible.ips` (file `$4837` = `$C9`, both versions; the same byte as the Game Genie code).

## Hidden-content sweep

Coverage: Mesen code/data logs from the attract mode, the password screen with wrong codes and every special,
battles, and the whole game to the ending with the cheats above (`tools/gb1/cov.sh`, scenarios in `cov.lua`).
Executed code: **21,136 bytes** (JP), **21,274** (Wario).

- **Dead code** (`tools/gbsweep.py dead`, `disasm/gb1/dead_<ver>.txt`): never-run code reached by a branch from code
  that ran: 4,771 bytes (JP) / 4,802 (Wario); reached only from never-run code: 1,538 / 1,316; no reference: 3 (the
  unused serial/timer/joypad interrupt RETIs). The larger stretches sampled are set and boss paths the bot never
  forced (draws, boss losses) and sound-driver states; not every stretch was read. The orphan list (428 / 446) is mostly graphics
  data in banks 2 and 9 that decodes as code; nothing in it references text or RAM the game lacks.
- **Unset flags** (`tools/gbsweep.py flags`): 15 sound-driver work bytes at `$D905-$D955`, written indexed through HL.
  None is a real flag.
- **Input codes** (`tools/gbsweep.py pad`, `disasm/gb1/pad_<ver>.txt`, 22 hits each): A+B+Select+Start held
  (`$00:07B7`, soft reset), the pause, the password digits and movement. **No hidden pad code** beyond the passwords.
- **Text**: the title and menu strings are BG tile codes (A = `$EA`, space = `$C0`, `$0A:44E7` JP), the story/battle
  texts tile records at `$04:567E`; no readable unused string was found. A full text dump is not done (no complete
  tile-to-kana table).
- **Stages**: the arenas are built at run time; the stage format is not decoded here.
- **Debug features**: none found (no unreferenced menu, no flag read without a write).

### Super Game Boy

Captured without an SGB BIOS: `tools/emu/sgb.lua` decodes the packets the game writes to `$FF00` and answers
MLT_REQ like an SGB, so the game takes its SGB path; `tools/emu/sgb_dump.py` renders the transfers.
At boot (frame 85): MLT_REQ 2 players / back to 1 (the detection), eight DATA_SND (the standard SNES-side patch),
MASK_EN freeze, CHR_TRN (tiles 0-127), PCT_TRN (the border map and palettes), PAL_TRN, ATTR_TRN, PAL_SET.

| | JP | Wario |
|---|---|---|
| Border | ![](img/gb1/sgb_border_jp.png) | ![](img/gb1/sgb_border_wario.png) |
| Title in SGB colours | ![](img/gb1/sgb_title_jp.png) | ![](img/gb1/sgb_title_wario.png) |

Wario's border puts Wario where the JP border has a blue Bomberman (top centre), as TCRF says (Known). TCRF also says
the game takes the SNES multitap; at the title only the 2-player detection request is sent, so that wasn't seen here.

## Regions (Wario vs JP)

| | JP | Wario |
|---|---|---|
| Title | BOMBERMAN GB, START / PASSWORD | WARIO BLAST featuring BOMBERMAN!, same menu |
| Player | Bomberman only | Bomberman or Wario for the whole game (`$C3D5`); the other one is the enemy (TCRF, Known) |
| Passwords | 34 codes | the same 34 + 32 Wario stage codes + 2264, 6565 |
| Story | attract story about the stolen techniques (TCRF quotes it, Known) | removed |
| SGB border | blue Bombermen | Wario in the top centre |

![JP and Wario titles](img/gb1/title_jp.png) ![](img/gb1/title_wario.png)

Logos: `docs/img/logos/gb1_jp.png`, `gb1_wario.png` (`tools/gb1/logo.py`: BG tiles of the title from
`tools/gb1/vdump.lua`, colour 0 transparent).

Item icons: the password stores no items (a table index only), so none were ripped for this game.

## Open

- The SGB multitap game TCRF mentions was not reached.
- Text dump and stage format not done.
