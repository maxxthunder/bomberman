# Super Bomberman 2 (SNES): passwords and secrets

Everything here comes from disassembling the ROM (`tools/disasm.py`, coverage grown from Mesen 2 code/data
logs via `tools/sb2/cdl2entries_hirom.py`) and checking the results in Mesen 2. Addresses are for the USA ROM
(HiROM, banks `$C0-$CF`) unless noted. The other dumps share banks `$C0`/`$C1` byte for byte where it matters;
bank `$CC` code sits at a different offset in each (Europe +`$5B`, Japan -`$11`, Caravan +`$198`), so the
tools find routines by their bytes instead of by address.

Prior art: the GameFAQs codes page and a published article on the game (both in `res/`). Finds are marked
**★ New** (in neither), **Fixed** (posted wrong) or **Known**. None of the posted codes was wrong.

## The password

Code: `$CC:1926` (check), table `$CC:0000`, stage table `$CC:19BE`, full-power kit `$C1:3BB5`.
`tools/sb2/password.py` and `tools/sb2/password.mjs` reproduce it.

- Four digits, kept as words at `$7F:0028`, `$7F:002A`, `$7F:002C`, `$7F:002E`, cursor `$7F:0032` (see
  "Entering a password" below).
- **There is no checksum or encoding.** START compares the four digits with an 11-entry table of 4-byte
  records at `$CC:0000` (loop `$CC:193A`, count `CMP #$000B` at `$CC:196C`). A match stores the index in
  `$1C6A` and sets `$7F:0030` = 1; a miss sets it to 2 and clears the digits.
- So the whole space is 10,000 codes and exactly 11 work, in every version:

| Index | Code | Effect | Set by |
|---|---|---|---|
| 0 | `4361` | stage 1-1 | `$1A` = `$10` (table `$CC:19BE`) |
| 1 | `6442` | stage 2-1 | `$1A` = `$20` |
| 2 | `3903` | stage 3-1 | `$1A` = `$30` |
| 3 | `9564` | stage 4-1 | `$1A` = `$40` |
| 4 | `7735` | stage 5-1 | `$1A` = `$50` |
| 5-9 | `1111` `5462` `6763` `8784` `6925` | stage 1-1 ... 5-1 with full power | index ≥ 5 at `$C1:3BC0` |
| 10 | `5656` | sudden-death flag `$1C68` = `$FFFF`, back to the title (`$CC:17D2`) | see below |

- The table has a 12th record, `0000`, that the loop never reaches, so `0000` is rejected like any other
  wrong code.
- `$1A` is the stage: high nibble = world 1-5, low nibble = area − 1. The "x-y START!" card shows area + 1.
- **Full power** (`$C1:3BC9`) writes player 1's kit at `$7E:80E0`: speed 2 (`$80E0`, normal 1), 6 bombs
  (`$80E1`), fire 5 (`$80E2`, the HUD shows 6), bomb type 1 = remote control (`$80F3`) and the power glove
  (`$80FE`). A normal code writes speed 1, 1 bomb, fire 0. `$80F0-$80F2` get the same values (the copy that
  comes back after a death).

Verified: all 11 codes typed with real button presses in Mesen 2 (USA), reading `$1A`, `$1C6A`, `$1C68` and the
kit (`tools/sb2/type_code.lua`); `0000` and `4362` rejected. `1111` also loaded in Europe, Japan, the beta
and Caravan with the same kit.

**Fuzz against the game's own check** (`tools/sb2/fuzz.py`): each of the 10,000 codes is written into the
digit buffer and the real routine runs from a savestate taken at its entry; the found (`$CC:19A8`) or
not-found (`$CC:1971`) branch is logged. Results, per ROM:

| ROM | Check at | Codes run | Accepted | Mismatches with `password.py` |
|---|---|---|---|---|
| USA | `$CC:1926` | 10,000 | 11 | 0 |
| Europe | `$CC:1981` | 10,000 | 11 | 0 |
| Japan (En) | `$CC:1915` | 10,000 | 11 | 0 |
| USA beta | `$CC:1926` | 10,000 | 11 | 0 |
| Caravan | `$CC:1ABE` | 10,000 | 11 | 0 |

### Entering a password

Screen setup `$CC:165C`, input loop `$CC:1767`, digit code `$CC:19E0`, cursor code `$CC:1B5A`. Identical in
all five versions.

- **Start value: `0000`, cursor on the first digit.** The digits are copied from `$1C60-$1C66`, which are 0
  after power-on. The game-over/continue screen (`$CC:4216`) writes the current world's password there
  (from the table at `$CC:0000`, index (`$1A` − `$10`) / 16), so after a game over the screen opens with that
  code already in place. Verified in Mesen (USA): `3903`, four deaths, CONTINUE? shows `3903` and `$1C60-$1C66`
  = 3 9 0 3; NO, then PASSWORD opens on `3903` ([img](img/sb2/password_after_game_over.png)) and START plays 3-1.
- **Up adds 1, Down subtracts 1, and both wrap: 9 → 0 on Up, 0 → 9 on Down.** Any pad works (`$7F:402E`,
  all pads). Holding repeats after 36 frames, then every 9.
- **Left/Right move the cursor and stop at the ends** (no wrap from the 4th digit back to the 1st). Holding
  repeats after 36 frames, then every 33.
