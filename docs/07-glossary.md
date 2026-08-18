# 07 — Glossary & Equations

Quick reference for terms and the key equations used throughout the project.
Cross-referenced from `01-physics.md`.

---

## Terms

| Term | Meaning |
|---|---|
| **Pulse radar** | Radar that transmits short bursts, then listens in the quiet interval |
| **Monostatic** | TX and RX co-located (shared antenna/position) |
| **Bistatic** | TX and RX at different locations |
| **PRI** | Pulse repetition interval — time between pulse starts |
| **PRF** | Pulse repetition frequency = `1/PRI` |
| **Duty cycle** | Fraction of time the transmitter is on: `τ/T` |
| **Pulse width (τ)** | Duration of one transmitted burst |
| **Bandwidth (B)** | Frequency range of the waveform |
| **Chirp / LFM** | Linear frequency-modulated pulse; enables pulse compression |
| **Pulse compression** | Matched filtering that turns a long chirp into a short spike |
| **Matched filter** | Filter maximizing SNR for a known signal in white noise; = correlation |
| **Range bin** | One sample of fast time, mapped to a range: `ΔR = c/(2·fs)` |
| **Fast time** | Time within a single pulse (maps to range) |
| **Slow time** | Time across pulses (pulse index; maps to Doppler/velocity) |
| **CPI** | Coherent processing interval — the `N` pulses used for one Doppler FFT |
| **Doppler shift (f_d)** | Frequency shift of the echo due to radial target motion |
| **Range-Doppler map** | 2-D plot: range vs velocity (from fast-time delay × slow-time FFT) |
| **Kalman filter** | Optimal recursive estimator blending prediction and measurement |
| **ULA** | Uniform linear array — elements equally spaced on a line |
| **Steering vector a(θ)** | Per-element phase offsets for a wavefront from angle θ |
| **Beam pattern** | `|wᴴa(θ)|²` — array gain vs angle |
| **Grating lobe** | Extra main lobe when element spacing `d > λ/2` |
| **DOA** | Direction-of-arrival estimation |
| **Bartlett scan** | Beamformer power scan: `P(θ) = |a(θ)ᴴx|²` |
| **Capon / MVDR** | Minimum-variance distortionless response beamformer |
| **LCMV** | Linearly constrained minimum variance beamformer (used for nulling) |
| **Null steering** | Forcing zero array gain at an interferer direction |
| **CFAR** | Constant false alarm rate detector — adaptive detection threshold |
| **SDR** | Software-defined radio (HackRF, USRP, LimeSDR) |
| **Baseband** | Signal after down-conversion; complex I/Q representation |
| **Hermitian transpose (ᴴ)** | Conjugate transpose of a vector/matrix |

---

## Key equations

### Radar / range

```
R = c · τ_delay / 2
R_unamb = c · T / 2
ΔR (rect pulse) = c·τ / 2
ΔR (chirp) = c / (2·B)
```

### Doppler

```
f_d = 2·v / λ ,   λ = c / f_c
v = λ·f_d / 2
Δv = λ / (2·N·T)
v_max = λ / (4·T)
```

### Array

```
Δφ = 2π·d·sin(θ) / λ
a(θ) = [1, e^{jΔφ}, ..., e^{j(M-1)Δφ}]ᵀ
y = wᴴ · x
P_bartlett(θ) = |a(θ)ᴴ x|²
w_capon = R̂⁻¹ a(θ) / (a(θ)ᴴ R̂⁻¹ a(θ))
```

### LCMV nulling

```
min  wᴴ R̂ w    s.t.   Cᴴ w = g
C = [a(θ_t), a(θ_i)],   g = [1, 0]
w_lcmv = R̂⁻¹ C (Cᴴ R̂⁻¹ C)⁻¹ g
```

### Kalman

```
Predict:  x̂ = F·x ,   P = F·P·Fᵀ + Q
Update:   K = P·Hᵀ (H·P·Hᵀ + R)⁻¹
          x = x̂ + K·(z − H·x̂)
          P = (I − K·H)·P
```

---

## Numbers worth remembering (baseline config)

| Quantity | Value |
|---|---|
| `λ` at 2.45 GHz | 0.1224 m |
| `f_d` per m/s | 16.3 Hz |
| `Δv` (N=64, T=1 ms) | 0.96 m/s |
| `v_max` (T=1 ms) | 30.6 m/s |
| `ΔR` at B=5 MHz | 30 m |
| Round-trip delay at 1 km | 6.67 us = 133 samples @ 20 MHz |
| Duty cycle (τ=20 us, T=1 ms) | 2% |