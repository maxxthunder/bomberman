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
pad and Left on the left pad (`$0702_00F0`). The handlers start at `$0702_01EC`.

- ★ **`1298`**: the level choice comes up, then THE SCARY RUINS against **Zach the Were-Bomberman** ("My name is
  Zach. I am a Were-Bomberman!") instead of Drifty. ![1298](img/pbvb/zach_1298.png)
- With L and R held: `0130` auto play, `1001` sound test, `0720` stage select, `0716` the ending (all Known, all
  typed in BizHawk).
- ★ **`0825` and `0513`** with L, R, right-pad Up and left-pad Left held open the **[ DEBUG MENU ]**: SCROLL,
  ANIMATION, DOKURO, TUBU, ENEMY, WORLD, SPEED, COLOR, ERASE, ITEM, EVENT, WIN and CPU, each with a value; A starts a
  game with them. The two handlers differ only in a sub-mode byte; both menus look the same.
  ![0825](img/pbvb/debug_menu_0825.png)
- ★ `0612`, `0911`, `0704` and `4476` (with L and R) and `9782` (no buttons) are taken and return to the menu. Their
  handlers set flags at `$0500_24E0`, `$24E4`, `$24E8` and `$24F4` (`0612` clears `$0500_2500`); the game reads them
  when a stage starts, each frame, and when a stage code is entered, but a game started after each looked the same as a
  normal one in BizHawk. (BizHawk's Virtual Boy core exposes no work RAM, so the flags were read from the code only.)
