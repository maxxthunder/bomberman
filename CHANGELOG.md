# Changelog

Changes to the [codes page and password generator](https://maxxthunder.github.io/bomberman/).

## 2.10.0 (2026-11-17)
- New game: Bomberman 64: The Second Attack!. A Z + A code for playing as the computer's characters, a map warp
  with two test maps, the shop that sells the four extra Battle stages and the Cowboy parts that change its
  salesman, the Battle-type unlock rule, GameShark codes, and developers' placeholder messages.
- New game: Bomberman 64 (Japan, 2001). A code in Bomberman Park that opens everything, the attractions played from
  the High Score page, a debug boot menu nothing loads, Panic Bomber X lettering, and text left over from
  Bomberman Land.
- Bomberman Hero: a Start-button code on the first screen opens a hidden Bonus entry, a three-stage White Bomb
  mission; Golden Bomber needs any five gold planets; Japan's Treasure Hunt rule.
- Bomberman 64: the Gold set needs a Hard file; Green Garden stage 1 cleared with the controller alone; an earlier
  look for the Battle stage Up and Down; Spellmaker's unused card voices; Europe's four-hour limit.
- Bomberman Quest: the Chaos Bomber beaten and the true ending; the second and third hidden duels won; the unused
  fourth fighter is the dancer, who needs only the Chaos Bomber.
- Bomberman B-Daman: the certificate ranks and what they open (title colours, Special, Survival and a hidden ????
  mode).
- Bomberman Max: a retail cart played into the other version's stages, the infrared panel that starts the legendary
  Charabom minigame, and a full Charabom battle from a save.
- Cards that the saved reference pages already list are marked Known on the Bomberman 64, Second Attack, 2001
  Bomberman 64, Hero, Quest and B-Daman pages.

## 2.9.1 (2026-11-16)
- A new icon for the Nintendo 64 games: the three-grip controller.

## 2.9.0 (2026-11-16)
- New game: Bomberman Hero. A GameShark code for the debug flag and its action menu and in-game menu, cheats, 35
  unused maps, the Gossick and Options unlocks, a hidden White Bomb mission behind a file-select entry that is never
  drawn, what all 24 treasures give, a developer backup-memory test and the 17 objects nothing uses.
- New game: Bomberman Quest. A Japan-only power-on code for the test menu and a debug new game, GameShark codes,
  the three hidden characters and their duels, both endings, an unused fourth fighter, town versions of the hidden
  characters, a third pause-menu button the cursor cannot reach, and four music tracks nothing plays.
- Bomberman 64: where each of the 24 Custom part pickups and the Gold Cards are, block by block; the unlocks the
  game grants and saves; the 30-kill Gold Card; the Gold set's rule; a clock code and a short-fuse code; the result
  screens; a broken one-enemy test room; a six-second jingle nothing plays.
- Bomberman '93: the enemy-wipe flag caught being set by a boss kill in play; the cheat tested across planets 3, 5
  and 6 and the boss stages; the Special Version's own code `1F00D3:01`; the "Tap is not connected" screen typed
  with the pad.
- Bomberman GB 3: City 5 played on foot from the first room to the boss with 85 of its 90 crystals.
- Bomberman Max: how the legendary Charaboms are earned (the By Chance Game, started only by infrared); the eight
  minigames; the stage count, 100 with 80 in each retail version.
- Tools: one Mesen runner for every system, one BizHawk runner, and shared fuzz and code-typing drivers in place of
  per-game copies. The page build stops on a broken code list or codec, and takes its game list from the code files.

## 2.8.0 (2026-11-15)
- New game: Bomberman 64, the first Nintendo 64 game here. A Start-button code for four more Battle stages, the
  three locked Options entries (music test, View Credits, Full Power) and what unlocks them, GameShark codes, four
  developer test maps, a stage warp and unused text and graphics.
- BizHawk's script console is hidden as well as the main window.

## 2.7.0 (2026-11-15)
- New game: Panic Bomber for PC Engine CD. A hidden sound test, a stage select for all 50 puzzle stages, a story
  stage select, and leftovers of an older title program on the disc.
- New game: Panic Bomber for PC-98. A DEBUG MODE page behind 128 presses on EXIT, a hidden 10th opponent, and the
  developers' crash screens.
- New game: Bomberman B-Daman. A Game Genie code for the debug mode left in the game: a scene select with all 100
  stages, five debug tools, unlimited tries, and a second battle arena the game never picks.
- Games with no passwords show their codes without the password box.

## 2.6.0 (2026-11-14)
- Bomberman '93: all 125 password cards typed in and played, US and JP. Codes for stages 2-8 of any world load that
  stage directly, so 7-2 to 7-8 can be played with no planet cleared.
- Fixed: '93's codes for 2-1 to 6-1 with no planet cleared start 1-1, since the planet map always opens the first
  uncleared planet.
- Fixed: the '93 enemy-wipe flag ($20CC) is one the game sets itself. Held on, it clears enemies on planets 1, 2,
  4 and 7 in both versions, not the bosses, and the stage can still be finished through its exit.
- Bomberman Max: "...END?" is one of three real endings, chosen by how many stages are cleared; the normal and full
  endings are shown.
- Bomberman GB 3: City 5's second room, with its four switches and door, reached; it leads to the round 6 boss.
- Super Bomberman 3: with the boss-death flag set, touching an enemy only makes the player blink too.
- Super Bomberman 5: the three graphics loaders followed; one is an object-script command nothing uses, and none
  can load the debug menu's font.
- Fixed: Bomberman Users Battle's password stages are drawn after a long black screen: 8-1 normally, rounds 1 and 2
  garbled.

## 2.5.2 (2026-11-14)
- Bomberman '93: a flag the game reads but never sets makes every enemy on the stage vanish (`1F00CC:01`,
  or `0080D0:80` in the ROM).
