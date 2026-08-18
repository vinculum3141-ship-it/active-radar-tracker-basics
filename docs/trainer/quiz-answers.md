# Trainer — Weekly Quiz Answers

Instructor key for `docs/training/06-training.md` §5 (weekly self-check
quizzes). Give full credit for the number plus a correct derivation; accept
±5% where noted. All constants come from `docs/training/01-physics.md`.

**Reference constants:** `c = 3e8`, `fc = 2.45 GHz` → `lambda = 0.12245 m`,
`fs = 20 MHz`, `PRI = 1 ms` (PRF = 1000 Hz), `tau = 20 us`, `N = 64`.

## Week 1

**1. Duty cycle** — `tau / T = 20e-6 / 1e-3 = 2%`. (The quiet window is why
a pulse radar can transmit and receive on one antenna — echoes return in the
98% dead time.)

**2. Round-trip delay** — `t_d = 2R/c = 2·1000/3e8 = 6.67 us`;
`n = t_d · fs = 6.67e-6 · 20e6 = 133.3 -> 133 samples`.
(Consistent with `n_delay` in the flowgraphs.)

**3. Factor of 2** — the wave must travel out **and** back; delay is
`2R/c`, so `R = c·t/2`.

**4. Range resolution** — LFM: `delta_R = c/(2B) = 3e8/(2·5e6) = 30 m`.
Rectangular 20 us: `c·tau/2 = 3e8·20e-6/2 = 3000 m`. LFM wins because
bandwidth (not pulse width) sets resolution; pulse compression recovers the
short-pulse resolution from a long, high-energy chirp.

## Week 2

**5. Doppler shift** — `f_d = 2v/lambda = 2·40/0.12245 = 653.3 Hz`
(≈ 650 Hz, within ±5%).

**6. Velocity resolution / max** —
`delta_v = lambda/(2·N·T) = 0.12245/(2·64·1e-3) = 0.96 m/s`;
`v_max = lambda/(4·T) = 0.12245/0.004 = 30.6 m/s`.

**7. Ambiguity** — Yes: `40 > v_max = 30.6 m/s`. The Doppler FFT can only
represent ±PRF/2 = ±500 Hz; `f_d = 653 Hz` folds to `653 - 1000 = -347 Hz`,
so the target appears at `-21.2 m/s` (approaching, not receding). This is
exactly what the `radar_doppler.grc` test case demonstrates.

**8. Kalman Q and R** — `Q` too big: filter assumes large process noise,
trusts measurements, track becomes jittery/over-responsive. `R` too big:
filter assumes large measurement noise, trusts the model, track becomes
sluggish/laggy behind the truth.

## Week 3

**9. Steering vector at 30°** — `a_m = e^{j·2pi·(m·d/lambda)·sin(theta)}`
with `d = lambda/2`: `a(30°) = [1, e^{j pi/2}, e^{j pi}, e^{j 3pi/2}] =
[1, +j, -1, -j]`.

**10. Grating lobes at d = lambda** — array manifold repeats when
`d·sin(theta) = n·lambda`; with `d = lambda`, a second lobe appears at the
angle where `sin(theta) = 1` (endfire) replicating the main lobe. Rule of
thumb: `d <= lambda/2` to avoid them.

**11. Bartlett vs Capon** — Capon (MVDR) weights from the data covariance
(`w = R^-1 a(theta) / (a^H R^-1 a)`) to null what the data says is there,
so it resolves closer angles than Bartlett (delay-and-sum), whose width is
set by the array aperture alone. Bartlett is robust with few snapshots;
Capon needs a well-estimated `R` (see L3).

## Week 4

**12. LCMV** — `w = R^-1 C (C^H R^-1 C)^-1 g` with
`C = [a(+20°), a(-30°)]`, `g = [1, 0]^T`. This forces `w^H a(+20°) = 1`
and `w^H a(-30°) = 0` (null). Numerically:
`w = [0.224-0.042j, 0.083+0.269j, -0.105+0.261j, -0.220-0.060j]`
(null depth 40+ dB). Reproduce with `uv run grc/gen_weights.py`.

**13. Same angle** — the two constraints conflict: gain 1 and null 0 cannot
both hold at one angle; the least-squares solution trades them off (shallow
null / reduced gain). This is why angular resolution (beam width) matters —
you can only null an interferer you can separate in angle.

**14. Null before matched filter** — spatial processing operates on the
element (pre-compression) data, so the interferer is suppressed before the
per-channel coherent matched filter. Cleaner architecturally (one array
stage, then the compression chain) and keeps a strong interferer from
exciting the matched filter / ADC chain.

## Week 5

**15. Block → code mapping** —
`blocks_delay` + `analog_noise_source` + `blocks_add` = `channel`/
`simulate_channel`; `fir_filter_xxx` (taps = conj,time-reversed chirp) =
`receiver`/`matched_filter`; `blocks_keep_m_in_n` + the `range_doppler` epy
block = `doppler`/`range_doppler_map`. The `radar_taps` epy module =
`signal_gen`.

**16. Swap for a HackRF** — replace `blocks_vector_source` (TX) and the
delay/noise simulation (RX) with an Osmocom SDR source at the same
`fs`/center frequency; drive `taps` and `n_delay` from the real
configuration; the matched filter and Doppler chain stay identical. Real
timing means the throttle block goes away.

**17. Why one HackRF can't do the array** — an array needs four
*simultaneous, coherent* receive channels: a shared/local oscillator and
phase-aligned sampling. A single-channel SDR has one RF chain; you'd need
four synced receivers (shared LO/clock) or a multi-channel SDR.
`radar_array.grc` keeps four parallel complex streams to model exactly that.