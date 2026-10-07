// Robo's robot voice: a channel vocoder on a fixed-pitch buzz. Measured from the parent's ElevenLabs "Robot" lines
// (blender/voice_analysis.py, sfx/ vs audio/): pitch locked at ~129 Hz, original pitch gone, lows and highs boosted.
// Works on any AudioContext (live or Offline, so test.html can render and measure it).
export const VOC = { hz: 129, bands: 20, lo: 90, hi: 7500, q: 4.3, noise: .25, gain: 7, limit: -13, makeup: 1.15 };  // level/limit tuned so rms ≈ sfx lines, peak < 1
let absCurve, noiseBuf;
export function robotVoice(ctx, src, dest, dur) {
  absCurve ??= Float32Array.from({ length: 1025 }, (_, i) => Math.abs(i / 512 - 1));
  if (noiseBuf?.sampleRate !== ctx.sampleRate) {
    noiseBuf = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
    const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  }
  const t = ctx.currentTime, end = t + dur + .1;
  // buzz = sawtooth harmonics (1/n) with scattered phases: same pitch and tone, no spike each cycle (spikes = fuzz + clipping)
  const H = 64, re = new Float32Array(H), im = new Float32Array(H);
  for (let n = 1; n < H; n++) { const ph = n * n * 2.3999; re[n] = Math.cos(ph) / n; im[n] = Math.sin(ph) / n; }
  const buzz = ctx.createOscillator(); buzz.setPeriodicWave(ctx.createPeriodicWave(re, im)); buzz.frequency.value = VOC.hz;
  const hiss = ctx.createBufferSource(); hiss.buffer = noiseBuf; hiss.loop = true;  // keeps s/sh audible
  const hissG = ctx.createGain(); hissG.gain.value = VOC.noise;
  const carrier = ctx.createGain(); buzz.connect(carrier); hiss.connect(hissG).connect(carrier);
  const lim = ctx.createDynamicsCompressor();  // the buzz is spiky: squash it, then make up level to match sfx/ loudness
  lim.threshold.value = VOC.limit; lim.knee.value = 0; lim.ratio.value = 20; lim.attack.value = .002; lim.release.value = .1;
  const out = ctx.createGain(), makeup = ctx.createGain(); out.gain.value = VOC.gain; makeup.gain.value = VOC.makeup;
  out.connect(lim).connect(makeup).connect(dest);
  for (let i = 0; i < VOC.bands; i++) {
    const f = VOC.lo * (VOC.hi / VOC.lo) ** (i / (VOC.bands - 1));
    const band = input => { const b = ctx.createBiquadFilter(); b.type = 'bandpass'; b.frequency.value = f; b.Q.value = VOC.q; input.connect(b); return b; };
    // voice loudness in this band (rectify + smooth) drives the buzz's loudness in the same band
    const rect = ctx.createWaveShaper(); rect.curve = absCurve; band(src).connect(rect);
    const env = ctx.createBiquadFilter(); env.type = 'lowpass'; env.frequency.value = 40; rect.connect(env);
    const vca = ctx.createGain(); vca.gain.value = 0; env.connect(vca.gain);
    band(carrier).connect(vca); vca.connect(out);
  }
  buzz.start(t); hiss.start(t); buzz.stop(end); hiss.stop(end);
}
