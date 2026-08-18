# 02 — Architecture

Design of the system across both implementations (Python simulation and GNU
Radio flowgraph), the module boundaries, the data contracts between them, and
the sim↔hardware abstraction points.

---

## 1. Two realizations, one conceptual chain

The processing chain is identical in both:

```
 TX pulse → channel → RX array → beamform → matched filter → range/doppler → track → display
```

- **Python realization**: batch/offline. Matrix math, easy to inspect, best for
  learning the math and verifying correctness.
- **GNU Radio realization**: streaming/online. Blocks pass samples continuously;
  identical processing in a real-time framework. Hardware can replace the
  simulated channel later.

The GNU Radio model must be a *structural mirror* of the Python pipeline so
results are comparable and the training material applies to both.

---

## 2. Python simulation architecture

### Module map

```
src/radar/
  config.py        # dataclasses + YAML/TOML loaders for all radar parameters
  signal_gen.py    # transmit waveform: rectangular pulse, LFM chirp, pulse train
  channel.py       # channel model: propagation delay, attenuation, noise
  receiver.py      # matched filter, peak detection, range estimation
  doppler.py       # slow-time FFT, range-Doppler map, velocity axis
  tracker.py       # Kalman filter: predict/update, track management
  array.py         # uniform linear array: steering vectors, beam pattern
  beamformer.py    # Bartlett/Capon scan, LCMV null-steering weights
  viz.py           # plotting helpers: radar screen, range-doppler, patterns
  cli.py           # entry points: simulate, bench, plot, test-tracks
```

### Data contracts (what flows between modules)

| Object | Type | Notes |
|---|---|---|
| `pulse` | `np.ndarray[complex]` | one transmitted pulse, fast-time samples |
| `pulse_train` | `np.ndarray[complex]` | `[N_pulses, samples_per_pulse]` |
| `rx_fast` | `np.ndarray[complex]` | one received pulse (fast time) |
| `rx_slow` | `np.ndarray[complex]` | `[N_pulses, samples_per_pulse]` stacked |
| `matched` | `np.ndarray[complex]` | `[N_pulses, samples_per_pulse]` after filter |
| `range_axis` | `np.ndarray[float]` | meters, derived from fast-time bins |
| `velocity_axis` | `np.ndarray[float]` | m/s, derived from Doppler bins |
| `rd_map` | `np.ndarray[float]` | `[range_bins, doppler_bins]` |
| `detections` | `list[Detection]` | `(range_m, velocity, snr, angle)` |
| `track` | `list[State]` | Kalman-filtered `(R, v)` sequence |
| `array_data` | `np.ndarray[complex]` | `[M_elements, N_pulses, samples]` (stages 6+) |
| `weights` | `np.ndarray[complex]` | `[M_elements]` beamformer weights |
| `pattern` | `(np.ndarray, np.ndarray)` | angle axis + `|wᴴa(θ)|²` |

### Processing pipeline (Python)

```
 signal_gen → channel → array (stages 6+) → receiver (matched filter)
     → doppler (range-Doppler map) → beamformer (stages 6+) → tracker → viz
```

The **beamformer** sits between the array and the matched filter: element
signals are summed with weights *before* the range–Doppler processing. This is
the key architectural choice — nulling happens in the spatial domain first,
then the cleaned single-channel stream is processed like a normal radar.

---

## 3. GNU Radio flowgraph architecture

Three flowgraphs, mirroring the Python chain.

### 3.1 Transmitter (TX)

```
 Signal Source (2.45 GHz, complex)
      │
      ▼
 Pulse Gate (multiply by pulse train envelope)
      │
      ▼
 Multiply / Throttle
      │
      ▼
 QT GUI Time Sink ──────────────► (to receiver / SDR later)
```

| Block | Role | Python equivalent |
|---|---|---|
| Signal Source | CW carrier | `signal_gen` |
| Multiply (pulse gate) | pulse train envelope | pulse shaping |
| Throttle | prevent CPU runaway | n/a |
| QT GUI Sink | visualize waveform | `viz` |

### 3.2 Simulated channel + receiver (RX)

```
 Signal Source (TX copy)
      │
      ▼
 Delay (round-trip time) ──────────────┐
      │                                │
      ▼                                ▼
 Noise Source ───────────────────► Add ──► Matched Filter (FIR)
                                           │
                                           ▼
                                        Complex to Magnitude
                                           │
                                           ▼
                                        QT GUI Time Sink
```

| Block | Role | Python equivalent |
|---|---|---|
| Delay | round-trip propagation | `channel` |
| Noise Source | receiver noise | `channel` |
| Add | combine echo + noise | `channel` |
| FIR Filter (conj. time-reversed chirp) | matched filter | `receiver` |
| Complex to Mag | detection envelope | `receiver` peak detection |
| QT GUI Sink | echo + filtered display | `viz` |

### 3.3 Doppler / range-Doppler processing

```
 Received Pulses
      │
      ▼
 Stream to Vector (vector length = pulses per CPI)
      │
      ▼
 FFT (over slow time)
      │
      ▼
 Complex to Magnitude
      │
      ▼
 QT GUI Frequency Sink / Range-Doppler Plot
```

For a true 2-D range-Doppler map in GNU Radio, use the **Vector to Stream /
Stream to Vector** pair with a `Vector FFT` or a **Serial-to-Parallel** buffer
so the FFT runs over the slow-time axis (pulse index in the spine; chirp index
in FMCW track A) while fast-time bins remain the row index. The QT GUI
**Raster Sink** renders the 2-D map.

