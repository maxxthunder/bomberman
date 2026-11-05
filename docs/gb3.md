# Bomberman GB 3 (Game Boy, Japan, 1996): passwords and secrets

Everything here comes from disassembling the ROM (`tools/sm83.py`, listing `disasm/gb3/jp.asm`) and checking in
Mesen 2 (`tools/gb3/run.sh`, helpers in `tools/gb3/lib.lua`). Addresses are `bank:address`.

Prior art: the GameFAQs "Bomberman GB 3" codes page (in `res/`). No wiki article on this game is saved there. Marks:
★ **New**, **Fixed**, **Known**.

| Dump | Header title | MD5 |
|---|---|---|
| Bomberman GB 3 (Japan) (SGB Enhanced) | `BOMBERMAN GB3` | `3addab2611566ab072fc996f8a81b224` |

256 KB MBC1, SGB flag `$03`, licensee `18`. It shares no code with the other Game Boy games (2-23 matching 32-byte
blocks); there was no release outside Japan.

## RAM that matters

| Address | Meaning | Evidence |
|---|---|---|
| `$C000` page | player object: `$C029` state (5 = dying, table `$01:4C4E`), `$C020` timer, `$C02A` | write log, `$01:4C07` |
| `$C1B8` | 1 = boss attack (DEB1F7F) | `$0D:691D`, `$00:13F7` |
| `$C1BC` | ★ unused invincibility flag (cleared at boot, never set) | `$00:12FA`, `$01:4BE6` |
| `$C1BD` | ★ unused clock-stop flag (cleared at boot, never set) | `$00:12FD`, `$00:29B1` |
| `$C2E0` / `$C2E1` | pad held (with repeat) / newly pressed | `$0D:6B0C` |
| `$C362` | area 0-6: Wood (モリモリ), City, Ice, Sand, Lava, Aqua, Evil | `$0D:6A26` |
| `$C363` | lives | `$00:1514` |
| `$C365` | stage - 1 (0-5) | `$0D:69E6` |
| `$C36B` | power-ups in effect; at a stage start it gets bits from the shop byte's high nibble (M1-M4, table `$00:140B`) | `$00:13DA` |
| `$C383-$C389` | areas cleared (one byte each) | `$0D:6A2A` |
| `$C38C` | capsules (クリスタル / カプセル) held: the shop currency | `$01:4BBA`, `$0A:769F` |
| `$C38D` | shop techniques bought, one bit each (see below) | `$0D:695A`, `$0A:767C` |
| `$C38E` | 0-2, set only by the stage-7 form of the password (below) | `$0D:6991`, `$02:7C52` |
| `$C480` | stage result: 0 playing, 1/2 died, 3 (set only when `$C1B8` = 2), `$FF` exit (cleared) | `$01:42D4`, `$01:45F0`, `$01:4690` |
| `$D200-$D206` | the 7 password digits (0-F); `$C621` cursor | `$0D:6B78` |

## The password

Code: `$0D:6AFC` (entry), `$0D:68EC` (check), `$02:7C41` (the code the game shows), tables `$0D:6AE0-$6AFB`.
`tools/gb3/password.mjs` decodes and encodes; `node tools/gb3/test_password.mjs` round-trips every state.

- **7 hex digits, 28 bits, every bit used.** `DEB1F7F` is compared as a literal first (boss attack). Otherwise:

| Field | Bits (digit:bit) | Meaning |
|---|---|---|
| s | d0:1 d0:0 d1:3 | stage 1-6; 7 = stage 6 with `$C38E` = b + 1; 0 rejects |
| b | d4:2 | must equal s & 1 (unless s = 7) |
| s check | d2:2 d3:1 = s & 3, d5:0 d6:3 = (s >> 1) & 3 | a second copy of s |
| group | d1:0 d2:3 | 3 = areas 0-2, 1 = areas 3-5, 2 = area 6; 0 rejects |
| y | d3:3 d3:2 | area = 3 × group + y - 1 (`$C362`, must be < 7); 0 rejects |
| group cleared | d6:2 d6:1 d6:0 | the 3 areas of the current group; the current area's own bit must be 0; area 6 takes none |
| shop | d0:2 d0:3 d1:1 d1:2 d2:0 d2:1 d4:3 d3:0 | `$C38D` bits 0-7 |
| capsules | d4:1 d4:0 d5:3 d5:2 d5:1 | `$C38C`, 0-18 |

- Entering group 1 marks areas 0-2 cleared, group 2 areas 0-5: the game is played in three tiers (Wood/City/Ice in
  any order, then Sand/Lava/Aqua, then Evil), which is what GameFAQs' notes describe.
