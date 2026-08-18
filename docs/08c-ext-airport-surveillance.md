# 08c — Extension: Airport Tower Surveillance

> **Elective track C.** Requires the completed spine (`05-roadmap.md`,
> stages 1–12). Prerequisite reading: `08-extensions.md`. This is the largest
> delta of the three tracks — expect it to take roughly two spine-weeks' worth
> of effort.

---

## 1. Objective

Extend the spine into an **airport tower surveillance radar** (ASDE-X-style
surface movement / terminal monitoring): many aircraft on a runway/taxiway
layout, super-resolution angle estimation, nonlinear tracking through turns,
and track management at scale — plus Doppler disambiguation for fast jets.

This track pushes the **tracking/estimation layer** to its limit: more targets,
finer angles, harder motion, and a real association problem.

## 2. Why (domain)

Airport surface surveillance must track dozens of aircraft and vehicles
simultaneously, separate aircraft on adjacent taxiways (fine angular
resolution), follow turns onto runways (nonlinear motion), and not swap
tracks between crossing targets. It is the classic "many targets, hard
association" problem — and it reuses almost everything from the spine, which
is what makes it achievable.

## 3. New physics / concepts (the deltas)

### 3.1 Super-resolution DOA: MUSIC / ESPRIT

Capon (spine) resolves angles down to roughly a beamwidth. Two aircraft on
adjacent taxiways can be closer than that. **MUSIC** uses the eigenstructure of
the array covariance to separate sources much finer than the beamwidth:

```
    R̂ = (1/N) Σ x xᴴ                 (sample covariance)
    R̂ = E_s Λ_s E_sᴴ + E_n Λ_n E_nᴴ   (signal / noise subspaces)
    P_music(θ) = 1 / ( a(θ)ᴴ E_n E_nᴴ a(θ) )
```

The noise-subspace vectors are orthogonal to the steering vectors of true
sources, so the spectrum spikes exactly at source angles. **ESPRIT** uses the
shift-invariance of a ULA to solve angles directly (no scan) — worth a
side-by-side. Both need the number of sources `D` estimated (e.g., via the
eigenvalue gap or AIC/MDL).

### 3.2 Coordinated-turn motion + EKF/UKF

Aircraft turn at roughly constant speed with a turn rate `ω` — the spine's
constant-velocity model fails during turns. Use a **coordinated-turn (CT)
model** with state `[x, vx, y, vy, ω]` and a **nonlinear filter**:

- **EKF** — linearize the CT process model around the current estimate
  (Jacobian). Simple, but linearization can drift on tight turns.
- **UKF** — propagate sigma points through the nonlinear model, no Jacobians;
  more robust. Either is a clear upgrade over the spine Kalman.

Key teaching point: the *same* predict/update skeleton; only the state model
and the nonlinearity handling change.

### 3.3 Track management at scale

With dozens of targets you need more than one Kalman filter:

- **Gating** — accept a measurement only if the Mahalanobis distance
  `D² = νᵀ S⁻¹ ν < g²` (innovation `ν`, innovation covariance `S`).
- **Association** — nearest-neighbor (then JPDA for ambiguous cases) between
  gates and tracks; handles the hard part: *which* measurement goes to *which*
  track when two aircraft cross.
- **Birth / death** — M-of-N confirmation logic starts tracks, N-miss logic
  deletes them; a target list is the output.

### 3.4 Multi-PRF Doppler disambiguation

Jets reach 200+ m/s but the spine's `v_max = λ/(4T) ≈ 30.6 m/s`. Stagger two
(or three) PRFs and solve the aliased Doppler with the **Chinese Remainder
Theorem**: each PRF gives a fold, and the true `f_d` is the value consistent
with all folds. This turns your stage-4 "aliasing gotcha" into a solved
engineering problem.

### 3.5 Waypoint traffic generator

A simple airport map (runway + taxiways as waypoint polylines) drives many
targets along routes with takeoff/landing/taxi segments. This is *simulator*
content (new `traffic.py`), not DSP — it feeds the whole chain realistic,
coordinated-turn motion.

## 4. Parameters (delta table)

| Parameter | Value | Note |
|---|---|---|
| Carrier `f_c` | 9.4 GHz (X-band) | surface-movement band; λ ≈ 3.2 cm, good `f_d` per m/s |
| Elements `M` | 8 | array resolution for taxiway separation |
| `N` pulses | 128 | more Doppler bins for track-side clarity |
| PRFs | 2 staggered (e.g. 3.0 / 4.5 kHz) | CRT disambiguation of jet speeds |
| Targets | 10–20 aircraft + vehicles | scale driver |
| Turn rate `ω` | 0–6 deg/s per route | nonlinearity driver |