### 3.4 Array + beamforming in GNU Radio (stages 6–11)

```
 M signal sources (or 1 source split into M delayed/phase-shifted copies)
      │        │        │
      ▼        ▼        ▼
   Antenna 1  Antenna 2 ... Antenna M
      │        │        │
      └────────┼────────┘
               ▼
        Beamforming (weighted sum)
               │
               ▼
        Matched Filter → Range/Doppler → Viz
```

The beamformer is a **phase-shifter (complex multiply) + adder** per element.
LCMV weights are computed offline (Python or a Python block) and applied as
fixed complex constants — adaptivity comes from recomputing them when the
interferer moves.

> **Design note:** the beamforming stage is deliberately placed *before* the
> matched filter in both realizations. This keeps the array processing a pure
> spatial operation and lets the rest of the chain stay single-channel.

---

## 4. Sim ↔ hardware abstraction points

The architecture is built so the GNU Radio model runs with **simulated
sources** today and accepts real hardware with minimal edits:

| Chain position | Simulated | Hardware swap-in |
|---|---|---|
| TX waveform | Signal Source | Osmocom Sink → HackRF/USRP TX |
| Channel | Delay + Noise (simulated echo) | Real over-the-air path |
| RX input | Signal Source copy | Osmocom Source ← HackRF/USRP RX |
| Array | M phase-shifted sim sources | Multi-channel USRP RX (one ch/element) |
| DSP after RF | Identical blocks | Identical blocks (no change) |

The *DSP core* (matched filter, Doppler, tracking, beamformer) is **identical**
in both cases. Only the source/sink blocks at the RF edges change — this is
the design principle that makes the project hardware-ready without hardware.

## 5. Design decisions log

| Decision | Rationale |
|---|---|
| Complex baseband throughout | Real radar DSP operates at baseband after down-conversion; avoids modeling the carrier in simulation |
| Beamformer before matched filter | Spatial filtering is a linear operation; doing it first keeps the rest single-channel |
| Batch (Python) then stream (GNU Radio) | Learn the math on inspectable matrices, then express it as a streaming graph |
| Sim-first, hardware-mapped | Zero-cost to run, complete coverage of the processing chain, portable to hardware later |
| Single ULA, `d = λ/2` | Simplest array with unambiguous beamforming; M=4 or 8 elements |
| Defer extension abstractions until a track starts | Extensions (`08-*.md`) swap different chain stages; per YAGNI, no interface is built until a second implementation actually begins (see §6) |

---

## 6. Extension seams & deferred abstractions

The specialization tracks (`08-extensions.md`) each replace a different stage of
the chain: A swaps the receiver front-end, B the channel/detector, C the
tracker and adds a target source. Per the project's *no abstraction without a
need* rule, **none of these seams are built into the spine.**

This section demonstrates **how to decide when to abstract** — a technique
you can reuse in any codebase you work on. (See `06-training.md` §3,
Engineering mindset.)

**Ask yourself these three things before building any abstraction**

1. *Is there a second consumer yet?* If only one place uses it, don't build an
   interface for it — wait until a real second use appears.
2. *Is the change structural or just naming?* Renaming a concept or stating a
   contract that's already true costs nothing and can be done immediately;
   restructuring costs and should wait.
3. *What would I build, and when?* Write down the answer — the proposed shape
   and its trigger — so the decision is explicit and reversible later.

The four rules below turn those questions into a concrete checklist.

**Decision rules**

1. *No second consumer, no seam.* An interface is only introduced when a second
   implementation actually starts (a track is selected and its first stage is
   on the board).
2. *Free-if-prose changes happen now* — naming and stating contracts that are
   already true in the code (no structural change).
3. *Structural changes are deferred* until the triggering track begins. The
   register below is the single source of truth for what to build then.
4. *Revisit this table when starting a track:* build only that track's rows,
   then fold them into the track's docs and delete the rows.

| Seam | Trigger | Shape when built | Status |
|---|---|---|---|
| Receiver front-end | Track A — dechirp replaces matched filter | `Receiver` protocol; `matched_filter` / `dechirp` implementations | deferred |
| Detector | Track B — 2-D CA-CFAR | `Detector` protocol; output contract already `list[Detection]` via `detect_peaks` | deferred (contract exists) |
| Channel effects | Track B — clutter, Swerling fluctuation, micro-Doppler | composable `Effect` chain inside `channel` | deferred |
| Tracker variants | Track C — EKF/UKF; Track A — TrackManager | `Tracker` protocol; `tracking/` package (`kalman`, `ekf`, `ukf`, `track_manager`) | deferred |
| Config nesting | Tracks A/B/C add many parameters | nested dataclasses under `RadarConfig` | deferred |
| Pipeline composition | first multi-mode chain | `pipeline.py` composing stages behind protocols | deferred |
| Slow-time axis semantics | Track A — slow time is "chirp index", not pulse index | doc wording only: "slow-time" as the generic axis | done now |
| Target-list input | already spine | `simulate_channel(tx, targets, cfg, rng)` takes a target list | already present |
| Detection output contract | already spine | `detect_peaks` returns `list[Detection]` | already present |

> The "already present" rows are the *contracts-first* lesson: because the data
> shapes (target list in, `Detection` list out) already generalize, the spine
> needs no restructuring when extensions arrive. When a track starts, revisit
> this table and build only its deferred rows.