# Bomberman (PC Engine / TurboGrafx-16, 1990): passwords and secrets

Everything here comes from disassembling the HuCards (`tools/pce90/huc6280.py`, a HuC6280 disassembler that
follows the MPR bank mapping; listings in `disasm/pce90/`) and checking the results in Mesen 2
(`tools/pce90/run.sh` runs a Lua script headless with `tools/pce90/lib.lua` prepended). Addresses are
`bank:address` as mapped when the code runs; the password code is bank 2 at `$C000`, the Special Select Room
bank 1 at `$A000`. Work RAM is `$2000-$3FFF`. US addresses unless a version is named. The only prior art is the
TCRF article in `res/`. Marks: ★ **New** (not in TCRF), **Fixed** (TCRF is wrong or incomplete), **Known** (TCRF
has it; the mechanism is added here).

| Dump | MD5 | vs US |
|---|---|---|
| USA | `22945308eb41396f39c00444be9f251f` | |
| Japan (En) | `4bece0e426eec02f894399219f1951cf` | 136,665 bytes differ. The password, Special Select Room and sound-test code sit at the same addresses and differ only in JSR targets into bank 0 (shifted by `$19`) |

## RAM that matters

| Address | Meaning | Evidence |
|---|---|---|
| `$2000-$2007` | high score, one decimal digit per byte, `$2000` = tens (the ones digit is always 0), `$2001` = hundreds | Special Select Room test: writing `$2001` = 4 shows HI 400 |
| `$2010` (`$10`) | 1 when the last attract-mode demo played to its end, 0 when Run cut it short | `$0B:CDBE` / `$0B:CDC2` |
| `$2200` / `$220A` | pad 1 held / newly pressed: `$01` I, `$02` II, `$04` Select, `$08` Run, `$10` Up, `$20` Right, `$40` Down, `$80` Left | `$01:A004`, `$02:C8D3` |
| `$243A` | player power-up bits: `$10` remote control, `$20` wall pass, `$40` bomb pass, `$80` invincible (timer `$2446`); bits 0-2 = dying/dead state | `$09:8757` item handlers, `$09:8AE9`, `$09:8FA3` |
| `$284A` | round - 1 (the game calls it SCENE in the select room) | `$02:C77D`, `$01:A156` |
| `$284B` | stage - 1 | same |
| `$284C` | bombs (1-10) | `$09:87A5` |
| `$284D` | fire (blast length) | `$09:8784` |
| `$284E` | roller skate: walk speed `$0100` instead of `$00C0` per frame | `$09:8B2E` |
| `$33B4` / `$33B6` | title menu cursor / chosen mode (0 1P START, 1 2-5P BATTLE, 2 C-LINK BATTLE, 3 PASSWORD, 4 LOAD) | `$01:A64F` |
| `$3444` / `$3445` | password grid cursor column / row | `$02:C84D`, `$02:C812` |
| `$3446-$344D` | the 8 letters entered (ASCII, `$20` = empty) | `$02:C908` |
| `$344F` / `$3450` | input position (0-7) / furthest position used | `$02:C90B` |
| `$3451` | `$FF` after BOMSOUND (sound test armed) | `$02:C968`, `$02:C76B` |
| `$3452-$3455` | the 4 decoded password bytes | `$02:CBBD` |
| `$345A-$345E` | decoded round-1, stage-1, bombs, fire, speed (copied to `$284A-$284E` on success) | `$02:CC34`-`$02:CCAD`, `$02:C77A` |
| `$3465` | decoder result: 1 valid, 2 invalid | `$02:CCD2`, `$02:CCD8` |

## The password

Code: `$02:C8D3` (entry screen input), `$02:CBAE` (decoder), `$02:CA40` (encoder). Tables: letter rows
`$02:CD8B`, field masks `$02:CD5F`, field byte indexes `$02:CD75`. `tools/pce90/password.py` and the
self-contained `tools/pce90/password.mjs` do both directions; `password.py --test` and
`node tools/pce90/test_password.mjs` round-trip every state.

