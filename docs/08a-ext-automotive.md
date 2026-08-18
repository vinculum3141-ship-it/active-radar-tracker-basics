# 08a — Extension: FMCW Automotive Radar

> **Elective track A.** Requires the completed spine (`05-roadmap.md`,
> stages 1–12). Prerequisite reading: `08-extensions.md`.

---

## 1. Objective

Extend the spine into a **fast-chirp FMCW automotive radar** that detects and
tracks multiple vehicles: generate chirps, mix echoes, produce a range-Doppler
map, detect targets with 2-D CFAR, cluster them into objects, and maintain
tracks — the algorithmic heart of adaptive cruise control / AEB-style sensing.

The central teaching point: **the spine's 2-D processing survives almost
unchanged.** Only the receiver front-end changes (matched filter → mixer + FFT).
Everything downstream — CFAR, Kalman, array — is reused.

## 2. Why (domain)

Automotive radar (77 GHz, "fast-chirp" FMCW) is the mass-market version of the
same signal chain. It trades away long-range and raw power for robustness,
cost, and the ability to separate many nearby objects at fine resolution. It is
also the smallest conceptual delta from the spine, which makes it the ideal
first track.

> Note: 76–81 GHz is a licensed automotive band. Simulating in software is the
> *correct* approach for learning, not a compromise.

## 3. New physics / concepts (the deltas)

### 3.1 FMCW and the beat (dechirp) receiver

Transmit a linear chirp sweeping bandwidth `B` over chirp duration `Tc`
(rate `S = B/Tc`). The echo from a target at range `R` arrives delayed by
`τ = 2R/c`. **Mixing** the echo with a copy of the transmitted chirp
(homodyne / dechirp) produces a constant **beat tone**:

```
    f_b = S · τ = S · 2R/c         ⇒    R = c·f_b / (2·S)
```

This is the *replacement* for the matched filter: instead of correlating with
the transmit pulse, you multiply the echo by the conjugate chirp and measure
the resulting tone's frequency. One FFT (the "range-FFT") turns `f_b` into a
range profile — the same fast-time axis you already know, relabeled.

### 3.2 Range–velocity coupling and fast-chirp

A moving target shifts the beat: with `f_d = 2v/λ`,

```
    up-chirp:    f_b = 2·S·R/c − f_d
    down-chirp:  f_b = 2·S·R/c + f_d
```

On a single chirp, range and velocity are coupled (you cannot tell which
caused the shift). Two fixes, both teachable:

- **Triangular modulation** — alternate up/down chirps and solve the pair:
  `R = c(f_up + f_down)/(4S)`, `v = λ(f_down − f_up)/4`.
- **Fast-chirp** (what modern automotive radars use) — repeat many short
  identical chirps; the range-FFT per chirp, then a **Doppler-FFT across
  chirps**, is *exactly* the spine's 2-D structure (fast-time axis → range,
  chirp index → velocity). This is the clean bridge back to your
  range-Doppler map.

### 3.3 Resolution / limits

```
    ΔR = c/(2B)                (same as pulse radar — depends only on B)
    Δv = λ/(2·N_c·Tc)
    v_max = λ/(4·Tc)
    R_max = c·fs/(4·S)         (beat freq must stay below fs/2)
```

### 3.4 Detection-to-object layers (new, post-map)

- **2-D CFAR** (already your stretch concept) — becomes the primary detector.
- **Clustering** — group CFAR cells into object blobs (connected components or
  DBSCAN); emit one centroid per object.
- **Track management** — gating + nearest-neighbor association, track
  birth/death, so the tracker survives a changing vehicle count.

## 4. Parameters (illustrative short-range)

| Parameter | Value | Note |
|---|---|---|
| Carrier `f_c` | 77 GHz | licensed band → sim only; λ ≈ 3.9 mm |
| Bandwidth `B` | 1 GHz | ΔR = 0.15 m — vehicle-level resolution |
| Chirp duration `Tc` | 20 us | S = 50 MHz/us |
| Sampling rate `fs` | 40 MHz | set by S and required R_max |
| Chirps per frame `N_c` | 128 | Δv ≈ 0.76 m/s, v_max ≈ 48.8 m/s |

> Trade-off to explore (make it a lab): longer `Tc` improves `R_max` but
> shrinks `v_max`; short-chirp designs trade the opposite way. Modern radars
> manage both with ambiguity resolution — a natural stretch.