- Pictures for four more cards (Super Bomberman 2, Bomberman GB, Bomberman II).
- Fixed: Bomberman II's OZSPTANK makes the $ item give 16 seconds of immunity to blasts, not to enemies.
- Super Bomberman 2's R-in-Normal-Game code: the HUD shows 9 bombs at once,
  but the extra bombs only arrive after a bomb goes off.

## 2.5.1 (2026-11-14)
- Pictures for 239 cards: every cheat, unused item, secret and debug code that can be shown on screen now has
  one. Cheats are an off/on pair from the same start and frame; the rest show the thing itself in the game.
- Fixed: the Super Bomberman 2 speed/bombs/fire cheat used the stored kit at $80E0, which play never reads.
  The card now gives the live addresses ($80F0-$80F2); as printed, the speed and fire codes did nothing.
- Fixed: Super Bomberman 4's title turbo-X trick needs 64 presses, not 48. The first 16 only clear the
  silhouettes under the logo, while the title still runs at half speed, and are too close together to count.
- Fixed: Super Bomberman 1's debug scene list does hold labels 2-1 to 2-8, but the STAGE NO. line stops at
  2-4, so the last four can never be displayed.
- Super Bomberman 2's spike bombs: the blast really does carry on past a soft block (7 blocks an arm instead
  of 3), which needs fire to spare to see.
- Super Bomberman 5's invincibility codes: without them one blast kills, as soon as the stage-start blink has
  run out; there is no heart at the start of 1-1.
- Super Bomberman 1's 9-lives code: the counter never moves, but the HUD shows 8 from the first death on.
- Super Bomberman 3's title tap works on the European version too, and Bomberman '93's two speed passwords
  were typed in rather than only accepted by the checker.
- Smaller images: the picture folder holds 239 more pictures and is still smaller than before.

## 2.5.0 (2026-11-13)
- Super Bomberman 5: the 100% password screen (0926, then 4622 and 0413 at "200%"); the debug menu's font, never
  loaded, with the menu drawn in it; unused zone-map labels, item icons and battle counts; table 6's END picture.
- Super Bomberman 3: a flag nothing sets stops the clock (new cheat card).
- Panic Bomber (Virtual Boy): L and R after a lost round too, and the Japanese ROM.
- Bomberman GB 3: the stage-5 crystal count of all seven areas, and City stage 5's self-scrolling room.
- Wario Blast / Bomberman GB: B stops a kicked bomb (new card).
- Pocket Bomberman: the flower's bombs and fire last into the next stage.
- Bomberman Max: the bonus stages and an "...END?" screen.
- The page: clearer game names and version labels.

