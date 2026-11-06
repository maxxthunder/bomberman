# Changelog

Changes to the [codes page and password generator](https://maxxthunder.github.io/bomberman/).

## 1.8.1 (2026-11-05)
- Every section heading has an icon (a key for passwords, a bomb for cheat codes, and so on).
- Country flags beside version and region names.
- Fixed: Bomberman Max and Bomberman Selection versions showed as short keys ("blue", "kr") instead of their names.
- README credits Font Awesome.

## 1.8.0 (2026-11-05)
- Each game opens with a header band: console-colour edge, big logo, name, system, year and a screenshot.
- Stage passwords show as a map grid (rounds or worlds down, stages across, boss stages tinted); codes that don't fit
  a grid show as labelled tiles.
- Passwords come first in every game's code list; the What's new section is gone (New marks stay on the codes).
- A dark/light toggle in the top corner, remembered in your browser; a faint bomb pattern behind the title.
- Icons from Font Awesome Free, loaded from jsDelivr.
- Google Tag Manager added.
- Fixed: card codes were drawn at the grid's smaller size, and a saved theme could flash the other one on load.

## 1.7.3 (2026-11-05)
- Game picker: space between the console groups, bigger group headings on desktop, and "Game Boy / Game Boy Color".
- Patch downloads have a download icon.

## 1.7.2 (2026-11-05)
- Bomberman Selection: cheat codes for 9,999 gold in Bomber Boy, and invincibility and instant set wins in Bomberman,
  each tested in an emulator.
- README: the games table and research notes follow the picker's order.

## 1.7.1 (2026-11-05)
- Removed the patches for Bomberman (PC Engine, 1990) and every Game Boy and Game Boy Color game; their cheat codes
  stay.
- Tools: unused scripts and screenshots removed, and the Mega Bomberman demo shares Mega Bomberman's VDP reader.

## 1.7.0 (2026-11-05)
- New game: Bomberman Selection (Korea), with a password generator for Bomber Boy (islands cleared and gold), its
  Bomber Man mode (NES Bomberman's codes) and Bomberman (Bomberman GB's codes).
- Game picker order: Super Nintendo, TurboGrafx-16 / PC Engine, Game Boy, NES, Genesis.
- Debug menu patches and cheats now show a screenshot of the menu they open.
- Removed Bomberman Quest, and the invincibility patches for Bomberman and Bomberman II (NES).

## 1.6.0 (2026-11-05)
- New fonts: Lilita One for headings, Fredoka for text, Azeret Mono for codes.
- Each game has its own link (for example `#sb2`); picking a game updates the address.
- Fixed: with the Japan version chosen, the Bomberman GB generator offered Wario and his codes, which that cart rejects.
- README rewritten: how to use it, a games table with links, highlights, and which ROM each patch needs.
- Tools: one shared IPS writer for the patch makers; duplicate scripts removed.

## 1.5.0 (2026-11-05)
- New game: Bomberman Quest (US and Japan), with an item code builder, its debug switches, cheats and patches.
- Cheat codes for both devices: Game Genie and Pro Action Replay (GameShark on Game Boy) side by side on each card,
  each tested in an emulator; RAM codes got a Game Genie form from the instruction that sets the value. Long code
  lists fold behind an "All codes" toggle.

## 1.4.2 (2026-11-05)
- The game picker on a game's page is a slim bar with the current game and a Change game button that opens every
  game as cards, grouped by console. No more scrolling row of logos; phones get the same bar instead of a drop-down.

## 1.4.1 (2026-11-05)
- Light mode: darker console colours for the picker headings and a readable ★ New mark in the password tables.

## 1.4.0 (2026-11-05)
- Each console has its own colour (Super Nintendo purple, Genesis blue, PC Engine orange, NES red, Game Boy green), and
  passwords are drawn as plates in the style of that console's password screen.
- Cards carry a coloured edge for what they are: a code to type, a secret, a cheat-device code, a patch or notes.
- Screenshots are shown full card width; the game picker is one scrolling row once a game is open.
- Light mode, following the device setting.

## 1.3.0 (2026-11-05)
- On the site (now on GitHub Pages): each game's passwords and special codes come first; debug notes, cheat codes and
  patches are at the bottom. Card details are collapsed behind a Details toggle.
- Every screenshot on a code's card shows that exact code; the ones that showed a blank entry, another code or
  several codes were re-captured.
- Pocket Bomberman's logo, icons and screenshots are in Game Boy Color colours.
- Removed the Super Bomberman 3 soft-reset patches (the Pro Action Replay codes stay).
- Tools: one HuC6280 disassembler, one emulator launcher (`tools/emu/run.sh`) and one Mesen runner.

## 1.2.1 (2026-11-05)
- Fixed: switching the Bomberman '93 or Bomberman II generator to another version made codes the checker rejected;
  Pocket Bomberman's ending code was missing from its special-code menu.
- Leaner page script: unused codec, logo and code-less-game paths removed.
- README: Bomberman Max's Charabom builder, a Bomberman Max row in the password table, notes grouped by console.

## 1.2.0 (2026-11-05)
- New games: Pocket Bomberman and Bomberman Max (all five versions, with a Charabom code builder).
- Users Battle moved to the bottom of the 1990 Bomberman page.
- The version selector shows only where the passwords differ by version; the letter-grid typing guide and the
  Fixed mark are gone.
- Open items closed in emulators: Bomberman II's icon colours and Four Score, Super Bomberman 2's Caravan stage
  select and bomb types, Mega Bomberman's invincibility and area codes, and the Game Boy games' text, stage maps,
  unused graphics and Super Game Boy 4-player battles.

## 1.1.0 (2026-11-05)
- New games: Bomberman and Bomberman II (NES), Wario Blast / Bomberman GB 1–3 (Game Boy), Bomberman: Users Battle,
  the Mega Bomberman 8-player demo, and the English Super Bomberman 4 and 5 and the TurboGrafx re-releases as versions.
- Every game swept for dead code, hidden button codes, unset flags, unused text and maps; cheat codes and IPS patches
  added and tested.
- Item icons ripped from the games next to the generator fields; one code per stage in the generators; long codes fit
  on a phone.

## 1.0.0 (2026-11-04)
- First release: Super Bomberman 1–5 and Mega Bomberman, with every code, a password generator and checker for each
  game, typing guides, and the Super Bomberman 5 character builder.
