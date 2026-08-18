# 08b — Extension: Counter-Drone Radar

> **Elective track B.** Requires the completed spine (`05-roadmap.md`,
> stages 1–12). Prerequisite reading: `08-extensions.md`.

---

## 1. Objective

Extend the spine into a **counter-UAS (counter-drone) radar** that detects and
tracks small, low, slow targets in clutter: fluctuating RCS, a 2-D CFAR
detector, ground-clutter rejection with MTI, and micro-Doppler drone
identification. The deliverable is a working "detect the drone, reject the
clutter, keep the track" pipeline.

This track hardens the **detection layer** — the layer the spine deliberately
keeps idealized (single clean target, plain peak detection).

## 2. Why (domain)

Drones are small, slow, and fly low — the **low-slow-small (LSS)** problem.
Their RCS is tiny, they hover (near-zero Doppler, indistinguishable from
clutter by velocity alone), and they're cheap enough to be everywhere. Counter-UAS
radar is a real, active domain (airports, critical infrastructure, defense) and
it exercises exactly the channel/detector realism the spine skips.

## 3. New physics / concepts (the deltas)

### 3.1 Fluctuating RCS (Swerling models)

A real target's radar cross-section fluctuates as its aspect changes. The
**Swerling models** parameterize this:

- **Swerling 0/5** — constant amplitude (what the spine assumes).
- **Swerling I** — scan-to-scan independent, exponential power (Rayleigh
  amplitude): `A = sqrt(chi2(2)/2)` scaled per pulse group.
- **Swerling III** — chi-square with 4 degrees of freedom (more benign).

Implement fluctuation in the **channel** (`channel.py`), not the receiver: the
echo amplitude for each CPI is drawn from the model's distribution. This makes
peak detection unreliable and is the *reason* CFAR exists.

### 3.2 Ground clutter and MTI

Ground returns pile up near **zero Doppler** and can bury a slow/hovering
drone. The classic fix is **moving target indication (MTI)** — a high-pass in
slow time. The simplest is the **pulse canceller**:

```
    2-pulse:   y[n] = x[n] − x[n−1]        (zeros DC/zero-Doppler)
    3-pulse:   y[n] = x[n] − 2x[n−1] + x[n−2]   (wider notch)
```

Add clutter to the channel as a stationary, high-power echo (fixed zero-Doppler
returns), then show the canceller rejects it while a moving target passes.

### 3.3 2-D CFAR detector

The spine's simple peak detection breaks under clutter + fluctuation. Replace
it with **cell-averaging CFAR (CA-CFAR)** over the range-Doppler map:

- For each cell under test (CUT): estimate local noise from reference cells
  around it (with guard cells to avoid target self-contamination).
- Threshold = `α · P̂_noise`; declare detection if `P_CUT > threshold`.
- `α` is set from the design `P_fa` and reference-cell count.

This is adaptive: a strong clutter cell raises its own local threshold, so it
doesn't fire — exactly the behavior you need in a real map.

### 3.4 Micro-Doppler (drone signature)

Propeller blades are rotating scatterers; they modulate the echo with
**micro-Doppler sidebands** around the body Doppler. Model the drone as the
body point-scatterer *plus* a few blade scatterers rotating at the propeller
frequency. A slow-time FFT / spectrogram of a single range bin then shows:

- a strong body Doppler line, plus
- blade-flash sidebands at `k·N_b·f_rot` (N_b blades, rotation rate `f_rot`).

This is the distinguishing feature between a drone and a bird or a ground
target — and it's a small, well-bounded addition to the channel model.

## 4. Parameters (delta table; spine otherwise unchanged)

| Parameter | Value | Note |
|---|---|---|
| Carrier `f_c` | 2.45 GHz (spine) | X-band (9.4 GHz) as a stretch: larger `f_d` per m/s, better slow-drone Doppler |
| Clutter power | +20–30 dB over noise | strong zero-Doppler return |
| Drone RCS | −20 to −10 dBsm | tiny; drives detection SNR |
| Swerling model | I (later III) | per-CPI fluctuating amplitude |
| Propeller `f_rot` | 50–150 Hz, 2–3 blades | micro-Doppler flash rate |
| `P_fa` (CFAR) | 1e-4 – 1e-6 | design point for the detector |

