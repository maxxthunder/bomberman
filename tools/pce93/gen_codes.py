import json, sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from password import encode
out = []
def stage_effect(w, s): return f"Start at world {w} stage {s} with 1 bomb, fire 1, normal speed, no planets cleared"
typed = {("us", 1, 1): "typed in Mesen: decoded to world 1 stage 1, bombs 1, fire 1; planet map, then stage 1-1",
         ("jp", 1, 1): "typed in Mesen: decoded to world 1 stage 1, bombs 1, fire 1; planet map, then stage 1-1"}
for ver, V in (("us", "US"), ("jp", "JP")):
    for w in range(1, 8):
        for s in range(1, 9):
            t = typed.get((ver, w, s))
            note = t or "accepted by the game's own decoder in the fuzz run with exactly these values"
            if w == 7: note += ". World 7 is closed until planets 1-6 are cleared: with this code the planet map puts you on planet 1 (typed for 7-1)"
            if ver == "jp" and w == 1 and s == 1: note += "; also accepted by the Special Version's leftover password screen"
            out.append({"code": encode(ver, world=w, stage=s), "effect": stage_effect(w, s),
                        "versions": [V] + (["SP"] if ver == "jp" else []) + ["vc"], "status": "unchecked",
                        "verified": "mesen" if t or w == 7 and s == 1 else "fuzz", "note": note, "section": "Stage codes"})
special = [
 (dict(world=7, stage=8, bombs=10, fire=5, cleared=63, speed=3), "Final stage (7-8) with 10 bombs, fire 5, every planet cleared and speed 3 (one above the skates' maximum)", "US_MAX"),
 (dict(world=1, stage=1, speed=3), "Stage 1-1 at speed 3, faster than the game's maximum of 2", "typed in Mesen: $389A = 3, player byte $9B = $30, measured faster than speed 2 (see docs)"),
 (dict(world=1, stage=1, speed=1), "Stage 1-1 at speed 1 (one skate)", "typed in Mesen: $389A = 1"),
 (dict(world=1, stage=1, speed=2), "Stage 1-1 at speed 2 (the game's maximum)", "typed in Mesen: $389A = 2"),
 (dict(world=3, stage=5, bombs=4, fire=2, cleared=3, speed=1), "Stage 3-5 with 4 bombs, fire 2, speed 1, planets 1 and 2 cleared", "typed in Mesen: all six values as stored; in the stage the player has $A0 = $24 (fire 2, bombs 4)"),
 (dict(world=2, stage=1, bombs=10, fire=5, cleared=1, speed=2), "Stage 2-1 with 10 bombs, fire 5, speed 2, planet 1 cleared", "typed in Mesen: player $A0 = $5A, $9B = $20 in the stage"),
]
for st, eff, note in special:
    for ver, V in (("us", "US"), ("jp", "JP")):
        n = note
        if note == "US_MAX": n = "typed in Mesen: decoded as listed; the planet map then starts the final stage (the four Bombers on karts)"
        fz = ver == "jp" and st.get("speed") in (1, 2) and st.get("world") == 1
        if fz: n = "accepted by the game's own decoder in the fuzz run with exactly these values (typed in the US version)"
        out.append({"code": encode(ver, **st), "effect": eff, "versions": [V, "vc"], "status": "unchecked", "verified": "fuzz" if fz else "mesen",
                    "note": n, "section": "Power-up codes"})
out.append({"code": "BBBBBBBB / AAAAAAAA", "effect": "Rejected (letters below the key)", "versions": ["US", "JP", "vc"], "status": "unchecked",
            "verified": "mesen", "note": "typed in Mesen (US); the screen stays", "section": "Stage codes"})