- **START or A submits** (`BIT #$1080`, any pad). A right code goes on to the stage (or, for `5656`, back to
  the title); a wrong one plays the error sound and resets all four digits to `0000` (and `$1C60-$1C66`);
  the cursor stays where it was. **B** leaves for the title screen.

So any code can be typed with at most 5 presses per digit by choosing Up or Down (e.g. `9564` = Down ×1,
Right, Down ×5, Right, Down ×4, Right, Down ×6).

Verified in all five ROMs with real presses (`tools/sb2/pw_entry.lua`): start `0000`/cursor 0; Down → `9000`;
Up → `0000`; Left on digit 1 and Right ×6 leave the cursor at 0 and 3; Up ×3 then A (wrong code `0003`) →
`0000`, cursor still 3; `9564` typed with Down only and A → accepted, index 3.

### Sudden death (5656)

The hurry-up blocks fall in the order listed at `$C5:E1C9` (cell numbers in the 13 × 11 arena), one every
quarter second, counter `$7E:5D12`. The list has a `$FE` marker after 80 cells, the two outer rings, and
ends at `$FF` after all 143. `$C0:D60C` stops at the marker unless `$1C68` is set, so with `5656` the blocks
keep coming until the arena is full and nobody can survive. Nothing clears `$1C68` but a reset.

Verified in Mesen 2: battle with TIME 1:00 after entering `5656`, block counter skipped from 74 to save time
(`tools/sb2/sudden_death.lua`). With the flag the counter ran 74 → 122 and blocks filled the middle
([img](img/sb2/sudden_death_5656.png)); with `$1C68` cleared again it stopped at 81 with bit 2 of
`$7E:5D0E` set. In a normal round the 80 blocks take 20 s, so the flag only matters if two players outlast the
outer rings; in our unpatched runs a COM won before that.

## GameFAQs codes, checked

| GameFAQs entry | Result |
|---|---|
| Stage 1-5 `4361 6442 3903 9564 7735` | OK, **Known**. "Stage N" = stage N-1 |
| Stage 1-5 (Full Power) `1111 5462 6763 8784 6925` | OK, **Known**. Full power = 6 bombs, fire 6, speed +1, remote, glove |
| Sudden Death Vs. mode `5656` | OK, **Known**. Battle only: the hurry-up blocks fill the whole arena |
| 2 extra battle stages (Joycard turbo + X) | OK, **Known**. Timing pinned down below |
| Jump in battle (A on multitap pad 5) | OK, **Known**. START works too |
| Colour change (Select at player select) | OK, **Known** |

## Hidden tricks and how the game detects them

### Battle stages 11 and 12 (Joycard turbo + X), `$CC:14C0`

Runs every frame on the title menu. `$1CCF` counts frames since the last new X press on **pad 1**
(`$7F:4032` bit `$40`). On each press: if the gap was 7, 8 or 9 frames, `$1CD1` goes up by one, otherwise
both counters reset (also after 32 idle frames). When `$1CD1` reaches 48 the game sets `$1CB5` = `$FFFF`
and plays sound `$0D`. The stage select (`$CC:2399`) then allows 12 stages (`$7F:401E` = `$0B`) instead of
10 (`$09`).

- So it takes 49 presses (the first one only starts the clock), about 6.5 s at 8 frames, matching "hold X
  for six seconds". Nothing checks for a Joycard: any turbo pad, or tapping at 7-9 frames, works.
- Verified in Mesen 2 (`tools/sb2/joycard.lua`): gaps of 7, 8, 9 unlock; 5, 6, 10 don't; 48 presses at 8
  don't, 49 do. Unlocks in all five ROMs. With it, Left on the USA stage select goes 1 → 12 → 11
  ([img](img/sb2/battle_stage11.png)). Stages 11/12 are **Known** (already known via `7E1CCD:0A/0B`).
- ★ New: **the Caravan version kills it.** Its stage select (`$CC:250E` there) writes 0 to `$1CB5` and a
  limit of 4 stages before reading the flag, so the trick sets the flag but the stage list never grows
  (checked: Left goes 1 → 4 → 3, `$1CB5` = 0).

### Jumping in Battle Mode (multitap pad 5), `$CC:1391`

The title menu waits until its delay counter `$1FFE` reaches `$E0` (`$CC:1379`, USA/Europe only), then takes
A or START from any pad (`$7F:402E`, all pads' new presses). If pad 5's own new presses (`$7F:404A`, read
through the multitap at `$CC:7654`) include A or START, `$1C6E` = `$FFFF` (`$CC:13B0`). That holds for any
menu item, not only BATTLE GAME. In battle (`$C0:65F1`) the jump code `$C0:6616`/`$C0:6658` then runs in
every stage except stages 2 and 3; without the flag it runs only in stage 12 (the trampoline stage).
`$1C6E` is never cleared.

Verified in Mesen 2 with an emulated multitap, no RAM writes (`tools/sb2/pad5_jump.lua`): a portable Mesen
whose `settings.json` has `Snes.Port2.Type = "Multitap"`, and A pressed on multitap port D (pad 5) through
`emu.setInput({a=true}, 0, 1, 3)` (in this Mesen build the 4th argument picks the multitap port; the
documented `(input, port, subPort)` form only reaches pads 1 and 2). The game reads it through the multitap
protocol like a real pad. Results, choosing BATTLE GAME:

| Pad pressing A | `$1C6E` | Y in battle stage 1 |
|---|---|---|
| pad 5 (multitap D), USA, Europe, Japan, beta, Caravan | `$FFFF` | player 1 jumps off the screen top, shadow left behind ([img](img/sb2/pad5_jump.png)) |
| pad 4 (multitap C), USA | 0 | nothing |
| pad 1, USA | 0 | nothing |

### Colour select, `$CC:2152`

On the battle player screen SELECT on pad 1-4 steps that player's colour (`$1CB7`, `$1CB9`, `$1CBB`,
`$1CBD`) through 15 values (`$CC:223A`), skipping colours another player already has. Verified: pad 1's icon
went white → pink → green.