## 2.4.0 (2026-11-13)
- Super Bomberman 5: about 30 menus written in plain kana, from before the graphic ones, one of them reading
  "under construction: the Bowling Bomber goes here" (new card).
- Panic Bomber (Virtual Boy): 1298 is a boss run of five opponents, not one match; L and R after a won round bring
  up the VIRTUAL BOY screen; an unused LICENSED BY NINTENDO boot screen; a sixth demo and the demo recorder.
- Bomberman Max: the eight cut messages drawn in the game.
- Bomberman GB 3: the unused flag stops walking and bombs but not Start; the crystal count of four areas, and
  City's second bell panel, which can never appear.
- Wario Blast / Bomberman GB: Bomberman Selection, the Korean cart, and its Bomberman GB without the multitap
  battle.
- The page: a filter box for each game, plainer card titles, and build steps in the README.

## 2.3.0 (2026-11-11)
- Bomberman GB 3: a pad-freeze flag nothing sets (new cheat card), and an unused briefing line for a moving area.
- Bomberman '94: enemy type $1D, which no stage places, shown in play.
- Bomberman Max: messages the game never shows (four stage objectives, a Kick Game help page, two team lines), and
  the Japanese ending's keyword.

## 2.2.0 (2026-11-10)
- Bomberman GB 3: the stage-5 crystals played for real: a 1-up at 40, bell panels at 50 and 60, and the helper at the
  boss.
- Super Bomberman 5: all ten bosses beaten, the final boss's three forms (the pilot only on the good route) and both
  endings.
- Wario Blast / Bomberman GB: the VICTORY screen for players 2-4 (Wario only for player 1), and kick, liner and
  trouncer in a multitap battle.
- Pocket Bomberman: ability bit 3 lets flames pierce soft blocks.
- Super Bomberman 3: two more assets in use (the ending's starfield, an enemy's death frames), and Black Bomberman in
  the two-player ending.

## 2.1.0 (2026-11-10)
- Bomberman '93: bending fire, an unused power that turns a blocked blast around the corner (new card); a flag that
  freezes the pad; the CONFIGRATION screen's values shown in play; the password arrows and the continue screen's
  code; the Special Version's address for each cheat.
- Bomberman '94: the hatch-sealing scene between stages and the Sound Room's tune-only code, both reached in play.
- Super Bomberman: a palette-fade flag that leaves you playing on a black field (new card); the debug menu's
  power-ups played (POWER is the kick, KICK the punch); every boss defeat, the 5-8 one included.
- Super Bomberman 3: every boss beaten through to END, with the graphics only the boss scenes load and the final
  boss's rare attacks; PRESENTED BY HUDSON is the staff roll's last card.
- Super Bomberman 5: the clock item's enemy freeze.
- Bomberman GB 3: the stage-5 diamond bonus and the boss helper it brings (new card); challenge mode's rating,
  levels, ranking and a door to a second arena; the room map format.
- Pocket Bomberman: the boss rush played to the ending, the flower's effect checked, and walk speed.
- Wario Blast / Bomberman GB: the multitap battle's eight arenas, TECHNIQUE and the VICTORY screen.

## 2.0.0 (2026-11-10)
- A simpler page: the stage pickers are gone from the nine games whose tables already list every password, and the
  code box sits under the password tables in every game. The search box, the "All codes" filter and the jump on
  clicking a code are gone too; the icon legend moved into "Where these come from".
- Each game's header lists the system, the year and a flag for every region it came out in. The Game Boy games
  with Super Game Boy support show their title in their own SGB border, and Atomic Punk is shown in plain Game Boy
  greys.
- New versions: Dynablaster (Game Boy and NES), Pocket Bomberman (Japan and Europe), Panic Bomber (Japan), Bomberman
  on the Famicom Disk System, and the 1996 Bomberman Collection for Game Boy.
