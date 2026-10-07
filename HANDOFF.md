# Robo — Farsi virtual pet. Session handoff (2026-10-07)

## What this is
Talking-Tom-style 3D virtual pet for a 3-year-old, Farsi learning hidden inside play. Originally planned as a Persian cat "Pash" for native iOS (see `C:\Users\ahmma\Downloads\Virtual Pet App\Pash_Farsi_iPad_App_Full_Chat_Handoff.txt` for the full product brief, 50-word list, personality, interaction list). Decisions made since:

| Topic | Decision |
|---|---|
| Platform | Web app (three.js, one `index.html`, no bundler), deployed to **GitHub Pages** (free HTTPS → mic + PWA work on iPad). Wrap with Capacitor later for native iOS/Android. User is on Windows, no Mac. |
| Character | **Robotz** pack from Fab (free, Standard License, by ThreeDee / Samuel Briskar). Blender source only. Build = **Head 2 + Body 5 + antenna copied from Head 4**. Robot instead of cat. |
| Animations | Pack has only wave/thumbs-up/shrug/scroll/money. We author all game moves ourselves as Blender bone actions via Python, run headless. |
| Voice | ElevenLabs pre-generated mp3s bundled in `audio/`. User will supply key via env var or generate manually; key never goes in app or chat. Fallback until then: Safari `speechSynthesis` fa-IR. |
| Talk-back | Mic auto-listen (volume gate) → record → play back pitch-shifted robot voice. No speech recognition in v1. |
| Sounds | User supplied `Virtual Pet Sounds/` (antenna, belly, bored, dance, Face, feet, Fly, Head, Hi, Rocket, Wake .mp3) — use these for reactions; note Fly/Rocket suggest a jet/hover move. |

Full approved plan: `C:\Users\ahmma\.claude\plans\noble-mixing-cookie.md` (Phase A Blender pipeline, Phase B web app, clip names, verification).

## Machine
- Blender 5.2: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (not on PATH). Run headless: `& "...blender.exe" -b file.blend -P script.py`
- Node + Python 3.14 installed. Preview via the Claude browser pane.

## Folder state
```
C:\Users\ahmma\Documents\Robo\
  HANDOFF.md
  blender\
    robotz_source_files.zip     18 MB  ← Blender source (the one we need)
    animations.zip              625 MB ← pack's 5 animations, probably rendered; inspect before relying on it
    separated_robots_png_files.zip, whole_robots_webp_files.zip ← reference PNGs (useful to see what Head 2 / Body 5 / Head 4 look like)
  Virtual Pet Sounds\*.mp3
```
Nothing unzipped yet. No code written yet. No git repo yet.