## Disabled debug switches

The code has seven `LDA #$0000` / `BEQ`/`BNE` switches. Each is turned on by changing the operand's high byte
to `01`, which is what the known codes do. All seven are at the same address in every version except the
stage-select one in bank `$CC`.

| Switch | Code | Effect | Status | Verified |
|---|---|---|---|---|
| `$C1:00BD` | `C100BF01` | CPU meter: force-blanks for a moment when the frame's work is done, a black line on screen | Known | Mesen: the line shows |
| `$C1:3D26` | `C13D2801` | Y jumps in Normal Game | Known | Mesen: off the ground with a shadow |
| `$C0:22F1` | `C022F301` | R in Normal Game gives everything (`$C0:22A0`) | Known | Mesen: speed 3, 9 bombs, fire 9, remote, kick, glove, both pass items, 144 hearts |
| `$C0:FCAD` | `C0FCAF01` | Normal Game soft reset: pause, hold SELECT, press START (`$C3` = `$3000` exactly) → `$C0:FA48` | Known | Mesen: back to the intro |
| `$C0:FB29` | `C0FB2B01` | the same soft reset in the **Battle Mode** loop `$C0:FB11` | ★ New | Mesen: back to the intro; unpatched, the round goes on |
| `$C1:5B3E` | `C15B4001` | **debug menu** on SELECT in Normal Game (below) | ★ New (only its text was known) | Mesen, all five ROMs |
| `$CC:239F` | `CC23A101` (EU `CC23FC01`, JP `CC239001`) | stage select always offers 12 stages, no `$1CB5` needed | ★ New | Mesen: Left from 1 → 12 ([img](img/sb2/stage_switch_12.png)) |

The Caravan version's stage select has its own switch at `$CC:250E` (`LDA #0` / `BNE` to `$CC:2527`, `LDA #$0B`):
★ New: **`CC251001`** skips both the 4-stage limit and the `$1CB5` clear and allows 12 stages. Verified in Mesen
(Caravan, cheat engine): `$7F:401E` = 11 instead of 3, Left goes 1 → 12 → 11; without the code 1 → 4 → 3.

### The debug menu (★ New)

The menu text (`$C1:6068`, unused font) was already known to be unused. The menu itself is complete. Turn it on with the
PAR code `C15B4001` or the IPS patches `patches/sb2_debug_menu_{us,eu,jp,beta,caravan}.ips` (one byte, ROM
offset `$15B40` = `$01`, the same in all five dumps; built and self-checked by `tools/sb2/make_ips.py`).

Only the Normal Game calls it (`$C0:FD11` → `$C1:5B44`, once per frame); SELECT on pad 1 draws the menu over
the stage and freezes it ([img](img/sb2/debug_menu.png)). Up/Down moves the cursor `$7E:5D50` over nine lines
and wraps (Up on line 1 goes to the last "-"). Right steps the line's value up, Left down; a tap is one step,
holding repeats after 32 frames, then every 4. START closes the menu; that START press also pauses the game,
so press START once more to play on. Handlers come from the table at `$C1:61C4`:

| Line | Effect (Right / Left) | Values, wrap | Verified in Mesen |
|---|---|---|---|
| STAGE NO. | `$7E:5D42`, shown as world-(area − 1). On close, if it differs from `$1A`, `$C0:FD15` sets `$1A` one lower and flags a stage clear (bit `$4000` of `$7E:8002`), so the game moves on to the chosen stage; unchanged = nothing happens | 1-0 ... 1-7, 2-0 ... 5-7, **6-0 = the ending and credits**; Right on 6-0 → 1-0, Left on 1-0 → 6-0 | wraps both ways; 5-6 (→ "5-7 START!"), 5-7 (boss) and 6-0 (ending) warp |
| NO DEATH | Right: hearts `$80EF` = `$90`, Left: 0. A hit only takes a heart while the count is below `$80` (`$C0:A644`), so `$90` never runs out: explosions just flash Bomberman white | OFF/ON | own bomb: OFF dies ("1-1 START!" again), ON flashes white and plays on, `$80EF` stays 144 ([img](img/sb2/debug_no_death.png), top OFF, bottom ON) |
| FIRE | `$80E2`/`$80F2` (the HUD shows value + 1) | 0-9, wraps 9 ↔ 0 | both wraps |
| BOMB | `$80E1`/`$80F1` | 1-9, wraps 9 ↔ 1 | both wraps |
| BOMB TYPE | `$80F3`: 0 normal, 1 remote control, 2 power bomb, 4 spike bomb, 8 a fifth type (below) | Right 0 → 1 → 2 → 4 → 8 → 0, Left back | both directions; a bomb laid with each ([img](img/sb2/debug_bomb_types.png)) |
| ITEM FULL | Right: `$80FA` `$80FB` `$80FE` `$80FF` = 1 (pass items, glove, kick) and speed `$80E0`/`$80F0` = 3; Left: all 0 and speed 1 | OFF/ON | RAM as listed, both ways |
| - (×3) | nothing: the handler `$C1:5DE3` is a bare `RTL` | | Left/Right change no RAM |

