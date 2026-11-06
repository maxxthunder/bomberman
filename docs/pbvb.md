# Panic Bomber (Virtual Boy, USA, 1995): passwords

Read from the ROM and checked in BizHawk (Virtual Boyee core, left eye only: `vb.anaglyph.preset` = disabled). Prior
art: the GameFAQs "Panic Bomber" (Virtual Boy) page (in `res/`). Marks: ★ **New**, **Known**.

| Dump | MD5 |
|---|---|
| Panic Bomber (USA) | `467247d5e3383d066005565bf8218436` |

![Title](img/pbvb/title.png)

## The password

PASSWORD on the main menu: four digits (Up raises a digit, Right moves on), then A. There is no algorithm: the code is
looked up in a list of 4-digit records at ROM `$27DFE` (`$0702_7DFE`):

| Rows | Codes |
|---|---|
| Very Easy | `1000` `4390` `3281` `5607`, then `1000` four times |
| Easy | `2000` `6835` `9081` `2473`, then `2000` four times |
| Normal | `3000` `2695` `1038` `6934`, then `3000` four times |
| Hard | `4000` `8647` `0538` `9316`, then `4000` four times |
| (after the levels) | `9782` `1298`, then `1000` four times |
| with L and R held | `0612` `0130` `1001` `0720` `0716` `0911` `0704` `4476` `0825` `0513` |

- The four columns are the stages: **The Scary Ruins** (stage 1), **The Sinister Forest**, **Desert of Desolation**
  and **Doom Castle**. `d000` is stage 1 of level d; the four slots after Doom Castle repeat it, so a code for a
  later stage never comes up.
- Every level and stage code was typed in BizHawk and starts its stage (the stage card names it).
- GameFAQs has most of them, under shifting labels: the Very Easy row is filed under Normal as "Star/Moon/Sun Medal",
  the Hard row appears twice (as stages and as medals), and `4000` "The Scary Ruins" is Hard stage 1. The Very Easy
  row and `1000`, `2000` and `3000` are not on its page.

## Special codes

The decoder (`$0701_FFDC`, from the MAME `unidasm` V810 listing) walks all 48 entries and returns the first match;
entries 38-45 also need L and R held (`$0702_00D0`, pad copy `$0500_2510`), and entries 46-47 L, R, Up on the right
pad and Left on the left pad (`$0702_00F0`). The handlers start at `$0702_01EC`. Typed in BizHawk unless marked.

| Code | Hold | Effect |
|---|---|---|
| ★ `1298` | | pick a level, then THE SCARY RUINS against **Zach the Were-Bomberman** instead of Drifty ![](img/pbvb/zach_1298.png) |
| ★ `9782` | | sets `$0500_24F4`: every game uses piece set (TUBU) 5 ![](img/pbvb/other_pieces_9782.png) |
| `0130` | L R | auto play (Known) |
| `1001` | L R | sound test (Known) |
| `0720` | L R | stage select (Known) |
| `0716` | L R | the ending (Known) |
| ★ `4476` | L R | sets `$0500_24E8`: the opponent's control word becomes 1 (`$0700_6DDE`), so **your pad moves both fields** and the CPU never moves ![](img/pbvb/one_pad_both_sides_4476.png) |
| ★ `0911` | L R | sets `$0500_24E0`: a **RESULT** screen (`$0700_7E46`: level, chains, giant bombs, stage times) after every round, normally only after the ending ![](img/pbvb/result_screen_0911.png) |
| ★ `0704` | L R | sets `$0500_24E4`: DOKURO on at every stage (skull attack blocks); from the code |
| ★ `0612` | L R | clears `$0500_2500`: ANIMATION 0 (slowest) in every game; from the code |
| ★ `0825` | L R, right Up, left Left | the **[ DEBUG MENU ]**, then a game with its settings ![](img/pbvb/debug_menu_0825.png) |
| ★ `0513` | L R, right Up, left Left | the DEBUG MENU, then a game where the CPU plays **both** sides (`$0700_6D64`) and the round replays ![](img/pbvb/cpu_vs_cpu_0513.png) |

## The DEBUG MENU

Left-pad Right and Left change the selected value (they wrap). A normal game fills the same variables from a 9-byte
record per stage (`$0700_7AF8`, tables `$0702_6588`, `$65EB`, `$664E`, `$66B1`, one per level); the menu (`$0700_64B0`,
defaults `$0700_6B46`) lets you set them by hand.

| Setting | RAM | Range | Effect |
|---|---|---|---|
| SCROLL | `$0500_24C0` | 0-1 | background scroll; 0 = still (seen) |
| ANIMATION | `$0500_24C4` | 0-2 | animation step every 4th / 2nd / every frame (`$0700_EC68`; code only) |
| DOKURO | `$0500_2540` | 0-1 | the 8-block attack row uses the skull block (`$0700_97F2`; code only) |
| TUBU | `$0500_254E` | 0-5 | the piece set (seen) |
| ENEMY | `$0500_252E` | 0-10 | the opponent and portrait (seen: 10 is a girl in place of Drifty) |
| WORLD | `$0500_26E0` | 0-3 | the background (seen) |
| SPEED | `$0500_2536` | 0-5 | drop speed (seen) |
| COLOR | `$0500_2532` | 1-5 | how many kinds of block (seen: 1 = all the same face) |
| ERASE | `$0500_2534` | 1-6 | blocks in a row to clear (seen) |
| ITEM | `$0500_26E3` | 0-16 | n > 0 makes every item type n-1 (`$0701_5FEC`; code only) |
| EVENT | `$0500_26E4` | 0-4 | n > 0 forces event n-1 and lowers the chain thresholds (code only) |
| WIN | `$0500_2538` | 1-2 | rounds to win (code only) |
| CPU | `$0500_253C`, `$253A` | 0-15 | CPU level, opponent and your side |

## ★ The developer menu (patch)

An unreferenced routine at `$0700_0A48` draws a boot menu: **VERTIAL BOY** (sic) / PANIC BOMBER, **VERSION
1995/07/21**, with GAME START, DEBUG GAME PLAY, DEBUG AUTO PLAY, SOUND TEST and ENDING. Nothing calls it.
`patches/pbvb_dev_menu.ips` (`tools/pbvb/mkpatch.py`) calls it at power-on and points the three debug items at the
sub-mode word the finished game reads (`$0500_24F8`; the menu still writes the old byte `$0500_26D9`). Patched file
(MD5 `8799f344054ba0088d399684902eefa1`) in BizHawk: GAME START boots normally, DEBUG GAME PLAY and DEBUG AUTO PLAY give
the DEBUG MENU and then a game (as `0825` and `0513`), SOUND TEST and ENDING open those.
![The developer menu](img/pbvb/dev_menu_patch.png)