## Status (end of session 2)
Steps 1–4 DONE. `blender/robo_master.blend` = Head 2 (`geo_head_bot_1`) + Body 5 (`geo_body_bot_4`) + arms (`geo_arm_bot_4`) + spring antenna split from Head 4 (`geo_antenna`, own bone `Antenna_Spring`), palette tint, 17 actions.
Rebuild from scratch: `blender -b src/ROBOTZ.blend -P assemble.py` then `blender -b robo_master.blend -P animate.py`. Previews: `render_clips.py [-- Clip]` → `preview/clips_N.png`.
- Pack numbers parts from 0 (Head 2 = `_1`). Rig is Rigify; actions key controls (`Body`, `Head`, `upper_arm_fk/forearm_fk`, finger masters, `Antenna_Spring`), IK_FK set to FK. Export must bake to DEF bones.
- Blink is NOT a bone action: eyes/mouth are Blender-only shaders driven by `Eyes_*`/`Mouth_*` bones. Plan: bake face screens to images at export, swap textures in the web app.
- Arms are short: raised hand reaches mid-head. Wave/ThumbsUp authored by us (pack's "animations" were single-frame poses).
- Step 5 DONE: `blender -b robo_master.blend -P export.py` → `robo.glb` (19.3k tris, 1.7 MB, 17 clips, WebP 1k textures, subsurf off, arms decimated) + `face/*.png` (22 eye/mouth expressions). Checked in `blender/glb_check.html` (serve Robo/ with `python -m http.server 8123`; `pose('Fall', 1.25)` in console).
- Web app notes: three.js strips dots from names → bones `DEF-Body`, `DEF-Head`, `DEF-handL`, `Antenna_Spring`. Face = meshes `Cube014_2` (mat `mat_bot_1_eye`) and `Cube014_1` (mat `mat_bot_mouth`); expression = swap `material.map` to a `face/*.png` (set `flipY=false`, sRGB). Blink = `eye_blink.png` for ~120 ms.
- Clips (23): Idle, HeadPoke, BellyPoke, FootPoke, Dizzy, Fall/GetUp (side), FallBack/GetUpBack, FallFront/GetUpFront, FallApart/Reassemble (head pops off + arms slide off, then fly back), Fart, Sneeze, Eat, DanceWiggle, DanceSpin, DanceJump, Sleep, Fly, Wave (palm to screen), ThumbsUp (fist, thumb up). App picks a random fall variant and plays the matching get-up.
- Pose params in animate.py: `twistL/R` (1 = palm to camera), `curlL/R` (1 = fist), `thumbL/R` (thumb master euler). `render_hands.py` = hand close-ups.

## Phase B status (session 2)
Steps 1–11 DONE and verified in the browser pane: `index.html` (whole app), `game.js` (pure rules/state machine), `phrases.json` (104 lines), `sfx/` (copied sounds), `test.html` (29 checks, ALL PASS), `manifest.json`, `sw.js`, `icon.png`, `gen-audio.mjs`, `README.md`, `.gitignore`.
- Controls: tap zones head/face(screen)/belly/foot/hand/antenna; 4 taps in 2 s = random fall + matching get-up; swipe up = Fly 3.5 s; drag food = Eat (3 in a minute = fart); speaker = dance 24 s; bed = sleep (tap to wake); 👂 = talk-back; idle 30–60 s = random silly; hold top-left 3 s = parent panel.
- No Persian system voice on iPad: until `node gen-audio.mjs` runs, phrases only animate the mouth (still counted in stats).
- Mic gate `TH = .04` in index.html — tune on the real iPad.
- Step 12 DONE: public repo https://github.com/kitchennetweb-a11y/robo, live at https://kitchennetweb-a11y.github.io/robo/ (live test.html ALL PASS). SSH push is not set up on this PC; push with `git -c "credential.helper=!gh auth git-credential" push` (or run `gh auth setup-git` once). Bump `V` in sw.js on every deploy.
- `sfx/*.mp3` are the parent's own ElevenLabs voice lines (same voice). Rule: when one plays, no phrase is said on top. Mapping: hi=greet+hand tap (Wave), wake, sleep=bed, fly=swipe up (only sound), head=head swipe (HeadWobble, woozy face), bored=no touch for 2 min, face/belly/feet/antenna=those taps, dance=dance start. arm=upper/forearm tap (ThumbsUp), feed=food dropped on Robo, jump=jump dance step, yay=get-up after a fall + dance end, listen=👂 turned on, rocket=toy rocket. ball/bubbles/peek copied, not used yet (future toys). Head *tap* uses ElevenLabs phrases.
- Rocket DONE: tap toy rocket → RocketLaunch (crouch, booster flames + smoke + camera shake, out of view) → RocketLand. Flames are two additive cones on DEF-Body in index.html.
- Browser pane runs ~5 fps in the background, so animations look slow there; use `robo.pose(clip, t)` in the console to check frames.
- Voice DONE: 104 phrases in `audio/` (voice 8Ebkg5uUcbSbeqGucAoR, eleven_v3), deployed. App adds a ring-mod robot effect to them + talk-back (`ROBOT_HZ`/`ROBOT_DRY` in index.html) to match the parent's ElevenLabs "Robot" filter on sfx/. To redo one phrase: delete `audio/<id>.mp3`, run gen-audio.mjs, commit.
- Robot voice v2 (`voice.js`): channel vocoder on a fixed 129 Hz buzz — measured from the parent's ElevenLabs Robot lines with `blender/voice_analysis.py` (their pitch is locked at 129 Hz; a ring modulator sounded "too fuzzy"). Phase-scattered harmonics keep it smooth and unclipped. test.html renders it offline and checks pitch lock, no clipping, loudness vs sfx/hi.mp3.
- Ball toy DONE: striped ball, tap = roll to Robo, flick = throw; friction, wall/rocket bounces; reaching idle Robo → FootPoke kick back toward the child + ball.mp3. Robo's head follows the rolling ball.
- Ball simplified (user request): tap only (no drag/flick) → rolls to just in front of Robo → he kicks it back toward the screen (±35°). Ball is fenced to z ≥ .35 (in front of Robo) so it can never hide behind him; if Robo is busy it waits at his feet and gets kicked when he's free. Rocket toy moved to (.85, .1), behind the fence. Verified 10/10 start positions with `robo.stepBall` (console helper; works even when the pane is hidden and rAF is paused).
- Bubbles toy DONE: pink bottle with wand by the bed; tap → Robo hops (star eyes) + bubbles.mp3, 16 pastel bubbles float slowly toward Robo; tap a bubble (generous reach) to pop it (synth pop + splash); bubbles touching Robo pop; Robo's head follows them. Ball moved to front-centre (-.4, .8) so it doesn't hide the bottle.
- Fixed: tapping an unknown zone could leave Robo stuck in 'react' (game.js now ignores it; tested).
- Peekaboo DONE: folded starry blanket on the floor left of Robo (-.55, .1). Tap → it arcs over and covers Robo (mode 'hide', blanket "breathes"); tap blanket or Robo (or wait 7 s) → it flies back folded, Robo does DanceJump (arms up) with joy face + peek.mp3. Other toys are ignored while hiding.
- Console helpers: `robo.render()`, `robo.stepBlanket(t)`, `robo.stepBall(dt, t)` work even when the pane is hidden (rAF paused, screenshots time out).
**Next: iPad testing with the child. All parent sounds are now wired.**

## Next steps (Phase A, in order)
1. Unzip `robotz_source_files.zip` into `blender/src/`. Peek at the reference PNGs to confirm which parts are "Head 2", "Body 5", "Head 4".
2. `blender/inventory.py`: dump objects, collections, armature bones, shape keys, actions, materials → `blender/inventory.txt`. Read it; map the real names.
3. `blender/assemble.py`: keep Head 2 + Body 5 (+ arms/hands), duplicate Head 4 antenna onto Head 2, add an antenna bone, delete the rest, palette (gray-blue body, cream face, teal accents). Save `robo_master.blend`.
4. `blender/animate.py`: actions `Idle, Blink, HeadPoke, BellyPoke, FootPoke, Dizzy, Fall, GetUp, Fart, Sneeze, Eat, DanceWiggle, DanceSpin, DanceJump, Sleep, Fly` (+ pack's `Wave`, `ThumbsUp`). Render preview frames to `blender/preview/` and check them visually.
5. `blender/export.py` → `robo.glb`, ≤30k tris. Load in a bare three.js page, print `gltf.animations` names.
6. Then Phase B (web app) per the plan, then `git init` + `gh repo create` + Pages.

## Rules carried over
- Ponytail mode: shortest working thing. One HTML file. No framework, no bundler.
- No ElevenLabs key in code or chat. Script reads `ELEVENLABS_API_KEY` from env.
- Child-safe: no text, no menus, no timers, no wrong-answer punishment. Parent area behind long-press.
```

## Prompt for the new session
Paste this:

> Read `C:\Users\ahmma\Documents\Robo\HANDOFF.md` and the plan at `C:\Users\ahmma\.claude\plans\noble-mixing-cookie.md`. Continue from Phase A step 1: unzip the Robotz source, inventory it with a headless Blender script, then assemble Head 2 + Body 5 with the antenna from Head 4 and show me a rendered preview before animating. Keep it ponytail-minimal. Don't ask me to re-decide anything already in the handoff.
