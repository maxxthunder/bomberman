# Super Bomberman: Panic Bomber W (Super Famicom, Japan, 1995): passwords

Read from the ROM and checked in Mesen 2. Prior art: the GameFAQs "Super Bomberman: Panic Bomber W" page (in `res/`).
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

The PC Engine Super CD-ROM² version (Bomberman: Panic Bomber, 1994) has no password: its Story mode goes straight to
the difficulty choice.
