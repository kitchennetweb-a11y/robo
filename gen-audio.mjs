// Generate audio/<id>.mp3 for every line in phrases.json with ElevenLabs. Skips files that already exist.
// PowerShell:  $env:ELEVENLABS_API_KEY="..."; node gen-audio.mjs
// Voice defaults to Robo's voice (same one as sfx/). The robot filter is applied by the app at playback, not here.
// Optional: ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL (default eleven_v3, which speaks Persian).
import fs from 'node:fs';
const { ELEVENLABS_API_KEY: key, ELEVENLABS_VOICE_ID: voice = '8Ebkg5uUcbSbeqGucAoR', ELEVENLABS_MODEL: model = 'eleven_v3' } = process.env;
if (!key) { console.error('Set ELEVENLABS_API_KEY first.'); process.exit(1); }
fs.mkdirSync('audio', { recursive: true });
for (const p of JSON.parse(fs.readFileSync('phrases.json', 'utf8'))) {
  const file = `audio/${p.id}.mp3`;
  if (fs.existsSync(file)) continue;
  const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice}?output_format=mp3_44100_64`, {
    method: 'POST', headers: { 'xi-api-key': key, 'content-type': 'application/json' },
    body: JSON.stringify({ text: p.fa, model_id: model }),
  });
  if (!res.ok) { console.error('FAIL', p.id, res.status, await res.text()); continue; }
  fs.writeFileSync(file, Buffer.from(await res.arrayBuffer()));
  console.log('ok', p.id, p.fa);
}
