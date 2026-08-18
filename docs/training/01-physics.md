# 01 — Physics

Intuition-first explanations with the governing equations. No full
derivations — for those, see the references in `07-glossary.md`. Every section
maps to roadmap stages in `05-roadmap.md`.

---

## 1. Monostatic pulse radar (stages 1–2)

An **active radar** transmits its own energy. **Monostatic** means the
transmitter and receiver share a location (often an antenna). A **pulse radar**
transmits short bursts of energy separated by quiet intervals.

- **Pulse width** `τ` — how long the burst lasts. Controls range resolution
  for a plain (unmodulated) pulse.
- **Pulse repetition interval (PRI)** `T` — time between pulse starts. The
  reciprocal is the **pulse repetition frequency** `PRF = 1/T`.
- **Duty cycle** `D = τ/T` — fraction of time the transmitter is on. At
  `τ = 20 us` and `T = 1 ms`, `D = 2%`.

**Why pulse?** You can't hear an echo while still shouting. Pulse operation
creates the quiet window in which the faint echo is received.

### Key equations

```
Range from round-trip time:
    R = c · τ_delay / 2

Unambiguous range (max range not aliased by the next pulse):
    R_unamb = c · T / 2
```

With `T = 1 ms`, `R_unamb = 150 km` — comfortably above the ~km-scale targets
we simulate, so no range aliasing.

**Radar range equation** (orders-of-magnitude tool — not needed for the sim,
but gives intuition for why echoes are tiny):

```
    P_r = P_t · G² · λ² · σ / ( (4π)³ · R⁴ )
```

`σ` is the radar cross section; the `1/R⁴` term is why echo power collapses
with range.

### Parameter rationale — why these numbers

The baseline parameters form a self-consistent set where round, convenient
values also keep the DSP stable, and the deliberately "inconvenient" one
(`40 m/s` target vs. the `30.6 m/s` unambiguous velocity limit) creates the
teaching exercise. They are fixed here so all stages, tests, and flowgraphs
agree.

| Parameter | Value | Rationale |
|---|---|---|
| Carrier frequency `f_c` | 2.45 GHz | ISM band → legal over-the-air test later. λ ≈ 12.2 cm → a half-wave array (`d = λ/2 ≈ 6 cm`) is bench-sized, so a 4-element ULA is physically plausible. Doppler constant `2/λ ≈ 16.3 Hz` per m/s → velocities give clearly observable slow-time phase rotations. |
| Bandwidth `B` | 5 MHz | `ΔR = c/(2B) = 30 m` → separates km-scale targets without fine bins. At `fs = 20 MHz`, `B = fs/4`, comfortably inside Nyquist (`fs/2 = 10 MHz`). With `τ = 20 us`, `τ·B = 100` → strong pulse-compression SNR gain. |
| Pulse width `τ` | 20 us | Duty cycle `τ/T = 2%` at PRI 1 ms → realistic for a low-power radar. 400 samples per pulse at 20 MHz → tidy matrix shapes. |
| PRI `T` | 1 ms | `R_unamb = cT/2 = 150 km` → no range aliasing at our ~km targets, so learners never fight an artifact. Sets `v_max = λ/(4T) ≈ 30.6 m/s`. |
| Sampling rate `fs` | 20 MHz | Nyquist-safe for the 5 MHz signal. Round-trip to 1 km = 6.67 us = 133 samples → range bin ≈ 7.5 m, fine enough to resolve 30 m cells. |
| Pulses per CPI `N` | 64 | Power of two → clean FFT. `Δv = λ/(2NT) ≈ 0.96 m/s` → velocities readable to a bin or two. |

Note the deliberate friction: with `v_max ≈ 30.6 m/s`, the baseline target at
`40 m/s` is **aliased**. That is intentional — Stage 4 uses it to teach Doppler
ambiguity (raise `PRF` or lower `f_c`, watch the map unwrap). See
`05-roadmap.md` Stage 4.

### The measurement loop (stage 2)

For a target at range `R(t)` moving at radial velocity `v`:

1. Compute `R(t) = R₀ + v·t`.
2. Round-trip delay `τ_delay = 2·R(t)/c`.
3. Place a scaled copy of the transmitted pulse at that delay in the received
   signal.
4. Add attenuation (`1/R⁴` or a simpler `1/R²` for teaching) and noise.