Bomb types, from the code and the test (fire 3, a bomb laid between two soft blocks; image rows are types
0, 1, 2, 4, 8): type 0 breaks the first block each way; type 1 never goes off by itself (remote); type 2
looks like type 0 here (it only differs in range, which the blocks hide); **type 4 burns through every soft
block in its range** (the spike bomb); type 8 explodes like type 0. Type 8 gives the bomb a random direction from
`$0408` (`$C0:93A2`, direction at object `+$5E`). ★ New, verified in Mesen (USA 1-1, cheat engine `7E80F308` +
glove `7E80FE01`, bomb thrown down): **a thrown type-8 bomb changes direction on its bounces** (directions
02 02 02 04 04 04 04 04 04 04 10 10 10 02 over 14 bounces, about 180 frames in the air); a type-0 bomb thrown the
same way bounced 4 times, all down (08), then went off. Kicking was not exercised (the kick test never moved the
bomb). Each type has its own item counter (`$80E5` type 4, `$80E6` remote, `$80E7` power,
`$80E8` type 8) and pickup handler (`$C0:9965` sets 4, `$C0:9C19` sets 8).

The known text also lists "NORMAL GAME" and "BATTLE GAME", which this menu never draws.

Verified on the IPS-patched ROMs with no RAM writes (`tools/sb2/debug_menu_check.lua`): TEST=1 walks every line
in all five versions with identical results ([img](img/sb2/debug_menu_nav.png)); TEST=2/3 are the bomb-type
and NO DEATH runs above (USA).

## Unused graphics sweep

Method (`tools/sb2/coverage.lua`, `tools/sb2/unused_gfx.py`): Mesen code/data logs from coverage runs on the
USA ROM, merged: every Normal Game stage 1-1 ... 5-8 warped to with the debug menu, a bomb laid in each, the
ending and credits (route 1); dying to GAME OVER and the continue screen (route 2); Battle Game menus, the
stage-select previews and a few battle stages (route 3, with resets; the script lost its place in some
rounds), plus all the other test runs in this file. Bytes in banks
`$C2-$CF` that no log flags as read, in runs of 4+ tiles, are drawn as 4bpp tiles in a grey ramp; runs that
compress like noise (zlib > 0.75: sound samples, compressed or packed data) are left out.

Result: 153 runs, 4,425 tiles never read, in [sweep_index.txt](img/sb2/unused/sweep_index.txt) and one
labelled sheet per bank (`img/sb2/unused/sweep_bank_C2.png` ... `sweep_bank_CD.png`, addresses on each run).
What they are, as far as checked:

| Where | What it looks like | Status |
|---|---|---|
| `$C5:0D00-$C5:7BBF` (most of it) | enemy sprite frames in 16 × 16 cells, interleaved with frames that were read | candidates only: these are animation frames the short stage visits did not trigger (turning, dying). The known Mr. Moai tongue frames (**Known**) should be among them; not singled out |
| `$C8:40C0-$C8:D8BF`, `$C9:2000-$C9:5F9F` | stage background tile sets | candidates: battle stages 6-12 and some world maps were not covered |
| `$C3:06E0-$C3:39FF`, `$CB:ACE0-$CB:C55F`, `$CD:0000-$CD:0D5F` | not readable as 4bpp (likely 2bpp/8bpp or packed) | unidentified |
| `$C2`, `$C4`, `$CA`, `$CC` runs | mostly not tile art (code tables, sound) | not graphics |