## 5. Architecture changes

### Python (`04-python-discipline.md` + deltas)

| Module | Change |
|---|---|
| `channel` | add `swerling` amplitude fluctuation; add `clutter` (stationary zero-Doppler returns); add `micro_doppler` (rotating blade scatterers) to the `Target`/channel model |
| `receiver` | add `mti(x_slow, n_pulses=2|3)` pulse canceller on the slow-time axis |
| `beamformer` → new `cfar.py` | `cfar2d(rd_map, n_guard, n_ref, p_fa)` → detection mask |
| `tracker` | reuse spine Kalman; add track scoring (require M-of-N detections before confirming a drone track) |
| `viz` | add spectrogram of a range bin (micro-Doppler view) |

### GNU Radio (`03-hardware.md` §2 style)

```
 RX chain (spine) ──► FIR MTI canceller (taps [1, −1] or [1, −2, 1])
                         │
                         ▼
                  Stream to Vector ──► FFT (Doppler) ──► CFAR (Python block) ──► Raster Sink
```

The MTI canceller is just a short FIR; CFAR is a small embedded Python block
(custom block or `vector_xxx` in GRC). Both are natural GNU Radio additions —
no new sources or sinks required.

## 6. Mini-roadmap

**B1 · Swerling fluctuation**
New: Swerling models, fluctuating RCS. Reuses: channel, receiver.
Task: implement Swerling 0/I/III amplitude in `channel`. Verify: the empirical
per-CPI amplitude distribution matches the model (histogram test). Observe the
spine's `detect_peaks` start missing detections at low SNR.

**B2 · 2-D CA-CFAR**
New: CUT/reference/guard cells, adaptive threshold, `P_fa` design.
Verify: measured `P_fa` within spec on noise-only frames; detection retained at
the drone cell at `SNR ≈ 15 dB`. Plot: RD map + detection mask.

**B3 · Ground clutter + MTI**
New: clutter model, pulse canceller. Verify: zero-Doppler clutter rejected by
the canceller; a 10 m/s drone remains detectable. Plot: RD map before/after MTI.

**B4 · Micro-Doppler**
New: rotating-blade scatterers, spectrogram. Verify: body Doppler line + blade
sidebands present in the range-bin spectrogram; a simulated "bird" (single
scatterer, no blades) lacks the sidebands. Plot: spectrogram.

**B5 · Integrated CUAS pipeline**
Task: wire B2–B4 into one chain (clutter → MTI → CFAR → confirm → track).
Verify: end-to-end — drone detected and tracked through clutter + fluctuation;
a stationary clutter target never births a confirmed track.

**B6 · (◇) X-band + slow-hover scenario** — move to 9.4 GHz, drop the drone to
`1 m/s` hovering near clutter; verify the CFAR + track confirmation still
reject clutter (exercise of the whole design).

## 7. Testing & verification

- Swerling amplitude distributions match theory (KS/histogram test).
- CFAR `P_fa` Monte Carlo within an order of magnitude of design.
- MTI transfer function: null at zero Doppler, pass at drone Doppler.
- Micro-Doppler sidebands appear only for the blade model.
- Integration: confirmed track count = true drone count across many seeded
  scenarios (no clutter tracks).

## 8. Portfolio artifacts

1. RD map with clutter, before/after MTI (B3)
2. CFAR detection mask over a fluctuating-target RD map (B2)
3. Micro-Doppler spectrogram: drone vs. bird (B4)
4. End-to-end CUAS track plot (drone tracked, clutter rejected) (B5)

## 9. Stretch goals

- X-band / hover scenario (B6).
- 3-pulse (or more) MTI + optimal (Doppler-notch) filtering comparison.
- Track classification: drone vs. bird vs. vehicle via micro-Doppler features.
- Multi-drone scenes with the track manager from track A (cross-track synergy).

## 10. Boundaries (not covered)

- No measured RCS or real drone EM signatures — models only.
- Simplified blade model (a few point scatterers, no aerodynamics).
- No EO/IR or RF-jamming fusion; detection and tracking only.
- Clutter is stationary ground clutter — no rain, birds, or building multipath.