- About 70 Game Genie codes from a community compilation, each tested, with the Pro Action Replay or GameShark form
  where there is one. Cheat cards show a small logo for each device.
- About 120 cards now list more versions, each tested or checked against the other ROM, with the other version's
  code where it differs.
- New finds: Super Bomberman's fizzling battle bombs, its Reset keeping your password and its battle TIME UP!
  banner; NES Bomberman's score wrapping past 999,999,900; Super Bomberman 4's mouse warning screen; Super
  Bomberman 2's floor pits; a computer-only battle in Super Bomberman 5; chain effects in Panic Bomber W; more
  Mega Bomberman graphics; and region differences in several games.
- The soft-reset cards are gone.
- Smaller images, with duplicates removed, and an update now replaces cached copies.
- Bigger tap targets for the code buttons, sound clips and Details links.

## 1.18.0 (2026-11-09)
- Mega Bomberman: Bomberman '94's title logo on an unused planet screen, big countdown digits from an early
  continue screen, and a creature in the area 3 boss scene.
- Bomberman II: the ending's church cross, still in the US cartridge.

## 1.17.0 (2026-11-08)
- Play buttons on the unused music and sound cards.
- More unused sounds: three effects in Super Bomberman, one each in Super Bomberman 3 and Pocket Bomberman, two in
  Bomberman Max, three in the Mega Bomberman 8-player demo, and three samples only the Bomberman II sound room plays.
- Cut graphics: item panels and clock digits in the Mega Bomberman 8-player demo, a second ending sky in Panic
  Bomber W, other medals in Panic Bomber, a sprite sheet in Mega Bomberman, and Kondoria in Bomberman II.

## 1.16.0 (2026-11-07)
- Unused music and sounds in 11 more games: sound effects in Bomberman GB, Bomberman '90, '93 and '94, Mega
  Bomberman, Bomberman GB 2 and Panic Bomber W; two rewritten jingles in Users Battle; a tune and ten effects in
  Atomic Punk; a tune no world plays in Pocket Bomberman; tunes and effects beyond the sound test in Panic Bomber.
- The Bomberman head as the favicon and home-screen icon.
- Panic Bomber: the LICENSED BY NINTENDO screen is gone from the list.

## 1.15.0 (2026-11-07)
- Unused music and sounds: seven Super Bomberman tracks only the debug menu plays, eight Super Bomberman 2 sound
  effects, a jingle and four effects in Super Bomberman 4, Bomberman GB 3's music for the cut extra areas, and two
  Bomberman GB tunes.
- Cut stages, played: Super Bomberman's ring map as a battle stage; four unused boss arenas and two battle stages kept
  in the Caravan in Super Bomberman 2; stage 12's three cut variants in Super Bomberman 3; two cut World 5 stages and
  an unreferenced battle stage in Super Bomberman 4; an unused Area 6 map in Bomberman II.
- Bomberman '93 Special Version: the leftover SELECT STAGE map, a cut COM-LINK mode's screens, and its own world 6
  and staff-roll pictures. Bomberman '94: an unused jet sprite.
- Panic Bomber W: a surprise match against Shadow Bomber and the 名人 stamp after 10 VS wins. Panic Bomber: a button
  code that cuts the ending short. Atomic Punk: the password every island clear writes but never shows.
- The game picture keeps a wide title screen's own shape.

## 1.14.0 (2026-11-07)
- Unused graphics, shown in the games: Bomberman GB 3's TIME OVER screen and another PAUSE picture; a mechanical boss
  sprite set and four small machines in Bomberman '93; Pocket Bomberman's Japanese menu text; a starfield picture in
  Bomberman Max.
- Graphics notes for Bomberman, Bomberman GB and Bomberman '94.

## 1.13.0 (2026-11-07)
- Panic Bomber: a title-screen button code opens a hidden screen-alignment test; an unused LICENSED BY NINTENDO
  screen (patch); all 16 ITEM types of the DEBUG MENU, each with its effect; WIN confirmed.