- **8 letters, 4 bytes.** Letters 2k and 2k+1 are byte k: each letter is looked up (`$CD3A`) in that pair's
  16-letter row and its index is a nibble, low nibble first. A letter not in its row rejects the code.

  | Letters | Row (`$CD8B`) |
  |---|---|
  | 1-2 | `MUROYAGCQXSKIWHB` |
  | 3-4 | `WRECKFVBYHOZNAGL` |
  | 5-6 | `NEWSLOGIMPHJTVBQ` |
  | 7-8 | `NUCLEARHPSTVZYGK` |

- **Byte 0 is a header** (`$CBDE`-`$CC14`): bits 5, 6, 7 invert bytes 1, 2, 3 (`EOR #$FF`); bits 3-4 must be
  `10` (`AND #$18 / CMP #$10`, else rejected); bits 0-2 = n, and bytes 1-3 as one 24-bit big-endian number are
  shifted right n times (`$CD24`).
- **Bytes 1-3 then hold six fields**, each read bit by bit, most significant first, from a (byte, mask) list
  (`$CCE9`). Every bit read as 1 is counted in `$345F`.

  | Field | Bits (byte:mask, MSB first) | Accepted | Stored |
  |---|---|---|---|
  | round | 1:08 3:04 2:10 2:04 | 1-8 (`DEC A / CMP #$08`) | `$284A` = round-1 |
  | stage | 3:40 2:40 1:01 3:08 | 1-8 | `$284B` = stage-1 |
  | bombs | 2:80 1:10 2:01 3:20 | 1-10 (`BNE`, `CMP #$0B`) | `$284C` |
  | fire | 3:10 2:08 3:02 1:02 | 1-15 (non-zero) | `$284D` |
  | speed | 1:20 | 0-1 | `$284E` |
  | check | 2:02 3:01 1:04 3:80 2:20 | must equal the number of 1 bits in the five fields above (`$CCCB`) | |

  Bits 22-23 of the shifted value are not read, so they are free.
- Nothing else is saved: no score, lives, remote control, wall pass, bomb pass.
- ★ **New: fire up to 15.** In play a fire-up stops at 5 (`$09:8784 CMP #$05`) and a bomb-up at 10, but the
  password takes fire 1-15. `MUOEPHLA` (8-8, 10 bombs, fire 15, skate) set `$284D` = 15 in Mesen.
- **The encoder** (`$CA40`, called from `$D303`, the screen that offers CONTINUE / END / SAVE, strings at `$D565`)
  writes the fields from `$284A-$284E` with the free bits 0, picks the shift from `$E966` with X = 3 (0-2) and the
  flip bits with X = 8 (0-7) (`$CB12`-`$CB2E`), so it can show **24 different codes for one state**.
- **The decoder accepts many more.** Shifts 3-7 are legal (the encoder never uses them). With shift n the top n bits
  of y must be 0, because the shift brings in zeros, and the n bits shifted out are free. So the number of codes per
  state runs from **96** (24 × 4 for the two free bits) up to **2,080**; 1-1 with the starting power-ups has 544.
  In all, **5,930,496** of the 2^32 in-row letter strings are valid (`password.py --count`): 19,200 states
  (8 × 8 × 10 × 15 × 2), every one reachable.

### Codes verified

Every code below was **typed with real pad presses** in Mesen from the password screen (`tools/pce90/test_codes.py`,
`tools/pce90/test_codes.lua`), END pressed with I, and `$3465` and `$284A-$284E` read back. TCRF lists no level
passwords, so these are all status *unchecked* (no prior art to check against) in `docs/pce90_codes.json`.