This is the **channel model** — in GNU Radio, the delay and noise blocks do the
same job.

---

## 2. Matched filtering and range estimation (stage 3)

The receiver sees the transmitted pulse buried in noise. The **matched filter**
is the linear filter that maximizes output SNR for a known signal in white
noise: the filter's impulse response is the time-reversed, conjugated transmit
signal.

For real signals, matched filtering *is* **correlation**:

```
    y(t) = ∫ s_received(u) · s_transmit(u − t) du
```

In NumPy/SciPy:

```python
y = signal.correlate(rx, tx, mode="same")
```

The **peak** of `y` occurs at the round-trip delay. Convert delay to range:

```
    R = c · τ_peak / 2
```

### Why matched filtering works

It coherently sums the signal's energy (`∝ τ`) while noise sums incoherently
(`∝ sqrt(τ)`), giving an SNR gain of `τ·B` (time–bandwidth product).

### Range resolution

- Plain rectangular pulse: `ΔR = c·τ/2` — with `τ = 20 us`, that's **3 km**.
  Too coarse to separate nearby targets.
- Frequency-modulated pulse (next section): `ΔR = c/(2B)` — with
  `B = 5 MHz`, that's **30 m**.

This is the whole reason we move to LFM chirps.

---

## 3. Pulse compression with an LFM chirp (stage 1, extension)

A **linear frequency modulation (LFM) chirp** sweeps the carrier frequency
linearly across the pulse:

```
    s(t) = rect(t/τ) · exp(j·π·k·t²)
```

with chirp rate `k = B/τ`. The **time–bandwidth product** `τ·B` is large
(e.g. `20 us × 5 MHz = 100`).

The matched filter compresses the long, low-power chirp into a short spike of
width `~1/B`. You get the energy of a long pulse with the resolution of a short
one.

```
    ΔR = c / (2·B)          # 30 m at B = 5 MHz
```

Sidelobe levels are `~-13 dB` for a rectangular window; apply a window
(Taylor/Hamming) on transmit or in the filter to trade main-lobe width for
lower sidelobes.

Generate in SciPy:

```python
t = np.arange(pulse_samples) / fs
chirp = scipy.signal.chirp(t, f0, t[-1], f1, method="linear", phi=-90)
```

For a complex baseband model, generate the analytic chirp directly with
`exp(j·π·k·t²)` and use the **conjugated, time-reversed** version as the
matched filter.

---

## 4. Doppler and velocity estimation (stage 4)

A target moving with radial velocity `v` compresses (approaching) or stretches
(receding) the received waveform. Over many pulses, the *phase* of the echo
rotates from pulse to pulse — this is the **Doppler shift**:

```
    f_d = 2·v / λ ,        λ = c / f_c
```

With `f_c = 2.45 GHz`, `λ ≈ 12.2 cm`, so `f_d ≈ 16.3 Hz per m/s`.

**Why per-pulse, not per-sample?** Within one 20 us pulse, the target moves
a negligible fraction of a wavelength, so the *fast-time* (within-pulse) signal
looks static. Between pulses (`T = 1 ms`), the target moves enough to rotate
the phase measurably. So:

- **Fast time** → delay → range.
- **Slow time** (pulse index) → phase rotation → Doppler → velocity.

### Slow-time FFT (range-Doppler map)

Stack the `N = 64` matched-filter outputs into a matrix
`[range bins] × [pulses]`. FFT along the pulse axis. Each range bin now shows
a spectrum of Doppler shifts:

```
    v = λ · f_d / 2
```

### Resolution and ambiguity

```
    Velocity resolution:      Δv = λ / (2 · N · T)
    Max unambiguous velocity: v_max = λ / (4 · T)      (±)
```

With `N=64, T=1 ms, λ=0.122 m`: `Δv ≈ 0.95 m/s`, `v_max ≈ 30.6 m/s`. A target
at `40 m/s` would alias — a good exercise (stage 4) is to raise `PRF` or lower
`f_c` and watch the map unwrap. (True velocity can be disambiguated with
multiple PRFs.)

---

## 5. Target tracking with a Kalman filter (stage 5)

The range–Doppler map gives **detections** (measurements with noise). Tracking
produces a *filtered* state estimate that is smoother than any single
measurement.

**State vector** for a 1-D radial track:

```
    x_k = [R, v]ᵀ
```

**Motion model** (constant velocity):

