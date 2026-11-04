# Bomberman Codes: Super Bomberman 1–5, Mega Bomberman and the PC Engine games

**[Open the codes page and password generator →](https://maxxthunder.github.io/bomberman/)** &nbsp;[![v1.0.0](https://img.shields.io/badge/version-1.0.0-ff4f9a)](CHANGELOG.md)

<p align="center">
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

Every password and secret code for Super Bomberman 1 to 5 (Super Nintendo), Mega Bomberman (Genesis), and Bomberman,
Bomberman '93 and Bomberman '94 (TurboGrafx-16 / PC Engine), read from each game's own code and tested in emulators. For every game, the page has:

- **Make a password** for any stage, and **check** one: it says whether the game takes it and what it holds.
- **Letter-grid guide** for the codes typed on a grid (Super Bomberman 5 characters, Bomberman, Bomberman '93): the
  grid with the next letter lit.
- **Every code** with ★ New for codes no published list had, and Fixed for ones that were posted wrong.
- **Super Bomberman 5 character builder:** pick body, colour, bombs, fire, speed and items for a 6-symbol Config
  Battle password, or paste one to see what it holds.

The page works offline too: save [`index.html`](index.html) with the `docs/img/` folder next to it.

Every password checker was fuzzed against the game's own decoder: every possible code was fed to the real game in
Mesen 2 (SNES, PC Engine) or BizHawk (Genesis), and the game accepted exactly the codes the page accepts, in every version.

Contents: [What's new](#whats-new) · [How the passwords work](#how-the-passwords-work) ·
[Research notes](#research-notes) · [Tools](#tools) · [Credits and legal](#credits-and-legal)

## What's new

**Super Bomberman** (US, Europe, Japan, 1993-05-11 beta)
- 140 stage passwords no list had: every stage takes four codes, and the game shows one at random.
- `7632`, posted as "Level 7-1", is a 6-7 code; there is no world 7.
- The game never gives you a boss-stage password: a game over on x-8 shows an x-7 code.
- Secret items: the 20 known stages are the complete list. The 1-7 heart's trigger is pressing nothing for 21.3
  seconds, not standing on the exit. Each item's prize, including the cake's 999,900 points.
- The prologue 9-lives trick's exact rhythm, and the unused debug menu shown running without a ROM patch.
- The first look at the 1993-05-11 beta.

**Super Bomberman 2** (US, Europe, Japan, US beta, Caravan)
- The debug menu works: stage select (6-0 plays the ending), no death, fire, bombs and items.
- The hidden battle stages need no Joycard: any steady X tap at 7–9 frames does it. The Caravan version turns the
  trick off.
- 5656 explained: in battle the hurry-up blocks fill the whole arena.

**Super Bomberman 3** (Europe, Japan, beta)
- `6514`: hard mode, every enemy takes one more hit.
- 78 stage passwords no list had, four for every stage.
- 5656's "yellow character" doesn't happen; 4622, 1616 and 3194 pick one of four block layouts for every battle
  stage and lock stages 11 and 12 again.

**Super Bomberman 4** (Japan)
- `4622` (everyone starts in the middle) and `0164` (a wider battle item pool).
- `2609`, posted for 5-2, is `2679`. No 5-7 or 5-8 code can exist.
- The hidden battle stages need no Joycard, and tapping X 16 times clears the villain silhouettes from the title.

**Super Bomberman 5** (Japan, Caravan)
- Eight password handlers nothing points to, one of them invincibility.
- `0719` and `4737` only work on the Caravan cartridge, and 4737 starts everyone fully powered (no power-ups every 10
  seconds).
- `UO4GJL` and `XROPLG` need a zero, not the letter O; U04GJL is a yellow Bomberman, not Gold. 0926 doesn't unlock
  Gold: reaching 100% does, and how the game records it.

**Mega Bomberman** (US, Europe)
- The password stores which stages you cleared, so 50 codes skip stages, and each boss has several codes.
- `2200`, `7422` and `6803`, listed only for the TurboGrafx-16, are the Genesis codes missing from the list.
- The TurboGrafx sound test isn't in the Genesis game; nothing is locked or hidden behind a code.

**Bomberman** (TurboGrafx-16 / PC Engine, US and Japan)
- The Special Select Room needs a high score whose hundreds digit is exactly 3 (300 or 1,300, not "300 or more"),
  all five buttons held, and the last demo played to its end.
- Fire up to 15 by password, past the in-play cap of 5. Music 2D and 39 aren't unused: they play on the losing console
  in a link-cable battle.

**Bomberman '93** (US, Japan, Special Version)
- Why the US "Configration" screen can't be reached: the ending still sets its flag, but the US game no longer calls
  the screen. A 7-byte patch puts the call back.
- Speed 3 by password only, above the skates' cap of 2. The Special Version is a battle-only cart with the Normal Game,
  the password screen and an older Configration screen left inside.

**Bomberman '94** (Japan, demo CD)
- Every password also works in Mega Bomberman: the two games share the codec code for code.
- No button combination reaches the Debug Version menu. A debug pause menu behind TCRF's development text works again
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

The details, with ROM addresses, are in the research notes.

## Research notes

- [Super Bomberman](docs/sb1.md)
- [Super Bomberman 2](docs/sb2.md)
- [Super Bomberman 3](docs/sb3.md)
- [Super Bomberman 4](docs/sb4.md)
- [Super Bomberman 5](docs/sb5.md)
- [Mega Bomberman](docs/mega.md)
- [Bomberman (PC Engine)](docs/pce90.md)
- [Bomberman '93](docs/pce93.md)
- [Bomberman '94](docs/pce94.md)

Each code list is also in `docs/<game>_codes.json`, and the screenshots that prove the finds are in `docs/img/<game>/`.

## Tools

- `tools/<game>/password.py` and `password.mjs`: each game's password codec (the page uses the `.mjs` one).
- `tools/build_page.py`: builds `index.html` from `tools/page_template.html`, the codecs and the code lists.
  `node tools/check_page.mjs` checks the result.
- `tools/disasm.py`: recursive 65816 disassembler (LoROM and HiROM), grown with entry points from Mesen code/data logs.
  `tools/m68k.py`: 68000 listing for Mega Bomberman.
- `tools/emu/mesen.py` and `tools/emu/bizhawk.py` run the Lua test scripts in `tools/<game>/` headless. Set `MESEN`
  or `EMUHAWK` to the emulator.

IPS patches for the debug menus and other restored features are in `patches/`.

ROMs aren't included. Put them in `roms/` with their No-Intro names.

## Credits and legal

*Bomberman*, *Bomberman '93*, *Bomberman '94* and *Super Bomberman* 1–5 are © 1990–1997 Hudson Soft, and *Mega Bomberman*
is © 1994 Hudson Soft and Sega; Bomberman
now belongs to Konami. This project isn't affiliated with or endorsed by Konami, Hudson Soft or Sega. The game art on the page and in this repo (logos and
screenshots) belongs to them and is used here for reference. The disassembly listings are for research; no ROMs or game data are
included.

Published codes were checked against the GameFAQs cheat pages and The Cutting Room Floor's pages for each game.

The code in this repo (the page, codecs, tests and tools) is released under the [MIT License](LICENSE).
