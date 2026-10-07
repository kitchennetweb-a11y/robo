# Compare the parent's ElevenLabs "Robot"-filtered lines (sfx/) with plain lines of the same voice (audio/).
# usage: blender -b -P voice_analysis.py
import aud, glob, os
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, N = 44100, 4096

def load(p):
    x = aud.Sound(p).rechannel(1).resample(SR, True).data()[:, 0].astype(np.float64)
    return x / (np.abs(x).max() + 1e-9)

def frames(x, n=N, hop=1024):
    w = np.hanning(n)
    f = [x[i:i + n] * w for i in range(0, len(x) - n, hop)]
    f = np.array(f); e = (f ** 2).mean(1)
    return f[e > e.max() * .05]  # voiced/loud frames only

def f0(fr):  # autocorrelation pitch, 70-400 Hz
    ac = np.fft.irfft(np.abs(np.fft.rfft(fr, 2 * N)) ** 2)[:N]
    lo, hi = SR // 400, SR // 70
    k = lo + np.argmax(ac[lo:hi]); return SR / k if ac[k] > .3 * ac[0] else None

def analyse(files):
    spec, pitches, cep_peaks, env_spec = [], [], [], []
    for p in files:
        x = load(p); F = frames(x)
        if not len(F): continue
        S = np.abs(np.fft.rfft(F, axis=1)); spec.append((S ** 2).mean(0))
        for fr, s in zip(F, S):
            v = f0(fr)
            if v: pitches.append(v)
            c = np.fft.irfft(np.log(s + 1e-9)); q0, q1 = int(SR * .0015), int(SR * .02)
            cep_peaks.append((q0 + np.argmax(c[q0:q1])) / SR * 1000)
        env = np.abs(x); k = 64; env = np.convolve(env, np.ones(k) / k, 'same')[::8]  # 5.5 kHz envelope
        E = np.abs(np.fft.rfft((env - env.mean()) * np.hanning(len(env)))); fr_e = np.fft.rfftfreq(len(env), 8 / SR)
        m = (fr_e > 15) & (fr_e < 400); env_spec.append((fr_e[m][np.argmax(E[m])], E[m].max() / (E[m].mean() + 1e-9)))
    return np.mean(spec, 0), np.array(pitches), np.array(cep_peaks), env_spec

robot = sorted(glob.glob(os.path.join(ROOT, 'sfx', '*.mp3')))
plain = sorted(glob.glob(os.path.join(ROOT, 'audio', '*.mp3')))[:40]
R, P = analyse(robot), analyse(plain)
freqs = np.fft.rfftfreq(N, 1 / SR)

print('== average spectrum, robot minus plain (dB), octave bands ==')
for lo in [62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]:
    m = (freqs >= lo) & (freqs < lo * 2)
    print(f'{lo:>6} Hz  robot {10*np.log10(R[0][m].mean()/R[0].sum()):6.1f}  plain {10*np.log10(P[0][m].mean()/P[0].sum()):6.1f}  diff {10*np.log10(R[0][m].mean()/P[0][m].mean()*P[0].sum()/R[0].sum()):6.1f}')
ratio = 10 * np.log10(R[0] / P[0]); ratio -= np.convolve(ratio, np.ones(31) / 31, 'same')
m = (freqs > 100) & (freqs < 6000); r = ratio[m] - ratio[m].mean()
ac = np.correlate(r, r, 'full')[len(r) - 1:]; ac /= ac[0]
k = 3 + np.argmax(ac[3:200]); print(f'comb check: ripple autocorr peak {ac[k]:.2f} at {k*SR/N:.0f} Hz spacing (>0.3 = fixed comb, delay {1000/(k*SR/N):.2f} ms)')
for name, (_, pit, cep, env) in (('robot', R), ('plain', P)):
    print(f'== {name} == pitch median {np.median(pit):.0f} Hz, spread (IQR/median) {np.subtract(*np.percentile(pit, [75, 25]))/np.median(pit):.3f}, voiced frames {len(pit)}')
    h = np.histogram(cep, bins=np.arange(1.5, 20.5, .25))
    top = np.argsort(h[0])[-3:][::-1]
    print('   cepstral peak (ms) most common:', [(round(h[1][i], 2), int(h[0][i])) for i in top], 'of', len(cep))
    print('   envelope modulation peak per file (Hz, prominence):', [(round(f), round(s, 1)) for f, s in env])
