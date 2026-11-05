# Changelog

Changes to the [codes page and password generator](https://maxxthunder.github.io/bomberman/).

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