```
    x_{k+1} = F·x_k ,    F = [[1, Δt], [0, 1]]
```

**Measurement model:**

```
    z_k = H·x_k + w_k ,   H = [[1, 0], [0, 1]]   (measure R and v)
```

**Kalman update** (two steps):

1. **Predict**: `x̂ = F·x`, `P = F·P·Fᵀ + Q`
2. **Update**: `K = P·Hᵀ (H·P·Hᵀ + R)⁻¹`,
   `x = x̂ + K(z − H·x̂)`, `P = (I − K·H)·P`

`Q` = process noise (how much the model can be wrong), `R` = measurement noise
(how noisy detections are). Tuning `Q/R` is the craft.

The key idea: the Kalman filter **blends** prediction (model) and measurement
(sensor) with weights that adapt to their relative uncertainties.

---

## 6. Phased-array basics (stage 6)

An antenna **array** samples the wavefront at `M` positions. A wave arriving
from angle `θ` reaches each element with a **phase offset** proportional to the
projected path difference.

For a uniform linear array (ULA) with spacing `d`:

```
    Δφ = 2π · d · sin(θ) / λ
```

The **steering vector** encodes the phase of a signal from `θ` at every element:

```
    a(θ) = [1, exp(j·Δφ), exp(2j·Δφ), ..., exp(j·(M−1)·Δφ)]ᵀ
```

**Beamforming** = a weighted sum of the element signals. With weights
`w = a(θ_target)` (conjugated), signals from `θ_target` add constructively and
the array gains sensitivity there — a **beam**:

```
    y = wᴴ · x          (Hermitian inner product)
```

**Beam pattern** = `|wᴴ a(θ)|²` swept over all `θ`. It shows the main lobe
(toward the target) and sidelobes. With `M` elements you get `~M` main-lobe
widths of steering.

**Grating lobes:** if `d > λ/2`, extra main lobes appear at other angles.
Standard choice: `d = λ/2`.

---

## 7. Direction-of-arrival (stage 7)

Given array snapshots, estimate where energy comes from.

**Bartlett (delay-and-sum) beamscan** — sweep `θ`, beamform, and find the
angle with maximum output power:

```
    P(θ) = |a(θ)ᴴ x|²
```

**Capon (MVDR)** — improves resolution by nulling all other directions while
passing the look direction, using the sample covariance matrix `R̂`:

```
    w_capon = R̂⁻¹ a(θ) / (a(θ)ᴴ R̂⁻¹ a(θ))
```

Capon gives sharper peaks and is the bridge to null steering. For the first
pass, Bartlett is enough to *find* the target angle and the interferer angle.

---

## 8. Adaptive null steering / interference cancellation (stages 8–11)

An **interferer** at angle `θ_i` is a strong, spatially-localized signal that
can mask the target in the range–Doppler map. Because it arrives from a known
direction, we can place a **null** (zero gain) there.

**LCMV (linearly constrained minimum variance)** solves:

```
    minimize   wᴴ R̂ w
    subject to Cᴴ w = g
```

Constraint matrix `C` holds steering vectors; `g` the desired responses:

```
    C = [a(θ_target), a(θ_interferer)]
    g = [1, 0]
```

- `wᴴ a(θ_target) = 1` → unit gain toward the target.
- `wᴴ a(θ_interferer) = 0` → null on the interferer.

**Closed-form solution:**

```
    w_lcmv = R̂⁻¹ C (Cᴴ R̂⁻¹ C)⁻¹ g
```

This is the heart of the advanced portion. The resulting antenna pattern shows
a main lobe at the target and a **deep null** at the interferer angle —
an excellent portfolio visual.

**Extension (moving interferer):** recompute `w_lcmv` periodically as `θ_i`
drifts. Now the receiver *tracks* the null adaptively — the same math, updated
over time.

---

## Where this lives in the pipeline

| Physics | Pipeline stage | Roadmap |
|---|---|---|
| Range from round-trip delay | Matched filter → peak → `R = cτ/2` | 1–3 |
| Doppler shift | Slow-time FFT | 4 |
| State estimation | Kalman filter | 5 |
| Phase offsets across elements | Steering vectors | 6 |
| Angle from array snapshots | Bartlett/Capon scan | 7 |
| Spatial filtering | Beamforming + LCMV nulling | 8–11 |
| Streaming realization | GNU Radio flowgraph | 12 |