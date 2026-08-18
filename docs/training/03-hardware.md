# 03 — Hardware & GNU Radio

The project runs **fully simulated** — no hardware is required. This document
covers how to install GNU Radio, how to build the flowgraphs, and how each
block would swap to real SDR hardware if you ever add it.

> **Your finish line for this section is §5.** The last section — the
> *Sim-vs-hardware validation checklist* — is the gate for this document and
> for Week 5 on the roadmap. **Skim it now** before reading §2, so you know
> what "done" looks like; every flowgraph in §2 is designed to satisfy those
> items. `05-roadmap.md` Week 5 marks it complete when all boxes are ticked.

---

## 1. Installing GNU Radio

GNU Radio installs differently per platform:

**macOS (Homebrew)**

```bash
brew install gnuradio
# GUI (QT) support is bundled with the formula on macOS.
# Launch the flowgraph editor:
gnuradio-companion
```

**Linux (Debian/Ubuntu)**

```bash
sudo apt update && sudo apt install gnuradio gnuradio-dev gr-osmosdr
# Launch the flowgraph editor:
gnuradio-companion
```

> On some distros the launcher is `gnuradio-companion`; on others it is
> `gnuradio-companion` under a different PATH or Python's
> `python3 -m gnuradio.grc`.

**Check the install (both platforms):**

```bash
gnuradio-companion --version
```

```bash
# Import test. The Python that GNU Radio binds to is the Homebrew formula's
# Python, which may differ from your default `python3`.
# macOS (Homebrew):
python3.14 -c "import gnuradio; print(gnuradio.gr.version())"
# Linux (system Python):
python3 -c "import gnuradio; print(gnuradio.gr.version())"
```

**Troubleshooting `ModuleNotFoundError: No module named 'gnuradio'`**

GNU Radio's Python bindings are compiled against the Python it was built
with, and compiled extension modules do not import across Python versions.
On macOS, `brew install gnuradio` builds against Homebrew's `python@3.14`,
so `import gnuradio` works under `python3.14` (or whatever `brew info
gnuradio` lists under *Dependencies*) but *not* under a 3.12 venv or the
system Python. Check which interpreter to use with `brew info gnuradio`.
The flowgraph tooling is unaffected: `gnuradio-companion` and `grcc` always
use the correct Python themselves.

Python blocks are defined with **GRC (GNU Radio Companion)** generated
out-of-tree modules or plain Python blocks inside a flowgraph.

> If you use `uv` for the Python side (`04-python-discipline.md`), keep GNU
> Radio in a *separate* environment or install it system-wide — the GNU Radio
> Python modules bind to its own runtime. Do not mix them in the same venv.

---

## 2. Flowgraph design (simulated)

Three GRC flowgraphs, matching `02-architecture.md`.

### 2.1 `radar_tx.grc` — Transmitter

```
 Signal Source (Frequency: 2.45 GHz, Waveform: Cosine/Complex)
   → Multiply Const / Pulse Gate (multiply by 0/1 pulse train)
   → Throttle
   → QT GUI Time Sink
```

Key settings: **Complex** output, `Sampling Rate = 20 MHz`.

### 2.2 `radar_rx_sim.grc` — Simulated channel + receiver

```
 Signal Source (TX waveform)
   → Delay (delay = round-trip samples)
   → Add ← Noise Source (Gaussian)
   → FIR Filter (taps = conjugated, time-reversed chirp)   [matched filter]
   → Complex to Mag
   → QT GUI Time Sink
   → QT GUI Frequency Sink
```

Key settings:

| Block | Setting |
|---|---|
| Delay | `Delay = round(2·R/c · fs)` samples |
| Noise Source | Gaussian, variance per target SNR |
| FIR Filter | taps from `np.conj(chirp[::-1])` |
| FFT size | power-of-two (1024) |

### 2.3 `radar_doppler.grc` — Range-Doppler

```
 [matched pulses] → Stream to Vector (len = N_pulses)
   → FFT (over slow time)
   → Complex to Mag
   → QT GUI Raster Sink (2-D range-Doppler map)
```

> For the 2-D map: stream the `N_pulses` matched-filter outputs as a vector,
> FFT along that axis, and feed the result to a **Raster Sink** with the
> fast-time (range) axis as rows.

### 2.4 Array/beamformer (stages 6–11)

```
 M × (Signal Source with phase offset per element)
   → Complex Multiply (LCMV weights, fixed or Python-recomputed)
   → Add (weighted sum)
   → Matched Filter → Range/Doppler → Viz
```

M phase-shifted copies of the same source model the wavefront; the weights
steer the beam and place the null.

---

## 3. Hardware swap-in map

The processing chain after the RF edge is **identical** — only source/sink
blocks change.

| Chain position | GNU Radio block (sim) | Hardware replacement | Device |
|---|---|---|---|
| TX waveform | Signal Source | `osmocom Sink` (gr-osmosdr) or `uhd:usrp_sink` | HackRF, USRP, LimeSDR |
| Channel | Delay + Noise Source | real over-the-air path | — |
| RX input | Signal Source copy | `osmocom Source` / `uhd:usrp_source` | HackRF, USRP, LimeSDR |
| Array RX | M phase-shifted sim sources | multi-channel USRP (1 ch/element) | USRP X310/2-ch, X4xx |
| DSP (matched filter, Doppler, tracker) | FIR, FFT, etc. | identical blocks | — |

### Device comparison

| Device | Band | RX/TX | Multi-channel | Notes |
|---|---|---|---|---|
| HackRF One | 1 MHz–6 GHz | half-duplex, single ch | No | cheapest entry; 20 Msps max, 8-bit |
| LimeSDR | 100 kHz–3.8 GHz | full-duplex, 2 ch | 2 (LMS7002M) | good value; software-heavy |
| USRP B2xx | 70 MHz–6 GHz | full-duplex | 1–2 | solid docs, UHD |
| USRP X310/X4xx | up to 6 GHz | full-duplex | 2–4 | the one for a real 4-element array |

**Array note:** a real 4-element receive array needs a **multi-channel USRP**
(one RF chain per element). HackRF and B2xx are single-channel — they are
fine for single-antenna TX/RX but cannot receive 4 phase-coherent channels.

---

## 4. Legal / regulatory notes

- **2.45 GHz** falls in the **ISM band** (2.400–2.4835 GHz), where
  low-power, unlicensed devices operate worldwide.
- Keep transmit power **low** (e.g. below local ISM ERP limits; typical
  laptop-WiFi-class levels) and never aim at people.
- Even so, if you go over-the-air, comply with your local regulator's rules
  for that band (FCC Part 15 in the US; similar ETSI limits in the EU).
- For learning, **simulated is always legal**: the Delay/Noise channel models
  the air perfectly well for this project.

---

## 5. Sim-vs-hardware validation checklist

- [ ] Sim flowgraph produces the same range/velocity as the Python sim for a
      known target.
- [ ] Matched filter output peak appears at the expected delay.
- [ ] Range-Doppler map shows the expected target cell for `R=1000 m, v=40 m/s`.
- [ ] Array pattern shows main lobe at target angle, null at interferer angle.
- [ ] (Optional) hardware path: same DSP blocks, with TX/RX swapped to
      `osmocom` sinks/sources — re-run the above checks over the air.