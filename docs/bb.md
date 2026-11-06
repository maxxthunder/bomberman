# Atomic Punk / Bomber Boy (Game Boy, 1990-91): passwords

Bomber Boy (Japan, 1990) and Atomic Punk (USA, 1991) are one game. Read from the ROMs and checked in Mesen 2 (helpers in
`tools/bb/lib.lua`, `CODE=... tools/emu/run.sh bb tools/bb/test_codes.lua us|jp`). Addresses are the same in both carts
unless two are given (US / JP).

Prior art: the GameFAQs "Atomic Punk" page (in `res/`). Marks: ★ **New**, **Known**.

| Dump | Header title | MD5 |
|---|---|---|
| Atomic Punk (USA) | `ATOMIC PUNK` | `76010c6ff6bd0c4e8ac934dc69fb96ab` |
| Bomber Boy (Japan) | `BOMBER BOY` | `fc2d9eb9479543614b6e3d0d63c359aa` |

128 KB each. The title menu offers GAME A / BOMBER BOY (the adventure), GAME B / BOMBER MAN and VS. MODE; Game A and
Game B each have their own password screen.

![Atomic Punk title](img/bb/title_us.png) ![Bomber Boy title](img/bb/title_jp.png)

## Game A (Bomber Boy): 8 characters

CONTINUE opens INPUT PASSWORD: a grid of 32 places, 8 characters, END to check. `tools/bb/password.mjs` decodes and
encodes; `node tools/bb/test_password.mjs` round-trips every state.

| Cart | Grid (rows of 8) |
|---|---|
| Bomber Boy | `12345678` `ABCDEFGH` `JKLMNOPQ` `RSTUWXYZ` (no I, V, 9 or 0) |
| Atomic Punk | `12345678` `BCDFGHJK` `LMNPQRST` `VWXZ?!.=` (no vowels) |

The code stores each character's place, so the same state has a different code on each cart.

- The buffer `$C480-$C487` holds each character's place (0-31). `$01:44B2` / `$01:4497` turns it sideways: byte k
  (`$C490 + k`) gets bit k of every character, the first character in bit 7. Bytes 5-7 must be 0, which they always are.
- **Checks**: b1 + b2 + b3 = b0 and b1 ^ b2 ^ b3 ^ `$CA` = b4. ERROR !! otherwise.
- **Contents**: b1 → `$C0E9`, the islands cleared (one bit each); b2/b3 → `$C0E0`/`$C0E1`, the gold. That is all a
  code holds, so every state has exactly one code, and 1 string in 65,536 is valid.
- The game's own encoder (`$01:4670` / `$01:4655`, for the CONTINUE screen, from the copy kept at `$C9A0`) makes the
  same characters: with islands `$5A` and 9,999 gold it showed `K3RMPEGE` (Bomber Boy) and `M3VPSGJG` (Atomic Punk),
  as `password.mjs` does.

| Bit | Island | | Bit | Island |
|---|---|---|---|---|
| 0 | Cuolece | | 4 | Jagoraz |
| 1 | Windria | | 5 | Grad |
| 2 | Thulia | | 6 | Faria |
| 3 | Hevol | | 7 | Wather |

Names from `$00:0F79`; My Town, the hub you start on, has no bit. A new game is islands 0, gold 100 (`$00:08E2`).

- **Gold is 16 bits but capped at 9,999** (`$00:34E6`, `$00:379D`: past `$270F` it is set back to 9,999). The password
  takes any value up to 65,535 (`!!HH!H!G` loads 65,535); the cap applies the next time gold changes.
- **Faria is the last island**: it opens once the other seven are cleared (`$00:0EB7`, mask `$BF`).
- **All eight cleared goes to the ending** (`$00:0CA5`: `$FF` jumps to bank 3). `33FPS=J=` / `33DMPZGZ` play the
  closing scene and BOMBER BOY STAFF instead of opening the map; `$BF` opens the map. ![The ending from 33FPS=J=](img/bb/ending_us.png)

Typed in Mesen (RAM read back after END; the cards show the island map and the Panel Shop's GOLD): every Atomic Punk
code on the GameFAQs page, its US and "EU" lists alike, loads the islands and gold it decodes to. Two entries there are
misprints: `6M71L2B` has 7 characters, and `35QQB6CA` an A the grid doesn't have. The page's labels ("Hevol
Completed" and so on) name the last island its contributor cleared; the codes hold every island cleared so far.

## Game B (Bomber Man): NES Bomberman's code

Game B is a port of NES Bomberman, and its ENTER SECRET CODE screen is NES Bomberman's code system unchanged: the
letter chain v[k] = (l[k] + l[k-1] + 7) & 15 (`$02:451D`) and the same sum checks. `tools/nes1/password.mjs` covers it.

Bomber Boy's letters are NES Bomberman's (`ABCDEFGHIJKLMNOP` / `AOFKCPGELBHMJDNI`). Atomic Punk's table (`$02:44D5`)
is `0BCD1FGH2JKLMN3P` / `03FKCPG1LBHMJDN2`: the same letters with **A, E, I and O shown as 0, 1, 2 and 3**. So any NES
Bomberman code works on Atomic Punk with those four letters swapped.

Only the RAM moved: stage `$C40B`, bombs `$C402`, fire `$C403`, speed `$C404`, wall pass / flame pass / detonator
`$C406`-`$C408`. Typed in Mesen and read back: `BOHIDJFEKJGKEFOLFHAC` (Bomber Boy) and `B3H2DJF1KJGK1F3LFH0C`
(Atomic Punk) both start stage 50 with 10 bombs, fire 5 and every power-up, and `NM2HPPBPC0FH0BDPCPCH` (Atomic Punk)
stage 1 with 10 bombs, fire 5 and speed. The 20th letter submits the code.

## Button codes

- **Sound test** (Known): on Game A's stage select, choose MY TOWN with A + B + Select + Right held, and keep them held
  through the fade. `$00:2A95` checks for exactly that combination (`$17`) and jumps to the sound test (`$03:471A`).
  Typed in Mesen on both carts. ![Sound test](img/bb/sound_test_us.png)
- ★ **Soft reset**: hold Start and press Select. The joypad reader (`$00:04D7`) jumps back to the boot code (`$0179`);
  the bytes are the same in both carts, and both were tested in Mesen.
- No password check reads the joypad, so no code needs buttons held while it is entered.