Nothing in the sweep could be confirmed as never-used art, so no ★ New unused graphics are claimed. The known
items are a different kind: they are **loaded but never shown**, which a data log cannot see. The item icon
block `$C8:0002-$C8:0F11` (DMA'd to VRAM `$4000` in every stage) is drawn in
[items_C80002.png](img/sb2/unused/items_C80002.png) (16 × 16 icons, rows of 8). In it are the known unused
clock (row 2, 8th) and question mark (row 2, 7th) (**Known**). The early icon set (fire extinguisher, early
glove, ice cream, spike bomb) and the filler icons were not located. Palettes were not swept.

## Dead code

Method (`tools/sb2/coverage2.lua`, `tools/sb1/sweep.py dead2`, listing `disasm/sb2/dead_usa.txt`): code/data logs of
the USA ROM from portable Mesen copies that never had a ROM-code cheat loaded except the debug-menu switch, merged:
attract mode alone for 9,000 frames; 40,000 frames of random presses on all five pads from the title (menus, battle
setup, battles, password screen); 30,000 frames of random play in Normal Game with deaths, game over and continue;
the debug-menu warp through every stage 1-1 ... 5-8 and the ending (`tools/sb2/map_dump.lua`); a SNES Mouse run;
and the earlier `coverage.lua` routes (stages, game over, battle stages; their logs were dumped one byte early and are
shifted back when loaded). 115,233 bytes of code ran. Because the debug menu was used, its code counts as run here
(it is documented above).

- **Reachable, not covered:** 581 places (32,822 bytes) where a conditional branch in code that ran leads to code
  that did not: rare enemy, boss and battle cases (the largest, `$C0:6A30` and `$C0:C56B`, are battle-player code
  for situations the random play never produced).
- **Islands:** 94 runs of plausible code no code that ran leads to (19,050 bytes). 68 of them are referenced by a
  24-bit pointer, a 16-bit table entry or an `LDA #addr` object-state load: object handlers of enemies, bosses and
  battle items that the runs did not trigger (for example `$CC:CC4B`, 1,559 bytes, the state a battle-result object
  enters after `$CC:CBE1`). **26 (2,394 bytes) have no reference of any kind:**

| Address | Bytes | What it does | Class | Status |
|---|---|---|---|---|
| `$C0:0E9B`, `$C0:0EDB` | 145 | pad 1 R adds `$0400`, L subtracts `$0200` from every entry of the line-scroll tables `$7E:393C` / `$7E:3730`; `$C0:0EDB` sets HDMA channel 2 on BG1's horizontal scroll from `$C5:FD57` (the copy routine `$C0:0E88` is the only part still called). A raster-scroll test | debug feature | ★ New |
| `$C0:0C5F` | 75 | a second init path: force blank, the boot init calls (`$C0:209F`, `$C0:0F2C`, `$C0:211A`, `$C0:F60E`, `$C0:159E`, `$C0:096C`), then a frame wait loop | unreferenced | ★ New (minor) |
| `$CC:C1AE`, `$CC:A440` | 395, 238 | two object routines in the menu/ending bank using the animation tables `$CC:A831`/`$CC:A83D`; `$CC:A440` starts with two `NOP`s, where a call was removed | cut (not identified) | ★ New (minor) |
| `$C0:F339`, `$C0:20D2`, `$C0:1382` | 27, 40, 28 | clear VRAM `$8000-$9FFF`, upload `$7E:2200` to OAM by CPU, copy two palette rows from `$C1:DB3E`: helpers superseded by DMA versions | unreferenced | |
| `$C0:35C3`, `$C1:81FC`, `$C0:BE1F`, `$C0:693A` ... | 27-158 | map-cell and collision helpers on the player struct (`[$6A]`, `[$7C]`), e.g. `$C0:35C3` turns a cell of type 1 into `$43` | unreferenced helpers | |

Europe, Japan, beta and Caravan have the same islands at their shifted addresses (byte search); their own coverage
was not run.

## Unset flags

`tools/sb1/sweep.py flags` with the logs: 21 RAM addresses tested by code that ran but never written by code that ran.
Most are fields of the player structs at `$7E:8000`+`$100`·n (`+$52`, `+$A8`, `+$F5`) and the object area at
`$1000`, which the game writes through `[$6A],Y` / `$xx,X`, so the static check cannot see the writes. A write watch
(`tools/sb1/flagwatch.lua` on a random-play run) confirmed `$7E:80A8` (6,853 writes), `$7E:8152`, `$7E:85A8`, `$1026`,
`$1036` are all written. What remains:

| Address | Tested at | Written by | Result | Status |
|---|---|---|---|---|
| `$1CB5` | `$CC:23AB` | only the turbo-X code `$CC:1505` | stages 11/12 | Known |
| `$1C76` | `$CC:96C4` | only never-run object code (`$CC:96D4`, `$CC:CC50`) | part of the uncovered battle-result object above | |

No debug or invincibility switch is hidden behind an unset RAM flag; SB2's switches are the `LDA #0` constants in
ROM (Disabled debug switches).

## Maps

SB2 has no separate arena format: each stage's background tilemap is unpacked to `$7F:E000`, and `$C0:F71B` turns it
into a collision map at `$7F:C000` through the stage's tile-attribute table (`[$7C]`), one word per 8 × 8 tile; the
code of a 16 × 16 cell is at word y·64 + x. `tools/sb2/map_dump.lua` warps through every Normal Game stage with the
debug menu (cheat engine, NO DEATH on) and dumps that buffer plus a screenshot; `tools/sb2/maps.py` draws it
(`docs/img/sb2/maps/map_<stage>.png`, collision grid left, the game right; `sheet.png`). Codes: `$00` floor, `$C2`
soft block, `$C5`/`$C6` walls, others special floors. 41 maps: 1-1 ... 5-8 and the ending ($60). The grid is the
whole stage buffer, so on taller stages it does not line up with the visible screen.

Every stage the debug menu offers was reached (1-0 ... 5-7, 6-0); its STAGE NO. wraps at 6-0, so there is no stage
index beyond the 40 stages and the ending. Battle stages were not dumped: the scripted way through the battle menus
lost its place (stage select reached, battle not started). No cut stage was found, but unreferenced stage data could
not be searched for, since the tilemaps are compressed.

## Cheat codes

Checked with Mesen's cheat engine (`emu.addCheat`) on the unpatched USA ROM, real presses only (`tools/sb2/cheats.lua`,
`tools/sb2/cheats.sh`): `4361` typed on the password screen, a bomb laid under player 1. All in `sb2_codes.json`
(`section: "cheat"`); RAM codes apply to every version (same RAM map), only USA was run.

