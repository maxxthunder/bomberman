# Atomic Punk / Bomber Boy (Game Boy, 1990-91): passwords

Bomber Boy (Japan, 1990) and Atomic Punk (USA, 1991) are one game. Bomberman Selection (Korea) carries Bomber Boy
too, and its notes ([sel.md](sel.md)) hold the full password write-up; everything there applies to these carts. Checked
in Mesen 2 with the helpers in `tools/sel/lib.lua` (the menus differ only in naming).

Prior art: the GameFAQs "Atomic Punk" page (in `res/`). Marks: ★ **New**, **Known**.

| Dump | Header title | MD5 |
|---|---|---|
| Atomic Punk (USA) | `ATOMIC PUNK` | `76010c6ff6bd0c4e8ac934dc69fb96ab` |
| Bomber Boy (Japan) | `BOMBER BOY` | `fc2d9eb9479543614b6e3d0d63c359aa` |

128 KB each. The password check (`$01:44B2` US, `$01:4497` JP) is byte for byte the one in Selection, at the same RAM:
islands cleared in `$C0E9`, gold in `$C0E0`/`$C0E1`. `tools/sel/password.mjs` takes the grid as a parameter.

![Atomic Punk title](img/bb/title_us.png) ![Bomber Boy title](img/bb/title_jp.png)

## Game A (Bomber Boy): 8 characters

The entry grid has 32 places; the code stores each character's place, so the two grids give different codes for the
same state:

| Cart | Grid (rows of 8) |
|---|---|
| Bomber Boy | `12345678` `ABCDEFGH` `JKLMNOPQ` `RSTUWXYZ` (no I, V, 9 or 0, as Selection) |
| Atomic Punk | `12345678` `BCDFGHJK` `LMNPQRST` `VWXZ?!.=` (no vowels) |

Typed in Mesen (RAM read back after END): every Atomic Punk code on the GameFAQs page, US and "EU" lists alike, loads
the islands and gold it decodes to; two entries there are misprints (`6M71L2B` has 7 characters, `35QQB6CA` an A the
grid doesn't have). The page's labels ("Hevol Completed" and so on) name the last island its contributor cleared; the
codes hold every island cleared so far. All eight islands cleared (`33FPS=J=`, `33DMPZGZ`) goes straight to the
ending, as in Selection. ![The ending from 33FPS=J=](img/bb/ending_us.png)

## Game B (Bomber Man): NES Bomberman's code

Game B is NES Bomberman: the 20-letter code system unchanged (the letter chain at `$02:451D` in both). Bomber Boy's letter table is `ABCDEFGHIJKLMNOP` / `AOFKCPGELBHMJDNI`; Atomic Punk's is
`0BCD1FGH2JKLMN3P` / `03FKCPG1LBHMJDN2` (`$02:44D5`): the same letters with **A, E, I and O shown as 0, 1, 2
and 3**. So any NES Bomberman code works on Atomic Punk with those four letters swapped. Typed in Mesen:
`BOHIDJFEKJGKEFOLFHAC` (Bomber Boy) and `B3H2DJF1KJGK1F3LFH0C` (Atomic Punk) both start stage 50 with 10 bombs,
fire 5 and every power-up.
