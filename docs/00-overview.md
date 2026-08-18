# 00 — Overview

## Project statement

Build an **active radar target tracker** that demonstrates the full pulse-Doppler
radar processing chain: waveform generation, channel simulation, matched
filtering, range and Doppler estimation, Kalman tracking, and — as the advanced
capability — **phased-array beamforming with adaptive interference nulling**.

The project is realized in two stages that grow closer to real hardware:

1. **Python simulation** (NumPy/SciPy) — a precise, self-contained model of the
   full chain, used to learn and verify the math, and to develop and validate
   the algorithms.
2. **GNU Radio model** — a streaming flowgraph that realizes the same chain one
   step closer to actual hardware: blocks operate on continuous sample streams
   just as a software-defined radio would. It runs with *simulated* sources
   today and the RF edges are documented for swapping in real SDR hardware
   without redesigning the processing chain.

The GNU Radio model is not a second, independent implementation — it is a more
hardware-realistic realization of the processing chain first built and verified
in the simulation. Both have their own ways of testing and visualizing
different aspects of the system, and those test and visualization strategies
are documented alongside each stage.

Everything is sim-first: no hardware is required to complete the project. The
hardware is documented as an optional, clearly-mapped swap-in.

## Skill domains

| Domain | What you exercise |
|---|---|
| Radar signal processing | Pulse generation, matched filtering, FFT Doppler processing |
| DSP | Correlation, windowing, FFTs, complex baseband |
| Target tracking | Kalman filter predict/update, data association |
| Array processing | Steering vectors, beam patterns, DOA, LCMV nulling |
| Scientific Python | NumPy, SciPy, Matplotlib, code structure, testing |
| SDR / GNU Radio | Flowgraph design, stream processing, block chains |
| Systems design | Data contracts, modular architecture, sim↔hardware mapping |

## Final system

```
               Python Simulation                        GNU Radio

  Radar Pulse  ──────────────►   Moving Target Sim  ──►  Signal Source / Pulse Gate
        │                          (or SDR channel)          │
        ▼                              │                     ▼
  Moving Target Sim                    ▼              Real RF channel  (optional)
        │                          Received Echo             │
        ▼                              │                     ▼
  Received Echo   ◄─────────────────   │              Noise Source / Delay (simulated)
        │                              │                     │
        ▼                              ▼                     ▼
  Matched Filter  ────────────►   Matched Filter        Matched Filter
        │                              │                     │
        ▼                              ▼                     ▼
  Range Estimate ─────────────►   Range / Doppler        Stream-to-Vector → FFT
        │                              │                     │
        ▼                              ▼                     ▼
  Slow-Time FFT ─────────────►   Kalman Tracker         Range-Doppler Map
        │                              │                     │
        ▼                              ▼                     ▼
  Velocity Estimate ────────►   Target Display          QT GUI Sinks
        │                              │
        ▼                              ▼
  Kalman Tracker ──────────►   Array + Null Steering
        │                        (stages 6–11)
        ▼
  Target Display
```

## Radar parameters (fixed baseline)

| Parameter | Value |
|---|---|
| Carrier frequency | 2.45 GHz |
| Bandwidth | 5 MHz |
| Pulse width | 20 us |
| Pulse repetition interval (PRI) | 1 ms |
| Sampling rate | 20 MHz |
| Pulses per coherent processing interval | 64 |

See `01-physics.md` (Parameter rationale) for *why these exact numbers* were
chosen — including the deliberate `40 m/s` vs. `v_max ≈ 30.6 m/s`
Doppler-ambiguity teaching point — what each parameter controls, and
`05-roadmap.md` for when each is used.

## How to use these docs

There are two recommended paths through these documents. They serve the *same*
reader — you — at different points in the process, so you will switch between
them:

- **Reading (training) order** is for *understanding-first*: learn the physics
  and design before touching code. Use it at the start, when you pick up a new
  topic, or when you're stuck on a concept. It is the path a newcomer follows.
- **Implementation order** is for *doing-first*: the roadmap is your to-do
  list, and everything else is on-demand reference. Use it while building —
  which is most weeks once you've done the reading. It is the path a builder
  follows.

The two orders map onto the two halves of the training process
(`06-training.md`): the reading order corresponds to the **learning**
objectives and quizzes, the implementation order corresponds to the
**hands-on** labs and weekly milestones. A typical week looks like this:
skim the reading-order docs for the week's topic, then work through the
roadmap stage in implementation order, then verify with the week's quiz and
lab.

**Reading (training) order** — first pass, topic by topic:

1. `00-overview.md` — here
2. `01-physics.md` — the science behind every block
3. `02-architecture.md` — how the pieces fit together
4. `05-roadmap.md` — the weekly plan that ties physics to code
5. `04-python-discipline.md` — how to write the code well
6. `06-training.md` — exercises and self-checks
7. `03-hardware.md` — optional SDR swap-in
8. `07-glossary.md` — reference
9. `08-extensions.md` — *optional*, after the spine: specialization tracks
   (automotive, counter-drone, airport surveillance)

**Implementation order** — while building, task first:

1. `05-roadmap.md` — follow stages 1–12, week by week
2. `04-python-discipline.md` — the code spec each stage must follow
3. `02-architecture.md` — module boundaries and data contracts
4. `01-physics.md` — theory references as needed
5. `03-hardware.md` — GNU Radio flowgraph build and (optional) hardware swap

> **Rule of thumb:** reading when you want to *understand*, implementation when
> you want to *do*. There is no wrong time to switch between them.

## What you'll produce

**Given to you:** these docs, the Python code spec, the GNU Radio flowgraph
designs, and the training materials — everything you need to build the project.

**What you deliver** (your portfolio artifacts, detailed in `06-training.md` §6):

1. A working Python radar simulation — waveform, channel, range, Doppler,
   tracking, array processing, null steering
2. The equivalent GNU Radio flowgraphs running sim-only
3. The four artifacts: range-Doppler map, beam pattern, adaptive-null pattern
   with before/after maps, and a GNU Radio range-Doppler map
4. Your quiz and lab results per the training package