secrets = [
 ("Beat the game, hold I and press Run on the end screen, reset (Select+Run), start a Normal Game", "CONFIGRATION screen after each planet map: stage, scene, bombs, fire, power-ups, lives, sound/music test", ["JP"], "known", "mesen",
  "ending code 08:8C85 sets $3FFB; state 1 far-calls 08:8620 which checks it. Verified with $3FFB written, then real soft reset and presses; settings carried into the stage"),
 ("Same as JP (US)", "The sound plays and $3FFB is set, but nothing else: the call to the screen was removed (02:8421)", ["US"], "known", "mesen",
  "TCRF asked for a US way in: there is none on retail hardware. ROM patch file $4432: 00 20 E7 EA 20 86 08 restores the call; verified in Mesen"),
 ("Battle Game with Up+I+II+Select+Run held on pad 5 (or the only pad)", "'Tap is not connected' error screen", ["JP"], "known", "mesen",
  "07:A707 tests $36 & $1F = $1F; removed in the US. Verified by writing the pad-5 byte at the test"),
 ("(none: patch the title menu table 06:984C to $94A0)", "Leftover password screen; a valid code starts the leftover Normal Game through an old CONFIGRATION screen with a SOUND test", ["SP"], "new", "mesen",
  "all five menu entries are $A34E (battle), so the Special Version cannot reach it; 02:8435 calls the old screen 08:88BD with no flag"),
]
secrets += [
 ("Finish the game from a new game with no password and no continue", "The ending shows CONGRATULATIONS!, CLEAR TIME and CLEAR SCORE before the credits", ["US", "JP", "vc"], "new", "mesen",
  "08:8CB8 shows the page only when $38B1 = 0; a continue (07:A191) or a password (01:D93B) sets it. Shown in Mesen by clearing $38B1 at the ending (cheat 1F18B1:00)"),
 ("Title item 3 (VS GAME / COM-LINK)", "Link-cable screen: both players press Run, the first is White Bomberman; then waits for the other console", ["US", "JP"], "new", "mesen",
  "world 9 mode, 07:AC61; the serial handshake through the pad port never completes without a second console. On the Wii U VC the item starts the Battle Game instead (pcevc.md)"),
]
cheats = [
 ("1F0091:20", "Invincible: player 1 ability bit 5, read by the death check 02:8C79, never set by the game", ["US", "JP", "vc"], "new", "mesen", "Mesen raw code (RAM F8:0091 = $2091). Stood on its own bomb: lives kept; without it the same test lost a life (US)"),
 ("1F189F:09", "9 lives in reserve", ["US", "JP", "vc"], "new", "mesen", "RAM F8:189F = $389F; HUD showed 9 (US)"),
 ("1F189A:03", "Speed 3, one above the skates' maximum", ["US", "JP", "vc"], "new", "mesen", "RAM F8:189A = $389A, copied to the player at the stage start: $9B = $30 (US)"),
 ("1F1895:0w + 1F1896:0s", "World / stage select: every Normal Game stage is world w+1, stage s+1", ["US", "JP", "vc"], "new", "mesen", "RAM F8:1895 / F8:1896; 1F1895:03 + 1F1896:04 made a new game load record 28 (4-5) (US). Turn off after the stage starts"),
 ("1F1FFB:01", "CONFIGRATION screen after every planet map (stage, scene, power-ups, lives, sound)", ["JP"], "known", "mesen", "RAM F8:1FFB = $3FFB, the flag the ending's I+Run sets; screen shown (JP). US: use the patch"),
 ("1F18B1:00", "The ending's clear-time page even after a password or continue", ["US", "JP", "vc"], "new", "mesen", "RAM F8:18B1 = $38B1; page shown with the RAM cleared as the ending reads it"),
]
for code, eff, vers, status, ver, note in cheats:
    out.append({"code": code, "effect": eff, "versions": vers, "status": status, "verified": ver, "note": note, "section": "cheat"})
patches = [
 ("patches/pce93_configration_us.ips", "US: CONFIGRATION screen after every planet map", ["US"], "new", "mesen", "file $4432: 08 20 E7 EA 9A AB 06 -> 00 20 E7 EA 20 86 08 (far call to 08:8620 put back); the patched file showed the screen"),
 ("patches/pce93_normal_game_sp.ips", "Special Version: Run on the title opens the leftover password screen and Normal Game", ["SP"], "new", "mesen", "file $D84C: 4E A3 -> A0 94 (title menu entry 0 = $94A0); verified with the same bytes written in memory"),
]
for code, eff, vers, status, ver, note in patches:
    out.append({"code": code, "effect": eff, "versions": vers, "status": status, "verified": ver, "note": note, "section": "patch"})
for code, eff, vers, status, ver, note in secrets:
    out.append({"code": code, "effect": eff, "versions": vers, "status": status, "verified": ver, "note": note, "section": "Hidden screens"})
json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
print(len(out))