| Code | Effect | Check | Status | Game Genie (same test, all versions listed) |
|---|---|---|---|---|
| `7E80EF90` | invincible in Normal Game (144 hearts that never drop, the debug menu's NO DEATH) | own bomb: flashed and played on; control run died | ★ New | `0C67-E70D` `6767-E76D` `D8C9-8D0F` `D806-5D00` `5191-54D9` `9991-5409`: the three no-heart hit branches go to the heart-loss flash; own bomb: played on, all five ROMs |
| `7E80E003` `7E80E109` `7E80E209` | speed 3, 9 bombs, fire 9 | RAM | ★ New | none: read at about 20 places, set only at game start and by pickups |
| `7E80F304` | spike bombs (`01` remote, `02` power bomb, `08` the fifth type) | RAM | ★ New | `CB7D-54AF` `D07D-57DF` (`$C0:350B` type load → `LDA #$04`): new bombs get type 4, all five |
| `7E80FA01` `7E80FB01` `7E80FE01` `7E80FF01` | both pass items, power glove, kick | RAM | ★ New | none built (four separate tests) |
| `7E1CB5FF` `7E1CB6FF` | battle stages 11 and 12 (not in Caravan) | Left on the stage select: 1 → 12 | ★ New (`7E1CCD0A/0B` was known) | `DD48-ED7D` (Europe `DD4D-74EF`, Japan `DD4B-E7ED`): the `$1CB5` test `BEQ +0`; 1 → 12, all four |
| `7E1CCD0A` / `7E1CCD0B` | battle stage 11 / 12 | stage select shows 11 / 12, the battle is the boxing ring / trampolines | **Known** | none (no ROM form built) |
| `7E1C6EFF` `7E1C6FFF` | jump in battle (the pad-5 flag) | flag held; jump shown earlier with the same flag | ★ New | `DD1E-5F6F` (the `$1C6E` test `BEQ +0`): the jump handler runs in stage 1, all five |
| `7E1C68FF` `7E1C69FF` | sudden death (the `5656` flag) | flag held; effect shown earlier | ★ New | `DD2F-8F6F` (Caravan `DD24-8F0F`; the `$1C68` test `BEQ +0`): hurry-up blocks keep coming past 81 (`sudden_death.lua`, flag cleared), USA, Europe, Japan, beta |

The ROM switch codes (debug menu `C15B4001`, soft resets, CPU meter, R power-ups, Normal Game jump, 12 stages) are
listed under Disabled debug switches.

## Input codes

`tools/sb1/sweep.py pads` (shared with SB1; listing `disasm/sb2/pads.txt`) looks for rhythm windows (a frame
counter checked against two bounds, then a press counter), held combinations (`AND #m` / `CMP #m`, 2+ buttons),
sequence tables (compare against a table indexed by a RAM counter) and every test of a fixed pad. Run on USA,
Europe, Japan, beta and Caravan (each disassembly grown from that version's code/data logs, `disasm/sb2/<ver>`):

| Hit | What | Status |
|---|---|---|
| `$CC:14E6` (EU `$CC:1541`, JP `$CC:14D5`, Caravan `$CC:167E`) | the turbo-X rhythm (gap 7-9 frames, counter `$1CD1`): stages 11/12 | Known |
| `$CC:13A4` | pad 5 A/START on the title menu: battle jump | Known |
| `$CC:2154`-`$CC:21B4` | SELECT on pads 1-4 at the player screen: colours | Known |
| `$C0:FB30`, `$C0:FCB4` | `$C3` = SELECT+START exactly: the two disabled soft resets | Known / ★ New (above) |
| `$C0:0E9B` | pad 1 R / L shift the HDMA scroll tables `$7E:393C` / `$7E:3730` (+`$0400` / −`$0200` per frame); never called (see Dead code) | ★ New |
| `$C1:0A12`-`$C1:0B51` | each pad's START pauses Battle Mode; `$FFFF` (no pad) skipped | ordinary |
| `$C1:13F2` ... (`#$2800`), `$C0:DF72`, `$C1:1FF9`, `$C1:C069` | player-struct flags and map counters, not pads | false hits |

Same hits at shifted addresses in all five versions. There is no password-style or button-sequence code beyond the
password table.

## Text

The game has two encodings: ASCII for the ending credits (`$CC:81F1`-`$CC:84E4` USA) and the debug font for the
debug menu (letters `$01-$1A`, digits `$20-$29`, space `$2A`, `-` `$34`, each followed by an attribute byte;
`tools/sb2/textmap.py` for `tools/sb1/text.py`). Everything else on screen (story, menus, PASSWORD, stage cards) is
graphics. Listing: `disasm/sb2/text_usa.txt`.

| Address | Text | Shown | Status |
|---|---|---|---|
| `$C1:6064` | NORMAL GAME, BATTLE GAME, STAGE NO. 0-0, NO DEATH OFF, FIRE 0, BOMB 0, BOMB TYPE 0, ITEM FULL OFF, -, 0123456789 ONOFF | the menu lines only with the debug switch; NORMAL GAME and BATTLE GAME never | Known |
| `$CC:81F1`-`$CC:84E4` | credits: Game Planner, Graphics Designers, Programmers (TETUROU KIYOMOTO, B.HANAWA, TOSHIYUKI SUZUKI), Sound Producers, Sound Director, Composer, Sound Designer, Special Thanks, Director KYON KYON, Super Producer RAOH SHIMADA, HUDSON SOFT | yes (ending) | |
| JP `$CC:843D`-`$CC:85B0` | "Special thanks to all our friends for giving us these names:" PLASMA BOMBER (Akihiro Nishida and 3 other kids), MAGNET BOMBER (Tatsuya Shirai and 63), BRAIN BOMBER (Yoshinao Kawai and 4), **PRETTY BOMBER (Kazuma Asakura and 21), GOLEM BOMBER (Hirokazu Takada and 2)** | yes (JP and Caravan only; not in USA/EU/beta at all) | Known |

No string is left over that no code displays, apart from the two debug-menu headings. No Japanese text in any
version (the Japanese release is the "(En)" dump).

## RAM

| Address | Meaning |
|---|---|
| `$1A` | Normal Game stage (`$WA`: world, area − 1); in battle, the battle stage index |
| `$C3` | pad 1 held (16-bit) |
| `$1C68` | sudden-death flag (5656) |
| `$1C6A` | password index 0-10 |
| `$1C6E` | battle jump flag (pad 5) |
| `$1CB5` | battle stages 11/12 unlocked |
| `$1CB7-$1CBD` | battle colours, players 1-4 |
| `$1CCD` | chosen battle stage (0-11) |
| `$1CCF`, `$1CD1` | turbo-X frame counter and press count |
| `$1FFE` | title-menu delay counter (USA/Europe) |
| `$7E:5D0E`, `$7E:5D12` | hurry-up flags, block counter |
| `$7E:5D40-$5D52` | debug menu state |
| `$7E:5E04/06/08` | battle clock digits (min, tens, ones) |
| `$7E:80E0` (+`$100` per player) | speed `E0`, bombs `E1`, fire `E2`, hearts `EF`, bomb type `F3`, `FA`/`FB` pass items, glove `FE`, kick (likely) `FF`; `F0-F2` saved copy |
| `$7F:0028-$7F:0032` | password digits, result, cursor |
| `$1C60-$1C66` | digits the password screen starts with (0 at power-on; set by the continue screen) |
| `$CD-$D1` | controller ID per port (pad = 1, mouse: `AND #$1E` = 2), from `$C0:1797` |
| `$7E:5E14` | battle clock frame counter (0-`$40`, one clock second = 65 frames) |
| `$7E:80E5-$80E8` | bomb-type item counts: spike, remote, power, type 8 |
| `$7F:402E`, `$7F:4032/38/3E/44/4A`, `$7F:4034` | new presses: all pads, pads 1-5; pad 1 held |

Item names: `$C0:22A0` (the known "power-up toggler", whose list is remote, bomb-through, wall-through, kick,
throw) sets `$F3` = 1 and `$FA` `$FB` `$FE` `$FF`. The pickup handler `$C0:9BF6` sets `$FE` and holds the
power-glove sound byte already pointed out (`0x9BF7`), and `$C0:9C3A` (sound byte `0x9C3B`, power bomb) sets bomb
type 2. `$FF`'s pickup `$C0:9BA8` plays sound `$61` instead of the usual `$4C`, likely the "Kick" voice.
Which of `$FA`/`$FB` is bomb pass and which wall pass wasn't checked.

## Versions

- **Passwords:** the same 11 codes, same table at `$CC:0000`, same check, same effects in all five
  (fuzzed above).
- **USA beta** (★ New, listed as to-do before): it is the retail game with three letters missing. The credits
  say "Graphics Designer", "Programmer", "Sound Producer" (singular, like the Japanese version); retail adds the
  "s". Those 3 bytes (`$CC:8234`, `$CC:828A`, `$CC:82E3`) shift the rest of bank `$CC` by 1-3, which explains
  every other byte that differs except one 10-byte tilemap row at `$C7:C4CD` (two tiles moved one place,
  again as in the Japanese version) and the header checksum. Checked by realigning bank `$CC` around the
  three bytes: no other difference. No unique content, same passwords and switches.
- **Japan (En):** credits have the "Special thanks ... kids" block and singular titles (**Known**).
  No `$1FFE` menu delay (**Known**). The logo has no "TM" (see below).
- **Europe:** credits and logo as USA. Bank `$CC` has `$5B` extra bytes: `LDA #0 / STA $7F:4004` at
  `$CC:015B` and a block in front of the title menu (`$CC:1364`) that checks the controller ID of all five
  ports (`$CD-$D1`, built from `$4218-$421F` and `$4016/$4017` at `$C0:1797`; `AND #$1E` / `CMP #$02` = a
  SNES Mouse). If any port holds a mouse it jumps to `$CC:13AE`, which skips the menu, so the title menu
  never accepts input (below).
- **Caravan** (**Known**: sponsor screens, locked battle settings, 4 stages, hurry-up at 1:00): Normal
  Game and the password screen still work with all 11 codes; the debug switches are the same. New: it clears
  `$1CB5` at the stage select, so the Joycard trick does nothing (above).

### Region comparison, screen by screen

US vs Europe vs Japan (En) vs Caravan, same presses on each (`tools/sb2/region_tour.lua`, ROUTE 0-3), plus a
byte comparison: every 32-byte block of each ROM was looked up anywhere in the USA ROM, so moved data counts
as the same. Outside bank `$CC` (code, shifted, so every pointer into it differs) and the header, Europe has
no new data at all, Japan only the title/credit pieces below, Caravan its sponsor screens and battle-lock code.
Images: [title and password](img/sb2/region_title_password.png) (rows US, EU, JP, Caravan),
[battle menus and clock](img/sb2/region_battle.png).

| Screen | USA | Europe | Japan (En) | Caravan | Status |
|---|---|---|---|---|---|
| Header | `SUPER BOMBERMAN2`, region 1 | region 2 | region 0 | `SUPER BOMBER2 CARAVAN`, region 0 | ★ New (not in the prior art) |
| Power-on to intro | intro | intro | intro | 2 sponsor screens first | Known |
| Intro length (frames until the title menu polls input, no buttons) | 2506 | 2453 (41.8 s at 60 Hz in the US, 49.1 s at 50 Hz here) | 2282 | 2834 | ★ New (measured) |
| Title logo | "TM" | "TM" | no "TM" | no "TM" | Known (see Logos) |
| Title bottom lines | "TM & © 1994 HUDSONSOFT" / "Licensed by Nintendo" | same as USA | "© 1994 HUDSON SOFT", no Nintendo line (tilemap `$C7:C4CD` and `$CB:E822`/`$CB:EB32` blanked) | as Japan | ★ New |
| Title menu delay | `$1FFE` counts to 224 | same | no counter | no counter | Known (published as 253 and 31 frames) |
| Title menu with a SNES Mouse plugged in | works | **locked**: START/A do nothing, `$1FFE` stays 0 ([img](img/sb2/eu_mouse_title.png), left USA, right Europe) | works | works | ★ New |
| Password screen title | "PASSWORD" | "PASSWORD" | "PASS  WORD" | "PASS  WORD" | ★ New |
| Password entry, codes | same | same | same | same | (above) |
| Normal Game: story, "1-1 START!" card, HUD, 4:00 timer | same | same | same | same | checked to 10 s in |
| Battle: type, players, settings, stage select | same | same | same | type and settings skipped, settings locked, 4 stages | Caravan Known |
| Battle clock | 2:00, one clock second = 65 frames (`$C1:1C39`, `CMP #$0040`) | same code: not adjusted for 50 Hz, so a clock second takes 1.3 s and a 2:00 round 2 min 36 s | same | same; hurry-up at 1:00 | ★ New (PAL timing); Caravan Known |
| Battle stages 11/12 (Joycard) | yes | yes | yes | no (`$1CB5` cleared) | see above |
| Credits | plural titles | as USA | "Special thanks ... kids" block, singular | as Japan | Known |
| Music | reference | all data outside bank `$CC` byte-identical (moved only); not compared by ear | identical | identical | checked statically only |

Clock check: 600 frames after the battle starts the clock shows 1:51 (USA, JP) / 1:50 (EU, 17 frames
ahead); 3,600 frames in, 1:05 / 1:04: 55 clock seconds in 3,600 frames in all three.

## Logos

`docs/img/logos/sb2_us.png` (USA, Europe and the beta are pixel-identical) and `sb2_jp.png` (Japan and
Caravan: the same logo without "TM"). Made by `tools/sb2/logo.py`: boot in Mesen, dump VRAM/CGRAM/PPU
state once the title menu polls input, draw BG1 (mode 1, 16 × 16 tiles) from the real tiles and palette with
colour 0 transparent, crop to the logo above the menu text, save as an indexed PNG (253 × 122).

## Tools (`tools/sb2/`)

| File | Use |
|---|---|
| `password.py`, `password.mjs` | encode/decode/validate (no dependencies); `python password.py` lists and self-checks |
| `fuzz.py` | runs all 10,000 codes through the game's own check in Mesen |
| `run.py` | runs a Lua test on any version: finds addresses by pattern, adds `title()` and `pw()` |
| `type_code.lua`, `joycard.lua`, `debug_menu.lua`, `sudden_death.lua` | the Mesen checks above |
| `make_ips.py` | builds `patches/sb2_debug_menu_<ver>.ips` from the five ROMs, checking the switch bytes first |
| `debug_menu_check.lua`, `debug_menu_all.lua` | debug-menu checks (the first runs on the IPS-patched ROM, no RAM writes) |
| `pad5_jump.lua` | multitap jump trick with an emulated multitap (`PAD=5`, controls `PAD=4`/`PAD=1`) |
| `pw_entry.lua` | password screen controls |
| `region_tour.lua`, `mouse_title.lua` | region comparison screens; Europe's mouse lock (needs a Mesen with a mouse in port 2) |
| `coverage.lua`, `unused_gfx.py` | code/data-log coverage runs and the unused-graphics sweep |
| `coverage2.lua` | coverage runs for the dead-code sweep (attract mode, random play on five pads, Normal Game deaths) |
| `../sb1/sweep.py` | shared: `dead2` (never-run code), `pads` (input-code scanner), `flags` (tested, never written), `show` |
| `../sb1/text.py`, `textmap.py` | string dump with the debug-font map |
| `map_dump.lua`, `maps.py` | collision-map dump of every stage and its render |
| `cheats.lua`, `cheats.sh` | PAR checks through Mesen's cheat engine |

All Mesen runs use a portable copy (its own `settings.json` next to `Mesen.exe`, so its data folder is its
own); `MESEN` points at it. The multitap runs need `Snes.Port2.Type = "Multitap"` in that `settings.json`
(or `--snes.port2.type=Multitap` on the command line).
| `logo.py`, `bgrender.py` | logo rip; mode-1 BG layer renderer |
| `cdl2entries_hirom.py` | HiROM version of `tools/cdl2entries.py`, also seeds jump targets and sub entries |