## 5. Architecture changes

### Python (`04-python-discipline.md` + deltas)

| Module | Change |
|---|---|
| `signal_gen` | add `fmcw_chirp(cfg)`; chirp train replaces pulse train |
| `channel` | unchanged — delay/attenuation/noise already model the echo |
| `receiver` | add `dechirp(rx, tx_chirp)` = multiply by conjugate, then **range-FFT** per chirp (replaces matched filter) |
| `doppler` | reuse `range_doppler_map` with the chirp index as slow time (rename axes: range bins, velocity) |
| `beamformer` | new: `cfar2d(rd_map, n_guard, n_ref, p_fa)` |
| new `clustering.py` | connected-components/DBSCAN → object centroids |
| `tracker` | add gating + nearest-neighbor association + birth/death (a small `TrackManager`), reusing `KalmanTracker` |

### GNU Radio (`03-hardware.md` §2 style)

```
 Chirp Generator (ramp-driven VCO) ──► Throttle ──► QT Sink
      │                                          (TX)
      ▼
 Delay ──► Noise ──► Add ──► Multiply (× conj(TX chirp)) ──► Low Pass ──► Stream to Vector
                                                                             │
                                                    Range-FFT per chirp ◄────┘
                                                    Doppler-FFT across chirps
                                                              │
                                                              ▼
                                                  Raster Sink (RD map) / QT Sinks
```

Block swaps vs. the spine: **FIR (matched filter) → Multiply + Low Pass**
(the mixer), and the pulse-gate source becomes a chirp source. Everything
after the FFT is unchanged.

## 6. Mini-roadmap

**A1 · Chirp + dechirp receiver**
New: beat-tone concept, mixer. Reuses: waveform gen, channel, FFT.
Task: `fmcw_chirp`, `dechirp`; verify `f_b → R` for a static target to < 1
range bin (`R_max = 60 m` case). Plot: beat spectrum.

**A2 · Range-FFT → range profile**
New: fast-time range axis for FMCW. Verify `ΔR = c/(2B)`; two targets 5 m
apart resolve. Plot: range profile.

**A3 · Doppler-FFT across chirps → RD map**
New: chirp-index slow time; range–velocity coupling. Reuses: `doppler`.
Verify: moving target's velocity bin matches truth; show how a *single*
triangular chirp would have coupled the two. Plot: RD map.

**A4 · 2-D CFAR + clustering**
New: cell-averaging CFAR, clustering. Verify: false-alarm rate near the
design `P_fa`; cluster count = true target count in a 3-vehicle scene.
Plot: RD map with detected cells + centroids.

**A5 · Track management**
New: gating, association, birth/death. Reuses: `KalmanTracker`.
Verify: tracks persist across a frame where a vehicle briefly overlaps
another (no track swap); a new vehicle births a track; a leaving vehicle's
track dies. Plot: tracked object trajectories.

**A6 · (◇) Sensor-fusion stretch** — simulate a camera lane model and gate
radar tracks against it; report "validated" tracks.

## 7. Testing & verification

- Beat-frequency → range equation holds (analytic answer test).
- Range/velocity extraction within `ΔR` / `Δv/2`.
- CFAR `P_fa` within spec at high SNR (Monte Carlo over many seeded frames).
- Track-manager unit tests: gating decision, association correctness on a
  hand-built crossing scenario, birth/death timing.

## 8. Portfolio artifacts

1. FMCW beat spectrum (A1)
2. Automotive range-Doppler map, 3 vehicles (A3)
3. CFAR detections + clustered centroids on the RD map (A4)
4. Tracked vehicle trajectories with birth/death (A5)

## 9. Stretch goals

- Triangular-chirp range/velocity disambiguation (vs. fast-chirp).
- MIMO virtual array: 2 TX × 4 RX → 8 virtual elements for finer angle.
- Ambiguity-resolved long-range mode (higher `v_max`).
- Simulated radar-camera fusion (A6).

## 10. Boundaries (not covered)

- No real 77 GHz hardware (licensed band; sim-only).
- Simplified MIMO (no per-TX waveform separation beyond basic orthogonal chirps).
- No multipath, weather, or pedestrian micro-Doppler classification.
- Object tracking is centroid-based — no shape/length estimation.