- **The check is the capsule balance**: capsules + the prices of the bought techniques must equal the capsules the
  cleared areas paid out. Area payouts (`$0D:6AF2`): Wood 2, City 2, Ice 3, Sand 4, Lava 3, Aqua 4, Evil 0. Prices
  (`$0D:6AEA`, and on the shop screen): K 1, D 1, L 1, F 7, M1 1, M2 2, M3 2, M4 3.
- In all, **20,329** of the 2^28 strings are accepted (20,328 states + DEB1F7F; counted by brute force over
  `password.mjs`, and the encoder reaches all of them).

**Shop techniques** (bit order `$0A:7778`, prices as on the screen; icons ripped to `docs/img/items/gb3/`):

| Bit | Icon | Item | Price | File |
|---|---|---|---|---|
| 0 | ![](img/items/gb3/kick.png) | K kick | 1 | `kick.png` |
| 1 | ![](img/items/gb3/dash.png) | D dash | 1 | `dash.png` |
| 2 | ![](img/items/gb3/line.png) | L line bomb | 1 | `line.png` |
| 3 | ![](img/items/gb3/full.png) | F フルパワー (full power: always at full power; **Fixed**, GameFAQs: full bombs) | 7 | `full.png` |
| 4-7 | ![](img/items/gb3/moto1.png) ![](img/items/gb3/moto2.png) ![](img/items/gb3/moto3.png) ![](img/items/gb3/moto4.png) | M1-M4 モトボンバー1-4ごう: 1 takes one hit; 2 also hops one low hard block; 3 also breaks soft blocks when ridden into with B; 4 runs faster than dash and takes two hits | 1, 2, 2, 3 | `moto1.png`-`moto4.png` |

![The shop (after an area's 6th stage)](img/gb3/shop.png)

Names and effects are the shop's own help pages (Select on an item, messages 29-46 in `disasm/gb3/text_jp.tsv`; the K,
D and L pages were shown in Mesen, the others are read from the ROM).

**Codec API** (`tools/gb3/password.mjs`): `decode(code)` returns `{area, areaName, stage, extra, cleared[7], shop,
check}` (shop = the `$C38D` byte, check = capsules), `{special: 'boss'}` for DEB1F7F, or `null`; `validate(code)`;
`encode(area 0-6, stage 1-6, cleared[7], shop 0-255, extra 0-2)` returns the code or `null` when the capsules can't
balance; `stageCode(area, stage)` (nothing bought, only the required areas cleared); constants `AREAS`, `AREA_W`,
`SHOP_W`, `BOSS_ATTACK`.

### Verification

- **Fuzz** (`tools/gb3/fuzz.py`, `fuzz.lua`): 21,194 codes through the game's own check (savestate at `$0D:68EC`,
  results at `$0D:6871` accepted / `$0D:689C` rejected, area, stage, cleared flags, shop and capsules read back):
  every GameFAQs code, 224 encoded codes, 20,000 random, every digit at every position of 8 codes. 342 accepted,
  **0 mismatches**.
- **Typed with the pad** (`tools/gb3/test_codes.py`): all 73 distinct GameFAQs codes and 17 built ones. All as
  predicted.

![Wood 1, the final boss code, DEB1F7F, a rejected GameFAQs "maxed" code](img/gb3/codes_jp.png)

Entering: on the title, the 2nd line (ぱすわーど). Up/Down step the digit (0-F, wraps), Left/Right move the cursor
(wraps), A checks, B leaves.

## GameFAQs check

- The **"Passwords"** list (Dinob0t, CyberSach: Wood/City/Ice/Sand/Lava/Aqua 1-6, Fight Final Boss) and the
  **Boss Attack Code** DEB1F7F: all accepted and decode as their labels say (Known). Fight Final Boss F775818 is Evil 6
  with everything bought.
- **Fixed:** the **"Maxed Passwords"** list (36 codes, Aqua/City/Evil/Ice/Lava/Sand 1-6) is **all rejected**. With all
  8 techniques bought the prices total 18 capsules, and before Evil the cleared areas pay at most 14, so the balance
  can't hold; the Evil ones are wrong too (e.g. listed CF37D40, real CF37C00). Working Evil codes:

| Evil | nothing bought | everything bought |
|---|---|---|
| 1 | 0906640 | CF37C00 |
| 2 | 1144248 | D775808 |
| 3 | 1946648 | DF77C08 |
| 4 | 2104250 | E735810 |
| 5 | 2906650 | EF37C10 |
| 6 | 3144258 | F775818 |

![Evil 1, Evil 6 maxed](img/gb3/evil_codes.png)

## Secrets

### Unused debug flags (★ New)

Boot clears `$C1B9-$C1BD` (`$00:12F7`-`$00:12FD`). Two of them are read but never set anywhere:

- **`$C1BC`: invincibility.** The player-hit routine `$01:4BE6` jumps past the dying state when it is non-zero.
  GameShark `0101BCC1`: 0 hits in 6,000 frames of the bot (11 deaths without).
