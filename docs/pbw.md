# Super Bomberman: Panic Bomber W (Super Famicom, Japan, 1995): passwords

Read from the ROM and checked in Mesen 2. The cart is SA-1 (map mode `$23`): the game's variables live in the SA-1's
I-RAM (`$00:3000-$37FF`), not in work RAM. Prior art: the GameFAQs "Super Bomberman: Panic Bomber W" page (in `res/`).
Marks: ★ **New**, **Known**.

| Dump | Header title | MD5 |
|---|---|---|
| Super Bomberman - Panic Bomber W (Japan) | `PANIC BOMBER WORLD` | `cc9c8195b55b94e075c771ca1628cbc8` |

![Title](img/pbw/title.png)

## The password

ストーリーモード → パスワード: four digits (Up raises a digit, Right moves on), then A. The code is looked up in a list
of 4-digit records at file `$4AB5` (`$00:CAB5`), one row of 8 per difficulty:

| Difficulty | Round 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Easiest | `0001` | `1706` | `2158` | `7839` | `0285` | `1694` |
| Easy | `0002` | `3248` | `2516` | `0927` | `1439` | `6218` |
| Normal | `0003` | `7154` | `1386` | `2473` | `4890` | `3105` |
| Hard | `0004` | `5746` | `9510` | `4715` | `6532` | `1974` |
| Hardest | `0005` | `9650` | `3825` | `7431` | `5792` | `0819` |

- Each row ends with its round-1 code twice more; the Hardest row's last slots hold the character codes (`1993`,
  `5656`, `8111`, `4622`) and the L+R codes (`2200`, `4404`, `3445`, `0901`, `5963`).
- Every round code was typed in Mesen and starts its round. The round-1 codes `0001`-`0005` are not on GameFAQs;
  the rest of its list is complete and correct.
- The character codes are taken (the screen returns to the Story menu), and in a new Story game the falling pieces
  become baby Bombermen, balloons, Funya or Takahashi Meijin (watched in Mesen).
- With L and R held, typed in Mesen: `3445` sound test, `0901` stage select, `5963` the ending; `2200` and `4404` are
  taken (their rule changes, bombs exploding at once and four bombs to clear a line, are GameFAQs'). Without L and R
  the cheats are refused.

## ★ Warning screens

The boot code (`$80:E54B`) checks the console before the title. On a PAL console (`$213F` bit 4) it shows "This Game
pak is not designed for your SUPER FAMICOM or SUPER NES." on a yellow screen; with a SNES Mouse in either port (device
ID 1) it shows "You can not use a mouse with this Game." Both seen in Mesen (region PAL; a mouse in port 2). A patch at
file `$6585` (`D0` → `80`) skips the check. ![PAL](img/pbw/pal_warning.png) ![Mouse](img/pbw/mouse_warning.png)

The character-swap codes set `$37CC` to 1-4; its table (`$80:8D93`) has two more slots, which give a black or garbled
board. Table slots 6-7 of each row and the last `0005` repeat earlier codes, so they can never be reached.

The PC Engine Super CD-ROM² version (Bomberman: Panic Bomber, 1994) has no password: it saves to the System Card's
backup memory instead. Its Story mode goes straight to the difficulty choice; the save routine near the start of the
data track calls the System Card's backup-memory functions with the file name `P.BOMBER` and a 166-byte buffer, and
after one boot in Mesen the backup memory holds that file.