| Code | Effect | Versions typed | Notes |
|---|---|---|---|
| `MUVWLNPC` | 1-1, 1 bomb, fire 1 | US, JP | the "zero" code (flip 0, shift 0) |
| `MUVWNEPC` | 2-1 | US | |
| `MUVWLSPC` | 3-1 | US | |
| `MUVWNNZC` | 4-1 | US | |
| `MUVWLWZC` | 5-1 | US | |
| `MUVWNSZC` | 6-1 | US | |
| `MUVWLEZT` | 7-1 | US | |
| `MUGWNNPC` | 8-1 | US, JP | |
| `MUOEPHLA` | 8-8, 10 bombs, fire 15, skate | US, JP | everything maxed |
| `MUEEVHVU` | 1-1, 10 bombs, fire 15, skate | US, JP | |
| `RKGEWVHY` | 3-5, 4 bombs, fire 2, skate | US, JP | flip 5, shift 2: a code the game itself could show |
| `ACLCHINN` | 1-1 | US | shift 5: never shown by the game, still accepted |
| `CUVYVPNP` | 1-3, 3 bombs, fire 14 | US, JP | shift 7 |
| `MUVWLNPU` | rejected | US, JP | check count wrong; PASSWORD ERROR |

![Round codes 1-8](img/pce90/round_codes_1-8.png)

![MUOEPHLA](img/pce90/MUOEPHLA_8-8_max.png) ![MUVWLNPU](img/pce90/MUVWLNPU_rejected.png)

### Fuzz against the game's own decoder

The space is 2^32 byte values, too many to run through the emulator one by one (~750 decodes/s per Mesen
instance). What was run in the real decoder, with the result read at its own exits (`$CCD0` valid with
`$345A-$345E`, `$CCD6` invalid):

| Set | Codes | Accepted | Mismatches with `password.py` | US | JP |
|---|---|---|---|---|---|
| `tools/pce90/fuzz.py`: one code for each of the **19,200 states** (random flip and shift 0-7), 10,000 random in-row codes, every letter A-Z at every position of one code, all 256 values of byte 0 under three tails, BOMSOUND | 30,177 | 19,235 | 0 | yes | yes (same counts) |
| `tools/pce90/fuzz_all.py` (`fuzz_all.lua`): byte 0 = `$10`, bytes 1-3 = every value `$000000`-`$030D3F` in a row | 200,000 | 1,019 | 0 | yes | |

`fuzz.py` reloads a savestate for each code. `fuzz_all.lua` instead patches a small loop into free ROM in bank 2
(`$D600`, `$FF` fill in the dump): it builds the letters, jumps to `$CBAE`, and both decoder exits jump back to it,
so no Lua runs per code; accepted results go through a ring buffer at `$3100`. Both methods gave identical
accepted lists over the same 200,000 codes. The total of 5,930,496 is computed exactly from the bit layout above
(`count_valid()`), and the layout is what every emulator run confirmed. `password.mjs` matches `password.py` on
202,743 codes (200,000 random plus 2,743 encoded).

JP: the decoder, tables, BOMSOUND check and encoder are byte-identical to US apart from the bank-0 JSR targets
(`$CCE7`, `$CB14`, `$CB1F`). The JP `fuzz.py` run gave the same 30,177 / 19,235 / 0, and the 8 codes typed in JP (BOMSOUND
included) all behaved as predicted. **Both versions take the same passwords.**

## Entering a password

Title menu: PASSWORD is the 4th item (three Downs from 1P START / GAME START, then Run).

- The screen shows the grid `A-J` / `K-T` / `U-Z < > END` and eight dashes. The **grid cursor starts on A**
  (`$3444` = `$3445` = 0, `$02:C6C7`); the **input position starts at the first dash** (`$344F` = 0).
- **D-pad** moves the grid cursor (`$02:C7D3`). Left/Right wrap within the row: 10 columns on the first two rows,
  9 on the last (`U V W X Y Z < > END`). Up/Down wrap over the 3 rows; moving onto the last row from column 10
  (J or T) lands on END (`$02:C825`, `$02:C881`).
