# Robo

Farsi-speaking 3D robot pet for a 3-year-old. One web page (three.js), installable on an iPad home screen.

- **Play:** tap head / face / belly / feet / hands / antenna, poke fast to knock him over, swipe up to fly, drag food onto him, tap the speaker to dance, tap the bed to sleep, 👂 to have him repeat you in a robot voice.
- **Parents:** hold the top-left corner for 3 seconds.
- **Run locally:** `python -m http.server 8123`, open http://localhost:8123 (mic needs https or localhost). `test.html` runs the self-checks; `index.html?debug` shows touch zones.
- **Voice:** set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID`, run `node gen-audio.mjs`; files land in `audio/`. Until then Robo only moves his mouth (iPads have no Persian system voice).
- **3D asset:** `blender/` scripts rebuild `robo.glb` + `face/` from the Robotz pack (see HANDOFF.md).
- **Native later (Capacitor, not done yet):** `npm i @capacitor/core @capacitor/cli && npx cap init Robo ca.robo.app --web-dir . && npx cap add android` (iOS needs a Mac).
- Offline: `sw.js` is network-first, so a push shows up on the next launch (within ~10 min, GitHub Pages' HTTP cache); the cache is only used without internet.
