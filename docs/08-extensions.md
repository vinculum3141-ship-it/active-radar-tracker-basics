# 08 — Extensions: Specialization Tracks

> **Elective material — not part of the core course.** The spine (docs 00–07,
> roadmap 01–12) is the beginner-safe foundation and is *complete* on its own.
> These tracks are optional, more-focused applications that build directly on
> the spine. Do not start one until the spine's five weeks are done.

---

## 1. The idea

The spine teaches the **algorithmic heart** of pulse-Doppler radar. Each
specialization track takes that heart and adds a *small, well-bounded set of
new concepts* — its **delta**. The hard DSP is already in the spine; a track
only swaps or extends one layer of it. That is what keeps a specialization
achievable: you are never learning radar from scratch again, only the parts a
given application adds.

| What each track changes | Spine layer it touches |
|---|---|
| A — FMCW automotive | the **front-end waveform** (receiver structure) |
| B — Counter-drone | the **detection layer** (realism of the channel + detector) |
| C — Airport tower surveillance | the **tracking/estimation layer** (scale, resolution, dynamics) |

---

## 2. Branch comparison

| | A — Automotive | B — Counter-drone | C — Airport tower |
|---|---|---|---|
| Project | FMCW radar tracking multiple vehicles | Detect + track small UAVs against clutter | Track many aircraft around a tower |
| Waveform | Fast-chirp FMCW | Pulse-Doppler (spine, kept) | Pulse-Doppler, multi-PRF |
| New concepts | Beat mixing, range/Doppler FFT, 2-D CFAR, clustering, track management | Swerling fluctuation, 2-D CFAR, ground clutter + MTI, micro-Doppler | MUSIC/ESPRIT DOA, coordinated-turn EKF/UKF, association/gating, multi-PRF |
| Reuses from spine | Matched-filter *structure* (as FFTs), Kalman, beamforming | Matched filter, range-Doppler, Kalman, array | Range-Doppler, array/Capon, Kalman |
| Difficulty | ★★☆ (smallest delta) | ★★★ | ★★★★ (largest delta) |
| Mood | Automotive/safety | Defense/CUAS | Surveillance/ATC |

---

## 3. How to choose

- **A** if you want to see the *same core math under a different waveform*, and
  are interested in automotive/robotics sensing. Best first choice — it is the
  smallest delta and the biggest confidence boost.
- **B** if you are drawn to the *detection problem*: noise, clutter, weak and
  fluctuating targets, and making a radar "believe" what it sees. The most
  hands-on with the channel model.
- **C** if you enjoy *estimation and systems*: many targets, angles, turns, and
  disambiguation. The most mathematically demanding and the largest scope.

They are **complementary, not exclusive** — A and B together cover the front-end
plus the detection layer; adding C completes a fairly realistic surveillance
radar. If you only do one, start with A.

---

## 4. Shared prerequisites (before any track)

- All 12 spine stages complete and green (`05-roadmap.md`).
- Comfortable reading `01-physics.md`, `02-architecture.md`, and
  `04-python-discipline.md` as references.
- Week-5 GNU Radio skill if you plan the flowgraph portion of a track.

## 5. Mini-roadmap format

Each branch file uses a compact form of the spine roadmap:

```
<stage id> · <one-line objective>
  New concepts: <what this stage teaches>
  Reuses: <spine skills it builds on>
  Task: <what to build, per 04-python-discipline.md>
  Verify: <test + plot that proves it works>
```

Typically 5–6 stages per track, each ending in a verification — same discipline
as the spine.

## 6. Shared guidance

- **Scope rule:** each track adds *one layer*. If a track tempts you into
  adding a second waveform, a third detector, or real hardware — that is a new
  track, not a stage. Park it as a stretch goal.
- **Tests:** extend the spine's test plan (per-module analytic answers), never
  "compare to the previous run."
- **Parameters:** every track keeps `04-python-discipline.md`'s conventions
  (config dataclasses, seeded RNG, ruff, pytest).
- **GNU Radio:** every track has a flowgraph mapping; all are sim-only, with
  hardware swap points flagged where a real system would differ.
- **Architecture:** per YAGNI, tracks do *not* pre-build abstractions into the
  spine. When a track starts, see `02-architecture.md` §6 — the extension seams
  register — and build only that track's registered seams.

## Branch files

- [08a — Automotive FMCW radar](08a-ext-automotive.md)
- [08b — Counter-drone radar](08b-ext-counterdrone.md)
- [08c — Airport tower surveillance](08c-ext-airport-surveillance.md)