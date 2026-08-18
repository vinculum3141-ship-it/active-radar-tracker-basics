# 06 — Training

Self-paced training package. Use the roadmap's weekly milestones as the
syllabus; use this document for objectives, exercises, quizzes, and rubrics.

---

## 1. Prerequisites

Comfortable with:

- Python: functions, classes, `numpy` array basics, `matplotlib` plotting.
- A little DSP vocabulary: sampling, FFT, complex numbers.
- Not required: radar, RF, or GNU Radio background — those are taught here.

**Setup before Week 1:** follow `04-python-discipline.md` §1 (uv, venv,
package skeleton) and `03-hardware.md` §1 (GNU Radio install, only needed by
Week 5).

---

## 2. Domain relevance

This project implements the algorithmic heart of real pulse-Doppler radar —
the same chain used in military and mobile systems. Knowing *where* each piece
shows up in practice frames what you're building.

### What the project directly implements

| Project component | Where it appears in the real world |
|---|---|
| Pulse-Doppler processing (fast-time range, slow-time Doppler) | Airborne fighter radar (look-down/shoot-down), airborne early warning, MTI/GMTI ground moving-target indication |
| LFM pulse compression | Standard in virtually all modern radar to beat range-resolution limits |
| Range-Doppler map | The surface on which CFAR detection runs (detection layer in all of the above) |
| Kalman track-while-scan | Tracking aircraft, missiles, and vehicles from repeated scans; same math as automotive radar trackers |
| Phased array + beam steering | AESA (active electronically scanned arrays) |
| Adaptive nulling (LCMV) | Simplified STAP / electronic-protection; nulling a jammer direction is a real anti-jam capability |

**Mobile-tracking angle:** automotive radar (adaptive cruise control, automatic
emergency braking, ~77 GHz) uses this same chain — chirp waveforms,
range-Doppler maps, CFAR, and Kalman tracking of vehicles. The multi-target
stretch (two targets, independent tracks) touches the *data association*
problem that mobile and surveillance trackers share.

### Honest boundaries (not covered)

- **Full STAP** (joint space-time) — this project does spatial-only nulling,
  no Doppler-domain nulling.
- **Monopulse** angle measurement (sub-beamwidth angular accuracy).
- Real clutter statistics, ECM jamming waveforms, and sensor fusion /
  INS-aided tracking.

Roughly: the project covers the first third to half of a military radar
textbook and the exact algorithmic heart of automotive radar.

---

## 3. Engineering mindset

Beyond the radar, this course teaches **how to build a good system with good
code** — the same discipline transfers to any signal-processing or software
project. These principles are exercised by the project, not just preached:

| Principle | What it means | Where the project exercises it |
|---|---|---|
| Contracts before abstractions | Decide what data flows between pieces *before* designing interfaces; a clean `in → out` shape removes most need for clever abstractions | `02-architecture.md` data contracts; `04-python-discipline.md` API spec |
| Defer abstraction until a second consumer | Never build an interface for the one thing you have; wait until a real second use appears | the extension seams register (`02-architecture.md` §6) is the working example |
| Verify against analytic truth | Tests check the code against known answers, not against previous runs | `04-python-discipline.md` testing discipline; every roadmap stage's verification |
| Reproducibility as a default | Seeded randomness, config-driven parameters, saved artifacts — so results are audit-able | `04-python-discipline.md` (seeded RNG, config, `--plot` output) |
| Scope control | Add one capability per stage/track; park the rest as explicit stretch goals | the roadmap's ✓/◇ split; the extensions' "one layer per track" rule |
| Design for the seam, not for the abstraction | Know *where* you'd extend (the seams) before you need to — then build the abstraction only when you cross that point | `02-architecture.md` §6 register |

Two of these deserve emphasis because they're the ones beginners most often
get backwards:

- **Contracts first, abstraction second.** `simulate_channel(tx, targets,
  cfg, rng)` and `detect_peaks → list[Detection]` are stable contracts. They
  are why the spine needs no restructuring when extensions arrive — the *data
  shapes* already generalize even though no interfaces were built.
- **YAGNI is a timing decision, not a permanent no.** The seams register says
  "we will build a `Receiver` protocol when track A starts," not "never." The
  skill is *recognizing* the seam early and *resisting* building it early.

There is a self-check at the end of Week 5: explain, in your own words, why
the spine's module list survived the three extension tracks without changing
structure. If you can, you've absorbed the engineering mindset, not just the
radar.

---

## 4. Weekly learning objectives

By the end of each week you can explain/do:

**Week 1**
- Explain why a radar needs a quiet window (PRI, duty cycle).
- Compute range from a measured delay: `R = cτ/2`.
- Explain why matched filtering beats raw thresholding.
- Build a chirp in NumPy and confirm its frequency sweep.

**Week 2**
- Explain fast-time vs slow-time and why Doppler appears across pulses.
- Read a range-Doppler map: which axis is range, which is velocity.
- State `Δv` and `v_max` and what happens when they're violated.
- Explain the Kalman predict/update loop and what `Q` and `R` each mean.

**Week 3**
- Write the steering-vector formula `a(θ)` from memory.
- Explain what a beam pattern is and where sidelobes come from.
- Contrast Bartlett vs Capon DOA.

**Week 4**
- State the LCMV constraints (`Cᴴw = g`) and interpret them.
- Predict where the null appears given a constraint vector.
- Explain why nulling before matched filtering is architecturally clean.

