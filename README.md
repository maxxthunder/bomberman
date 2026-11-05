# Bomberman Codes: NES, Game Boy, Game Boy Color, Super Nintendo, Genesis and PC Engine

**[Open the codes page and password generator →](https://maxxthunder.github.io/bomberman/)** &nbsp;[![v1.4.2](https://img.shields.io/badge/version-1.4.2-ff4f9a)](CHANGELOG.md)

<p align="center">
  <img src="docs/img/logos/nes1_us.png" alt="Bomberman (NES)" height="72">
  <img src="docs/img/logos/nes2_us.png" alt="Bomberman II" height="72">
  <img src="docs/img/logos/gb1_wario.png" alt="Wario Blast" height="72">
  <img src="docs/img/logos/gb2_us.png" alt="Bomberman GB" height="72">
  <img src="docs/img/logos/gb3_jp.png" alt="Bomberman GB 3" height="72">
  <img src="docs/img/logos/pocket.png" alt="Pocket Bomberman" height="72">
  <img src="docs/img/logos/max_blue.png" alt="Bomberman Max: Blue Champion" height="72">
  <img src="docs/img/logos/max_red.png" alt="Bomberman Max: Red Challenger" height="72">
  <img src="docs/img/logos/sb1_us.png" alt="Super Bomberman" height="72">
  <img src="docs/img/logos/sb2_us.png" alt="Super Bomberman 2" height="72">
  <img src="docs/img/logos/sb3_eu.png" alt="Super Bomberman 3" height="72">
  <img src="docs/img/logos/sb4_jp.png" alt="Super Bomberman 4" height="72">
  <img src="docs/img/logos/sb5_jp.png" alt="Super Bomberman 5" height="72">
  <img src="docs/img/logos/mega_us.png" alt="Mega Bomberman" height="72">
  <img src="docs/img/logos/pce90_us.png" alt="Bomberman" height="72">
  <img src="docs/img/logos/pce93_us.png" alt="Bomberman '93" height="72">
  <img src="docs/img/logos/pce94_jp.png" alt="Bomberman '94" height="72">
</p>

Every password and secret code for Bomberman and Bomberman II (NES / Famicom), Wario Blast / Bomberman GB 1–3 (Game
Boy), Pocket Bomberman and Bomberman Max (Game Boy Color), Super Bomberman 1 to 5 (Super Nintendo), Mega Bomberman
and its 8-player demo (Genesis), and Bomberman, Users Battle, Bomberman '93 and Bomberman '94 (TurboGrafx-16 / PC
Engine), read from each game's own code and tested in emulators. For every game, the page has:

- **Make a password** for any stage, and **check** one: it says whether the game takes it and what it holds.
- **Item icons** ripped from each game next to the power-ups a password holds.
- **Cheat codes** (Game Genie, Pro Action Replay, GameShark) and **IPS patches** for invincibility, debug menus and
  restored features, each tested in an emulator.
- **Every code**, with ★ New on the ones no published list had.
- **Super Bomberman 5 character builder:** pick body, colour, bombs, fire, speed and items for a 6-symbol Config
  Battle password, or paste one to see what it holds.
- **Bomberman Max Charabom builder:** the game has no password, so the page makes GameShark codes that give you any
  Charabom at any level.

The page works offline too: save [`index.html`](index.html) with the `docs/img/` folder next to it.

Every password checker was fuzzed against the game's own decoder in Mesen 2 (NES, Game Boy, SNES, PC Engine) or
BizHawk (Genesis): every possible code for the 4-digit games, and tens of thousands of codes (every state, plus random
and one-letter-off codes) for the longer ones. The game accepted exactly the codes the page accepts, in every version.

Contents: [What's new](#whats-new) · [How the passwords work](#how-the-passwords-work) ·
[Research notes](#research-notes) · [Tools](#tools) · [Credits and legal](#credits-and-legal)

## What's new

**Bomberman** (NES / Famicom, US and Japan)
- The 20-letter password fully decoded: stage, score and every power-up, with no range check, so fire 0–15, 16 bombs
  and stages 0–255 load. Stage 51 freezes; stages 96–103 and 224–231 hang.
- The "highlight" letter swap moves a value from wall pass to the reveal flag, which marks the exit and item on any
  stage. Codes that reach stage 74, 131 and 243, and fire 11.

**Bomberman II** (NES / Famicom, US and Japan)
- The password: the first letter is a key the rest are scrambled with, so every state has thousands of codes, and US
  and Japanese codes convert letter for letter.
- A demo recorder left in the ROM (one byte turns the attract demo into recording), the US cart's Four Score support,
  and the sound-test code hidden at the end of the US staff roll.

**Wario Blast / Bomberman GB** (Game Boy)
- Wario Blast is the Japanese Bomberman GB: it keeps every Japanese code and adds 32 that play as Wario.
- An unused early title logo, and the 4-player battle on a Super Game Boy multitap, played in an emulator.

**Bomberman GB** (Game Boy, US; Bomberman GB 2 in Japan)
- 7824 is in an unused older copy of the password table, where it meant the ending; the game rejects it.
- 5656 is the only way into battle on a plain Game Boy.

**Bomberman GB 3** (Game Boy, Japan)
- The 28-bit password decoded: its check is a capsule balance between what the cleared areas paid and what you
  bought. Codes for every area with the shop items its capsules can pay for.
- Two unused debug flags, invincibility and a stopped clock.

**Pocket Bomberman** (Game Boy Color, US / Europe)
- The 32-code password list in full, with three powered-up starts (Wind, Cloud, Evil) and 0278, the ending.
- An unused second password screen whose digits are switches for invincibility, world, area and a stopped clock;
  a patch brings it back.

**Bomberman Max** (Game Boy Color: Blue Champion, Red Challenger, Hikari no Yuusha, Yami no Senshi, Ain Version)
- No password: the game saves. The page builds GameShark codes for the Charabom roster in the save, any Charabom at
  any level, including the legendary pair and the two unused ones.
- The Ain Version opens all 95 stages of both sides; the US release swaps two Charabom names.

**Super Bomberman** (US, Europe, Japan, 1993-05-11 beta)
- 140 stage passwords no list had: every stage takes four codes, and the game shows one at random.
- The game never gives you a boss-stage password: a game over on x-8 shows an x-7 code.
- Secret items: the 20 known stages are the complete list. The 1-7 heart appears after 21.3 seconds of
  pressing nothing. Each item's prize, including the cake's 999,900 points.
- The prologue 9-lives trick's exact rhythm, and the unused debug menu shown running without a ROM patch.
- The first look at the 1993-05-11 beta.

**Super Bomberman 2** (US, Europe, Japan, US beta, Caravan)
- The debug menu works: stage select (6-0 plays the ending), no death, fire, bombs and items.
- The hidden battle stages need no Joycard: any steady X tap at 7–9 frames does it. The Caravan version turns the
  trick off.
- 5656 explained: in battle the hurry-up blocks fill the whole arena.
- The Caravan cartridge has its own stage-select limit; a Pro Action Replay code opens all 12 stages there too.

**Super Bomberman 3** (Europe, Japan, beta)
- `6514`: hard mode, every enemy takes one more hit.
- 78 stage passwords no list had, four for every stage.
- 4622, 1616 and 3194 pick one of four block layouts for every battle stage and lock stages 11 and 12 again.

**Super Bomberman 4** (Japan)
- `4622` (everyone starts in the middle) and `0164` (a wider battle item pool).
- `2679` starts 5-2. No 5-7 or 5-8 code can exist.
- The hidden battle stages need no Joycard, and tapping X 16 times clears the villain silhouettes from the title.

**Super Bomberman 5** (Japan, Caravan)
- Eight password handlers nothing points to, one of them invincibility.
- `0719` and `4737` only work on the Caravan cartridge, and 4737 starts everyone fully powered.
- `U04GJL` and `XR0PLG` are typed with a zero (the grid has no letter O); U04GJL is a yellow Bomberman. Gold
  Bomberman unlocks at 100%, and how the game records it.

**Mega Bomberman** (US, Europe, 8-player demo)
- The password stores which stages you cleared, so 50 codes skip stages, and each boss has several codes.
- The stage map format, every map rendered, and Game Genie codes for invincibility, lives, the clock and area select.
- The 8-player demo's unused CPU-time meter and item, with codes to start powered up.
- `2200`, `7422` and `6803` work on the Genesis as well as the TurboGrafx-16.
- The Genesis game has no sound test, and nothing is locked or hidden behind a code.

**Bomberman** (TurboGrafx-16 / PC Engine, US and Japan)
- The Special Select Room needs a high score whose hundreds digit is exactly 3 (300 or 1,300),
  all five buttons held, and the last demo played to its end.
- Fire up to 15 by password, past the in-play cap of 5. Music 2D and 39 aren't unused: they play on the losing console
  in a link-cable battle.

**Bomberman: Users Battle** (PC Engine, Japan)
- The 1990 game cut down to battle mode, with all 64 one-player stages and the password screen still inside; a patch
  opens the screen and the one-player game.

**Bomberman '93** (US, Japan, Special Version)
- Why the US "Configration" screen can't be reached: the ending still sets its flag, but the US game no longer calls
  the screen. A 7-byte patch puts the call back.
- Speed 3 by password only, above the skates' cap of 2. The Special Version is a battle-only cart with the Normal Game,
  the password screen and an older Configration screen left inside.

**Bomberman '94** (Japan, demo CD)
- Every password also works in Mega Bomberman: the two games share the codec code for code.
- No button combination reaches the Debug Version menu. A debug pause menu behind the known development text works again
  with two small patches: invincibility, stage clear and an enemy editor.
- The demo CD has a hidden "needs Super CD-ROM²" screen and never-read sectors with earlier artwork.

## How the passwords work

| Game | Code | What it holds | Valid codes |
|---|---|---|---|
| Super Bomberman | 4 digits, 0–7 | stage only, plus a random salt and a check digit | 192 of 4,096, plus 5656 |
| Super Bomberman 2 | 4 digits | a fixed list: five stages, the same five at full power, 5656 | 11 |
| Super Bomberman 3 | 4 digits | stage, scrambled with a 4-bit check | 104 stage codes + 14 special |
| Super Bomberman 4 | 4 digits | a fixed table of 50 numbers | 38 stages + 12 special |
| Super Bomberman 5 | 4 digits; 6 symbols | option codes; Config Battle characters (30 bits with a 4-bit sum) | 12 option codes (10 on retail); any character |
| Mega Bomberman | 4 digits | area and a bitmask of the stages cleared, with a 5-bit check | 111 of 10,000 |
| Bomberman (PC Engine) | 8 letters | round, stage, bombs, fire, skate, with a bit-count check, scrambled at random | 5,930,496 strings |
| Bomberman '93 | 8 letters | world, stage, bombs, fire, speed, cleared planets, with a sum check | 716,800 |
| Bomberman '94 | 4 digits | the same as Mega Bomberman | 111 of 10,000 |
| Bomberman (NES) | 20 letters, A–P | stage, score, every power-up, with four sums | one code per state |
| Bomberman II | 8 characters | area, stage, bombs, fire, XORed with a key letter, with a sum | 4,096 per state + 7 secret |
| Wario Blast / Bomberman GB (Japan) | 4 digits | a fixed list | 68 (Japan 34) |
| Bomberman GB (US) / GB 2 | 4 digits | a fixed list | 11 |
| Bomberman GB 3 | 7 hex digits | area, stage, areas cleared, shop items, capsules, with a capsule balance | 20,329 |
| Pocket Bomberman | 4 digits | a fixed list | 32 |
| Bomberman Max | none: the game saves | (GameShark codes for the Charabom roster) | 30 Charaboms × levels 1–99 |

The details, with ROM addresses, are in the research notes.

## Research notes

- NES: [Bomberman](docs/nes1.md), [Bomberman II](docs/nes2.md)
- Game Boy: [Wario Blast / Bomberman GB](docs/gb1.md), [Bomberman GB / GB 2](docs/gb2.md),
  [Bomberman GB 3](docs/gb3.md)
- Game Boy Color: [Pocket Bomberman](docs/pocket.md), [Bomberman Max](docs/max.md)
- Super Nintendo: [Super Bomberman](docs/sb1.md), [2](docs/sb2.md), [3](docs/sb3.md), [4](docs/sb4.md),
  [5](docs/sb5.md), and the English [4](docs/sb4en.md) and [5](docs/sb5en.md) (Super Bomberman Collection)
- Genesis: [Mega Bomberman](docs/mega.md) and its [8-player demo](docs/mega8.md)
- PC Engine: [Bomberman](docs/pce90.md), [Users Battle](docs/pceub.md), [Bomberman '93](docs/pce93.md),
  [Bomberman '94](docs/pce94.md), and the [Wii U and Collection re-releases](docs/pcevc.md)

Each code list is also in `docs/<game>_codes.json`, and the screenshots that prove the finds are in `docs/img/<game>/`.

## Tools

- `tools/<game>/password.py` and `password.mjs`: each game's password codec (the page uses the `.mjs` one).
- `tools/build_page.py`: builds `index.html` from `tools/page_template.html`, the codecs and the code lists.
  `node tools/check_page.mjs` checks the result.
- `tools/disasm.py`: recursive 65816 disassembler (LoROM and HiROM), grown with entry points from Mesen code/data logs.
  `tools/m68k.py`: 68000 listing for Mega Bomberman. `tools/m6502.py` (NES) and `tools/sm83.py` (Game Boy) do the same
  for the 8-bit games, and `tools/huc6280.py` for the PC Engine.
- `tools/<game>/run.sh script.lua [ver]` (all through `tools/emu/run.sh`) runs a game's Lua test scripts headless with
  `tools/emu/mesen.py` (or `mesen_gb.py`, `mesen_nes.py`, `bizhawk.py`). Set `MESEN` or `EMUHAWK` to the emulator.

IPS patches for the debug menus and other restored features are in `patches/`.

ROMs aren't included. Put them in `roms/` with their No-Intro names.

## Credits and legal

*Bomberman*, *Bomberman II*, *Bomberman GB* 1–3, *Pocket Bomberman*, *Bomberman Max*, *Bomberman '93*, *Bomberman
'94* and *Super Bomberman* 1–5 are © 1985–1999 Hudson Soft, *Mega Bomberman* is © 1994 Hudson Soft and Sega, and
*Wario Blast* is © 1994 Hudson Soft and Nintendo; Bomberman now belongs to Konami. This project isn't affiliated with
or endorsed by Konami, Hudson Soft, Sega or Nintendo. The game art on the page and in this repo (logos and
screenshots) belongs to them and is used here for reference. The disassembly listings are for research; no ROMs or
game data are included.

Published codes were checked against the GameFAQs cheat pages and other published notes for each game.

The code in this repo (the page, codecs, tests and tools) is released under the [MIT License](LICENSE).