- **I or Run** (`$220A & $09`) on a letter writes it at the input position and moves right (`$02:C8FF`). After
  the 8th letter the position stays on the 8th, so further letters overwrite it.
- **II**, or **`<`**, moves the input position left without erasing (`$02:C93A`); **`>`** moves it right, but
  only as far as letters have been typed (`$02:C948`).
- **END** submits (`$02:C959`): first the BOMSOUND compare, then the decoder. On a bad code PASSWORD ERROR
  shows, the letters are cleared and the position goes back to the first dash (`$02:CCD6`). A good code goes to
  the ROUND screen and then STAGE x-y GAME START. A code with empty positions is rejected (a space is in no row).

## Secrets

### BOMSOUND: sound test (Known)

`$02:C959` compares the 8 letters with `BOMSOUND` at `$02:C96F`. A match sets `$3451` = `$FF` and then falls
into the normal decoder, which rejects it (the code is invalid as a password), so PASSWORD ERROR shows. The flag
survives: when the next **valid** code is entered, `$02:C76B` sees `$3451` = `$FF` and jumps to the sound test at
`$02:C59E` instead of copying the code to `$284A`. The flag is cleared only when the password screen is opened
again (`$02:C6CD`).

Sound test controls (`$02:C5EC`): I and II step the number `$3440` up and down through `$00-$39`, Run plays it,
Select stops. There is no exit: only a reset leaves the screen. Verified in US and JP: BOMSOUND, END,
MUVWLNPC, END → SOUND-00.

![Sound test](img/pce90/bomsound_sound_test.png)

### Special Select Room (Fixed)

TCRF: "300 points or more", reset, hold Down+Select+I+II as the title reappears after the first demo, Run on the
menu, keep holding Run through the intro. The check is `$01:A001`, called at `$00:EAEC` when the 1P intro ends,
only if the mode is 1P START (`$33B6` = 0), `$33BA` = 0 and `$284A` ≠ 8. It opens the room only if all of these
hold at that moment:

1. `$2200 & $4F = $4F`: **Down, Run, Select, II and I all held**;
2. `$10` ≠ 0: the **last attract demo played to its end**. Pressing Run during a demo clears `$10`
   (`$0B:CD86` → `$0B:CDC2`);
3. `$2001` = 3: the **hundreds digit of the high score is exactly 3**. So 300-390, 1,300, 2,350... work, and
   200 or 400 do not. "300 or more" is wrong.

The reset isn't needed itself: it's just a quick way back to the title with the high score kept, after which
the title times out into a demo. Holding the buttons before the menu appears means the menu never sees a new
Down or Select press, so the cursor stays on 1P START and Run starts the game.

Verified in Mesen (`tools/pce90/test_select_room.lua`, buttons held from the demo on, high score written to RAM),
left to right: 300, 400, 300 with the demo cut by Run, 300 without the reset, 1,300, 200. Only 300, 300 without
reset and 1,300 open the room. JP: same code at the same address, 300 opens it and 400 doesn't.

![Special Select Room conditions](img/pce90/special_select_room_conditions.png)

The room (`$01:A063`): Up/Down (or Select) moves between the 8 lines, I/II change the value: SCENE 1-8
(`$284A`, wraps), STAGE 1-8 (`$284B`), bombs 1-10 (`$284C`), fire 1-15 (`$284D`, again past the in-game cap of
5), and four ON/OFF power-ups, which are the `$243A` bits `$10` (remote control: bombs don't tick, II sets them
off, `$09:8FA3`/`$09:90A0`), `$20`, `$40` (passing through soft blocks / bombs, `$09:8B03`/`$09:8B0C`; which bit
is which is not checked in play) and `$80` (invincible, `$09:8716`). ★ **New:** entering the room also sets
`$284E` = 1 (`$01:A049`), so the game always starts with the roller skate. Run starts the chosen stage.

![Special Select Room](img/pce90/special_select_room.png)