- **`$C1BD`: clock stop.** `$00:29B1`, the per-frame clock update, returns at once. GameShark `0101BDC1`: after
  1,200 frames of Wood 1 the clock still reads 3:00 (2:41 without).

### Cheats (★ New, `tools/gb3/test_cheats.lua`)

| Code | Effect | Verified |
|---|---|---|
| `0101BCC1` | invincible (the debug flag) | 0 hits / 6,000 frames |
| `C3B-E6B-081` + `E4B-E7B-198` + `4AB-E8B-E6D` (Game Genie) | invincible as a ROM patch (`$01:4BE6` -> `JP $4AE4`) | 0 hits |
| `010363C3` | infinite lives | 14 deaths, lives stay 3 |
| `01FF80C4` | every stage ends cleared (`$C480` = `$FF`) | Wood 1-6 then City 2 in 6,000 frames |
| `0101BDC1` | clock stops (the debug flag) | 3:00 after 1,200 frames |

Patch: `patches/gb3_invincible.ips` (file `$4BE6` = `C3 E4 4A`).

## Hidden-content sweep

Coverage (`tools/gb3/cov.sh`): intro and title, STORY, the 3rd title mode (ちゃれんじ, challenge mode: score attack on はらはら / どきどき stages, 2 or 5 minutes), the boss
attack, all three area tiers with the cheats, a game over. Executed: **44,079 bytes**.

- **Dead code** (`disasm/gb3/dead_jp.txt`): branch-reachable never-run 5,019 bytes, dead 1,244, no reference 0.
  The `$C480` = 3 path (`$00:16D1`, set by `$01:45F0` only when `$C1B8` = 2, probably the challenge mode) and
  `$00:16F7` never ran. Orphans (241) are mostly graphics data.
- **Unset flags**: the static scan finds only object-page reads (`$C012`, `$C100`, written through HL); `$C1BC`
  and `$C1BD` were found by hand from the boot clear (they have a write, the clear, so the scan doesn't list them).
- **Input codes** (`disasm/gb3/pad_jp.txt`, 31 hits): menus, the password cursor, movement. No hidden pad code.
- **Text** (`tools/gb3/textdump.py`, `disasm/gb3/text_jp.tsv`): text is drawn glyph by glyph into tiles (`$00:0880`:
  character n = one compressed tile from the pointer table `$00:08AD`, bank `$0C` below `$70`, bank 8 above); the
  table was built by rendering every glyph: `$00-$32` hiragana (gojuon, ユ where ぬ would be, small kana last),
  `$33-$69` katakana with punctuation and Ⓐ Ⓑ ♡, `$70-$79` digits. Messages: table `$0A:6905` (71 entries: 32
  characters in two lines of 16, then an 8-byte mask, 2 bits per character, 3 = ゛, 2 = ゜); shop prompts: `$0A:7CA6`
  (12: 20 characters + 20 mark bytes, `$AA` ゛, `$AB` ゜). Area briefings, the intro and ending story, boss lines and
  the shop all show in the runs. Not shown: message 19 (an area that moves) and 68 (rocks that stop moving), the
  shop help for F and M1-M4 and its M2-M4 prompts; all are picked by the same tables, so none is known to be unused.
  The title, password and challenge-mode words are BG tile maps (not in this dump).
- **Graphics** (CDL incl. an SGB run): the unread blocks are small, plus two pictures at `$0B:4BBE` / `$0C:7308`
  that graphics sets do load (set records at `$00:0B52`, `$00:0AAF`) on screens the runs didn't reach. Nothing unreferenced found.
- **Stage format**: not decoded.

### Super Game Boy

Packets (`tools/emu/sgb.lua`): MLT_REQ 2 / 1, DATA_SND x8, CHR_TRN x2, PCT_TRN, ATTR_TRN, PAL_TRN, PAL_SET, then
MLT_REQ 4 players and palette fades. ★ New: the 4 players are never used. The pad reader `$00:055E` stores all four
pads (`$C2E0 + 2 x id`), but only pad 2's new-press byte is touched (`$00:021F`, a latch next to pad 1's) and no
code reads pads 2-4; with 4 players answered and pads 2-4 fed (`sgb.lua`), the title still has only すとーりー /
ぱすわーど / ちゃれんじ and challenge mode is one player. The border (space, a castle, Bomberman, characters in the corners):

![SGB border](img/gb3/sgb_border_jp.png)

## Title

![Title](img/gb3/title_jp.png)

Logo: `docs/img/logos/gb3_jp.png` (`tools/gb3/logo.py`).

## Open

- What `$C38E` (the stage-7 password form) changes in play.
- Challenge mode wasn't played to a result; the stage format is not decoded.