**Week 5**
- Read a GRC flowgraph as a pipeline of blocks.
- Map each GNU Radio block to its Python/algorithmic equivalent.
- Name the blocks that would swap for real hardware.

---

## 5. Weekly self-check quizzes

Short-answer questions per week. Check against `01-physics.md` and
`07-glossary.md`.

### Week 1
1. With `τ = 20 us` and `T = 1 ms`, what is the duty cycle?
2. A target at `R = 1000 m` — what round-trip delay (in samples at `fs = 20 MHz`)
   should the echo have? (`c = 3e8 m/s`)
3. Why does `R = cτ/2` have a factor of 2?
4. What is the range resolution of a 5 MHz LFM chirp? Why is that better than a
   20 us rectangular pulse?

### Week 2
5. A target at `40 m/s`, `fc = 2.45 GHz`. What is `f_d`? (to ±5%)
6. With `N=64` pulses and `T = 1 ms`, what is `Δv`? What is `v_max`?
7. Is a target at `40 m/s` ambiguous at these settings? How would you tell?
8. In a Kalman filter, what does `Q` do if it's too big? `R` too big?

### Week 3
9. Element spacing `d = λ/2`, `M = 4`. Write `a(θ)` for `θ = 30°`.
10. Where would a grating lobe appear if `d = λ`? Why?
11. Bartlett vs Capon — which resolves closer angles, and why?

### Week 4
12. Give the LCMV weights formula and the constraint pair for target at
    `+20°` / interferer at `-30°`.
13. What happens if the interferer and target are at the *same* angle?
    (Spoiler: you must choose — that's why beam width matters.)
14. Why null *before* the matched filter?

### Week 5
15. Which GNU Radio blocks replace the Python `channel` and `receiver`?
16. What would you change to attach a HackRF instead of a simulated source?
17. Why can't a single-channel HackRF receive a 4-element array?

---

## 6. Hands-on labs

Each lab is a mini-investigation on top of a stage's code.

| Lab | Task | Success looks like |
|---|---|---|
| L1 (wk1) | Sweep `SNR` from 30→0 dB; at what SNR does `detect_peaks` fail? | plot of detection error vs SNR |
| L2 (wk2) | Double `PRF` and re-run Doppler; does the ambiguous target unwrap? | consistent velocity across runs |
| L3 (wk3) | Two targets 10° apart; Bartlett then Capon; measure peak separation | Capon resolves, Bartlett doesn't |
| L4 (wk4) | Drift the interferer `-30°→-20°`; recompute weights each CPI | null tracks interferer; target stays |
| L5 (wk5) | Run sim + GNU Radio for same `(R, v)`; overlay results | numbers match to a bin |

---

## 7. Verification rubrics

Use these to self-grade each milestone artifact.

### Range-Doppler map (Week 2)
- [ ] Axes labeled correctly (range in meters, velocity in m/s)
- [ ] Peak cell within 1 range bin / `Δv/2` of truth
- [ ] No aliasing artifact without an explicit test explaining it

### Beam pattern (Week 3)
- [ ] Main lobe centered on steer angle
- [ ] Sidelobes < -13 dB for the chosen window
- [ ] (Week 4) Deep null (> 40 dB) at interferer angle; unit gain at target

### Tracking plot (Week 2)
- [ ] True, measured, and Kalman curves distinguishable
- [ ] Track visibly smoother than measurements, no systematic lag

### GNU Radio (Week 5)
- [ ] Same target cell as Python sim
- [ ] All three flowgraphs run end-to-end sim-only

> This rubric is the same gate as the `03-hardware.md` §5 validation
> checklist — complete and tick that one too.

---

## 8. Portfolio artifacts

The four artifacts that tell the story:

1. **Range-Doppler map** — pulse-Doppler processing
2. **Beam pattern** — array processing / DOA
3. **Adaptive-null pattern + before/after RD maps** — interference cancellation
4. **GNU Radio RD map** — SDR/flowgraph skill

For each, keep: the plot, the config that produced it, and a 3–5 line caption
(state what it shows, the key number, and the takeaway).

---

## 9. Definition of done

The single place that states when the whole course is complete. You're done
when **all** of the following hold:

- **Roadmap** — every stage in `05-roadmap.md` is complete: all five weekly
  milestones met, every per-stage verification green.
- **Code** — the full suite passes with no stubs left:
  `uv run pytest` green and `uv run ruff check .` clean
  (`04-python-discipline.md` §4); no `NotImplementedError` remains in
  `src/radar/`. Running
  `uv run radar simulate --config configs/baseline.yaml` produces detections
  and plots instead of "not implemented yet".
- **GNU Radio** — the `03-hardware.md` §5 validation checklist is fully
  ticked; the three flowgraphs reproduce the Python pipeline numbers.
- **Artifacts** — the four portfolio artifacts from §8 exist, each with its
  config and caption.
- **Self-assessment** — quizzes §5 and labs §6 complete; the §7 rubrics are
  self-graded and consistent.

---

## 10. Suggested study references

- Richards, *Fundamentals of Radar Signal Processing*
- Skolnik, *Introduction to Radar Systems*
- Van Trees, *Optimum Array Processing*
- GNU Radio documentation + GNU Radio Companion tutorials
- SciPy `signal` reference (chirp, correlate, spectrogram)
- **Going further:** after the spine, see `08-extensions.md` for the
  specialization tracks (automotive FMCW, counter-drone, airport tower
  surveillance) — each a mapped extension of what you've built here.