## 5. Architecture changes

### Python (`04-python-discipline.md` + deltas)

| Module | Change |
|---|---|
| new `traffic.py` | airport map, waypoint routes, target generation (feeds `channel`) |
| `array` | extend to `M=8`; add `source_count_est` (eigenvalue gap / MDL) |
| `beamformer` | add `music_spectrum`, `esprit_angles` (beside Capon) |
| `receiver` | add `multi_prf` disambiguation (CRT) across staggered PRFs |
| new `tracking.py` | `CoordinatedTurnEKF` / `UKF`; `TrackManager` (gating, NN/JPDA, M-of-N birth, N-miss death) |
| `viz` | airport-map overlay of tracks; MUSIC spectrum; association gating view |

### GNU Radio (`03-hardware.md` §2 style)

```
 Multi-PRF RX chains ──► (per PRF) FIR ──► Stream-to-Vector ──► Doppler FFT
        │                                                       │
        └─────────────────── CRT disambiguation ◄──────────────┘
                                    │
                                    ▼
                    M-element array (M sim sources) ──► MUSIC/beamformer
                                    │
                                    ▼
                          Raster sink + track overlay
```

Track C is where the flowgraph gets genuinely complex (staggered PRFs,
M-element array, Python blocks for CRT/MUSIC). Treat the Python chain as the
authoritative implementation and the flowgraph as a faithful streaming mirror.

## 6. Mini-roadmap

**C1 · Waypoint traffic generator**
New: airport map, routes, coordinated-turn trajectories. Reuses: `channel`.
Verify: generated tracks turn at set rates and stay on taxiways; plot airport
map with moving targets.

**C2 · MUSIC / ESPRIT DOA**
New: eigendecomposition, noise subspace, source-count estimation. Reuses:
array, Capon. Verify: MUSIC resolves two targets 5° apart that Capon cannot;
ESPRIT matches MUSIC angles within 1°. Plot: MUSIC spectrum with true angles.

**C3 · Coordinated-turn EKF (vs. spine Kalman)**
New: CT model, EKF/UKF. Reuses: `KalmanTracker` skeleton. Verify: during a
turn, CV-Kalman track error exceeds 100 m while CT-EKF stays under 10 m; UKF
matches EKF (or beats it on a tight turn). Plot: true vs. EKF vs. CV tracks.

**C4 · Multi-PRF disambiguation**
New: staggered PRFs, CRT. Reuses: `doppler`. Verify: a 250 m/s jet's true
velocity recovered from two folded Doppler estimates; velocity error < Δv/2.
Plot: folded spectra + recovered velocity.

**C5 · Track manager at scale**
New: gating, NN/JPDA association, birth/death. Reuses: C3 filters.
Verify: 15-target scenario — all tracks initiated and confirmed; two crossing
aircraft never swap identities; no clutter-born tracks. Plot: airport map with
stable, labeled tracks.

**C6 · Integrated tower demo**
Task: wire C1–C5 into one chain. Verify: end-to-end airport scenario produces a
consistent target list over time (count, identities, positions) matching truth
within tolerance. Plot: full airport surveillance picture.

**C7 · (◇) JPDA vs. NN head-to-head** — quantify track-swap rate in a dense
crossing scenario; show where JPDA earns its complexity.

## 7. Testing & verification

- MUSIC/ESPRIT: source angles within a beamwidth fraction; source-count
  estimation correct on synthetic snapshots.
- EKF/UKF: turn-scenario RMS error bound (vs. CV baseline).
- Multi-PRF: CRT recovers known `f_d` across many aliased seeds.
- Track manager: hand-built crossing scenario — association correctness,
  no swaps; birth/death timing under M-of-N / N-miss specs.
- Integration: track count and identity match truth over a full run.

## 8. Portfolio artifacts

1. MUSIC spectrum resolving two taxiway aircraft (C2)
2. CV-Kalman vs. CT-EKF track comparison through a turn (C3)
3. Multi-PRF disambiguation of a jet's velocity (C4)
4. Airport-map surveillance picture with stable multi-target tracks (C6)

## 9. Stretch goals

- JPDA vs. NN quantitative comparison (C7).
- UKF-only implementation and comparison on a tight-turn scenario.
- AIC/MDL model-order selection for unknown source counts.
- Data association with false alarms (CFAR output, not truth measurements).

## 10. Boundaries (not covered)

- No real ADS-B / IFF / radar fusion; the track list is radar-only.
- Simplified airport layout (2-D waypoints; no terrain/weather).
- No monopulse or real-time ATC display requirements.
- Synthetic traffic only — no recorded air-traffic data feeds.