- Panic Bomber W: the cut STAGE CLEAR tally screen (patch), and L or R with the d-pad scrolls the menu background.
- Atomic Punk / Bomber Boy: HATISUKE, a 10th panel the game never gives out, and TYUUSUU, My Town's unused name.
- Super Bomberman 3: the beta's extra continue case, played in both versions.
- NES Bomberman: all six bonus items made to appear, with their checks, stages and points. Bomberman II: the bomb-up
  seen in a stage.
- Hidden-content sweeps for Atomic Punk, Panic Bomber and Panic Bomber W.

## 1.12.1 (2026-11-06)
- The game picker has a tab per console and shows that console's games, so it takes far less room.

## 1.12.0 (2026-11-06)
- Region differences, new on many pages: Super Bomberman 5 Caravan's hidden HYPER Misobon setting (a returning player
  takes the stats of the one they blew up); Super Bomberman 2 Caravan's SNES Mouse lock; Super Bomberman 3's
  random-number log; Bomberman '93's format prompt on LOAD (US); Bomberman GB's attract story (Japan); Bomberman Max's
  certificate seal, Pentel logo and Game Boy boot screens; the NES Bomberman GBA releases' password screen; Bomberman
  II's Four Score check for BATTLE MODE and its intro skip.
- Bomberman (1990): items 12 and 14 seen and collected. Bomberman '93: the onigiri (pause 200 times), chick and tulip,
  each with its real trigger and points.
- Panic Bomber: what 0704 and 0612 really do, and the DEBUG MENU's EVENT, DOKURO, ANIMATION and CPU settings seen in
  play, with a card for the four forced events.
- Bomberman Max: the battle against the computer works on all five versions. Atomic Punk / Bomber Boy: the soft reset
  works on both carts.
- Super Bomberman 2: five card notes show their addresses again.

## 1.11.0 (2026-11-06)
- Panic Bomber (Virtual Boy): an unused developer menu (VERSION 1995/07/21), opened by a new patch; what the DEBUG
  MENU's 13 settings do; and what 4476, 0911, 9782, 0704 and 0612 really do (one pad moves both sides, a RESULT
  screen after every round, other pieces, skull blocks, slow animation).
- Bomberman (PC Engine, 1990): six hidden bonus items, worth 18,800 to 10,000,000 points, and what spawns each.
- Bomberman '93: the hidden pierce-fire item, an unused ribbon item and three hidden bonus items, with cheats.
- Wario Blast / Bomberman GB: the extra battle's 240-win PERFECT! screen with its CODE -SVJV-, and a cheat for it.
- Panic Bomber W: its PAL-console and SNES Mouse warning screens.
- Bomberman Max: a button sequence for a Charabom battle against the computer; Atomic Punk / Bomber Boy: the sound
  test and a soft reset.

## 1.10.0 (2026-11-06)
- The page works offline once opened, and installs as an app (Add to Home Screen).
- Panic Bomber (Virtual Boy): 0825 and 0513, with L, R, right-pad Up and left-pad Left held, open a hidden DEBUG MENU;
  the other button codes are read from the disassembled password check.
- Bomberman: Panic Bomber (PC Engine CD) has no password: it saves to the System Card.
- Removed Bomberman Selection; Atomic Punk / Bomber Boy has its own notes and tools.

## 1.9.0 (2026-11-05)
- New games: Atomic Punk / Bomber Boy (Game Boy), Panic Bomber (Virtual Boy) and Super Bomberman: Panic Bomber W
  (Super Famicom), each with a password generator and every listed code typed in an emulator.
- New finds: Panic Bomber's 1298 (play against Zach the Were-Bomberman) and its dead cheat slots; Panic Bomber W's
  round-1 codes; Atomic Punk's Game B takes NES Bomberman codes with A, E, I, O shown as 0-3.
- The NES Bomberman page notes the Game Boy Advance re-releases, which take the same codes.
- A Virtual Boy section in the game picker; within each system the games follow the list order.
- The generators' special-code menus are gone (the codes are listed below them).
- Special codes and secrets show what they do: the screens they open, and for Atomic Punk the island map and gold.
- Empty cells in a stage grid are marked as stages the game doesn't have.
- Images recompressed without loss (about 3 MB smaller).

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