### TurboTap detection (★ New, minor)

When a battle mode is chosen, `$00:E371` compares the new presses of all five pad ports. Without a TurboTap
every port reads pad 1, so all five are equal and `$33` = 0; any difference sets `$33` = 1. In 2-5P BATTLE
`$08:601E` sends `$33` = 0 to `$08:78D9` (not traced; presumably the tap error screen TCRF shows) instead of the
battle setup; C-LINK BATTLE skips the test. So with a tap,
the check fails only if all five players happen to press exactly the same buttons on the same frame.

## Unused content

- **Music 2D and 39 (Fixed: used, in C-Link battle only).** The battle result code plays `$31` (`$08:6E2A`) and
  `$32` (`$08:7389`). In C-LINK BATTLE (`$33B6` = 2, two consoles linked) each console checks its own player
  (`$53`) instead: if that player's status bit 0 is set (`$23BD`/`$23BE`, the "dead" state set at `$09:8CBD`),
  it plays **`$39`** in place of `$31` and **`$2D`** in place of `$32` (`$08:6E4B`, `$08:73AD`). So TCRF's
  "alternative death theme" (39) and "slowed-down Game Over" (2D) are the losing console's jingles. A link
  cable can't be emulated, so this is from the code only. Same in JP (`$08:6E7F`, `$08:73E1`).
- **Music 36, 37, 38 (Known).** No `LDA #n / JSR` to the sound routine (`$EA57` US, `$EA3E` JP) uses `$36`, `$37`
  or `$38` (nor `$00`, `$0E`, `$15`, `$16`, `$1E`, `$26`) in either ROM. They are reachable only from the sound
  test (range `$00-$39`, `$02:C5FB`). The scan finds only immediate operands, so a number loaded from a table
  wouldn't show; the absent `$0E`-`$26` are probably stage tunes picked that way.
- **Black Bomberman sliding sprite (Known):** from TCRF, not located in the ROM here.

## Regions

| | US | JP |
|---|---|---|
| Passwords, BOMSOUND, Special Select Room | same code and data | same |
| Title menu | 1P START, 2-5P BATTLE, C-LINK BATTLE, PASSWORD, LOAD | GAME START, BATTLE, BATTLE (link icon), PASSWORD, LOAD |
| Password prompt | PLEASE INPUT PASSWORD. | PASSWORD ヲ ニュウリョクシテクダサイ |
| Title logo | ™ added | no ™ |
| Copyright line | FROM NEC ©1991 HUDSON SOFT | ©1990 HUDSON SOFT |

![US title](img/pce90/title_us.png) ![JP title](img/pce90/title_jp.png)

The game also saves to backup RAM (Tennokoe / CD-ROM² "file cabinet"; strings `BOMBERMAN1-3`, `!BM FORMAT!`,
`WHICH FILE TO LOAD?`, LOAD on the title, SAVE after a game over). The file list shows round and stage per file (`$02:D286`). This is a normal feature; it isn't covered further here.

## Title logos

`docs/img/logos/pce90_us.png` (227×71) and `pce90_jp.png` (231×71, no ™). The title screen's VRAM, VCE palette
and SAT were dumped at frame 600 (`tools/pce90/vdump.lua`). The logo is BG: BAT tiles 33-63 × 2-13 of the
128×64 map, which the title shows by a raster split. `tools/pce90/logo.py crop` renders those tiles (4bpp
planar, palette from the BAT word) with colour 0 transparent and crops to the bounding box. The cloud and the
eyes on the two bombs seen on the title are sprites (palette 3, behind the BG), so they aren't part of the logo.

## Open

- The full 2^24 `fuzz_all.py` sweep was not run: it needs hours of emulator time on this machine.
- Which of `$243A` bits `$20` / `$40` is wall pass and which is bomb pass (cell type 0 vs 2-5 at `$09:8AE9`).
- Where the black Bomberman sliding sprite is.
