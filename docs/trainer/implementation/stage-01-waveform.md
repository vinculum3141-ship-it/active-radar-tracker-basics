# Stage 1 — Radar waveform

## In one sentence

We generate the "shout" of the radar: a short burst of radio energy — first a
plain rectangular blip, then an LFM chirp whose frequency sweeps across the
pulse — repeated 64 times per measurement frame.

## The problem

A pulse radar finds targets by transmitting energy and listening for echoes.
Everything downstream — the channel model (stage 2), the matched filter
(stage 3), Doppler (stage 4) — *starts from the transmitted waveform*, so the
very first thing the project needs is a precise definition of what the radar
sends. The problem has two halves:

1. **Timing.** A radar can't listen while it's shouting, so it alternates
   bursts of energy with quiet gaps. We must decide how long a burst lasts
   (`τ`) and how often bursts repeat (the PRI). This defines *when* the signal
   is present and *how many samples* each burst and each gap occupy.
2. **Waveform quality.** A plain rectangular burst can't tell nearby targets
   apart — its range resolution is `ΔR = c·τ/2 = 3 km`. But a *long* burst is
   what collects enough energy to hear a faint echo. That tension — energy
   wants a long pulse, resolution wants a short one — is broken by sweeping
   the frequency across the pulse (the LFM chirp), which later lets a matched
   filter compress the long burst back to a short one.

**Deliverable:** a function that, given the radar parameters in `RadarConfig`,
produces the exact digital signal the radar would transmit — the single pulse,
and the full train of pulses that makes up one coherent measurement frame
(a CPI of 64 pulses).

## Approach — the algorithm in words

Read this as a recipe; every step below has a named function in the code.

1. **Convert the timing into sample counts.** Time means nothing to a
   computer until we sample it. `τ = 20 µs` at `fs = 20 MHz` is 400 samples;
   one PRI of `1 ms` is 20,000 samples. These two integers shape every array
   that follows.
2. **Fill one pulse with a waveform.** Decide whether the burst is
   - *rectangular*: 400 samples, all unit amplitude, no modulation — the naive
     blip; or
   - *LFM chirp*: 400 samples whose *phase* advances quadratically in time,
     so the instantaneous frequency ramps linearly from 0 up to `B = 5 MHz`.
     All samples keep unit amplitude; the modulation lives in the phase.
3. **Repeat the pulse into a frame.** Allocate a `(64, 20000)` array — one row
   per pulse in the CPI, 20,000 fast-time samples per row. Copy the same pulse
   into the *first* 400 samples of every row and leave the rest silent. The
   silent tail of each row is the listen window where the echo will land
   (stage 2).
4. **Select and hand off.** Pick rectangular or LFM from the config, return the
   finished train, and let the next stage (the channel) consume it.

That's the whole stage: two sample-count constants, one burst generator
(two variants), one repackaging step, one selector.

## What we built

The transmit waveform generator in `src/radar/signal_gen.py`, per the API
spec (`04-python-discipline.md` §3), plus `viz.plot_pulse` and the `radar plot`
CLI subcommand that renders the pulse to `out/stage1/pulse.png`.

Algorithm step → function:

| Algorithm step | Function | Returns |
|---|---|---|
| 1 · sample counts | `_n_pulse_samples` / `_samples_per_pulse` (helpers) | `int` (400 / 20000) |
| 2a · rectangular burst | `rectangular_pulse(cfg)` | `(400,)` complex, all `1+0j` |
| 2b · frequency-swept burst | `lfm_chirp(cfg)` | `(400,)` complex analytic |
| 3 · repeat into a frame | `pulse_train(cfg)` | `(64, 20000)` complex |
| 4 · select + hand off | `transmit_waveform(cfg)` | `(64, 20000)` complex |

**Files touched:** `src/radar/signal_gen.py`, `src/radar/viz.py`,
`src/radar/cli.py`, `tests/test_signal_gen.py`.

## Physics in play

A monostatic pulse radar transmits short bursts of energy and listens in the
quiet gaps between them ("you can't hear an echo while still shouting").

- **Pulse width** `τ = 20 µs` — how long the burst lasts. Controls range
  resolution for a plain pulse: `ΔR = c·τ/2 = 3 km`. Too coarse to separate
  nearby targets.
- **PRI** `T = 1 ms` — time between pulse starts; the quiet window when the
  faint echo arrives. Duty cycle `τ/T = 2%`.
- **Sampling rate** `fs = 20 MHz` → `τ·fs = 400` samples per pulse, `T·fs =
  20,000` samples per PRI.

Why the chirp? A plain pulse can't resolve close targets, but a long pulse
collects more energy. An **LFM chirp** decouples the two:

```
s(t) = exp(j·π·k·t²),   k = B/τ   (chirp rate)
instantaneous frequency  f(t) = k·t   sweeps 0 → B across the pulse
```

with bandwidth `B = 5 MHz`. Its time–bandwidth product `τ·B = 100` is the SNR
gain a matched filter will recover in Stage 3, and it compresses to range
resolution `ΔR = c/(2B) = 30 m` instead of 3 km. That is the whole point of
moving to chirps.

**Complex baseband decision** (`02-architecture.md` §5): we model the
*pulse envelope* only — no carrier. The 2.45 GHz carrier enters later only
through `λ = c/f_c` for Doppler (stage 4) and array phase (stage 6). This keeps
the simulation at manageable sample rates and matches how a real radar DSP
chain operates after down-conversion.

## Design decisions

| Decision | Choice | Why |
|---|---|---|
| Chirp generation | direct `exp(j·π·k·t²)`, not `scipy.signal.chirp` | The physics doc (§3) recommends it explicitly; it is the exact analytic form, trivially vectorized, and the *conjugated time-reversed* version doubles as the Stage 3 matched filter. |
| Sweep direction | `0 → B` (not `−B/2 → +B/2`) | Simplest, matches `f(t) = k·t`, and still "spans B" per the roadmap verification. A centered sweep is equivalent up to a phase constant — noted as an alternative. |
| Pulse length | `round(τ·fs)` = **400** samples | The pulse as a standalone burst. Clean: `20 µs × 20 MHz = 400`. |
| PRI row length | `round(T·fs)` = **20,000** samples | Each row of the train is one PRI's fast-time window, so the echo of a target lands *inside* a row at its round-trip delay (stage 2 needs this). |
| Complex dtype everywhere | `complex` | Data contracts (`02-architecture.md` §2) fix `pulse`, `pulse_train` as complex; Doppler and beamforming later need the phase. |
| `pulse_type` select | `"rect"` \| `"lfm"` via `cfg.pulse_type` | The spec requires both waveform paths; the selector lives in `transmit_waveform`. |

Rejected: returning the pulse as a full-PRI-length vector (it would force the
channel to place it at index 0 of a longer buffer and make `pulse` a mostly
silent vector — less clean for tests and plots).

## Implementation

The whole module is four tiny functions built on the two integer helpers from
algorithm step 1:

```python
def _n_pulse_samples(cfg):
    return round(cfg.pulse_width_s * cfg.fs_hz)  # 400


def _samples_per_pulse(cfg):
    return round(cfg.pri_s * cfg.fs_hz)  # 20000
```

**Step 2a — rectangular pulse** — a unit complex envelope of length 400:

```python
def rectangular_pulse(cfg):
    return np.ones(_n_pulse_samples(cfg), dtype=complex)
```

**Step 2b — LFM chirp** — the analytic form, fully vectorized (no loop).
`t` is the per-sample time grid, `k = B/τ` is the chirp rate, and the quadratic
phase `π·k·t²` is exactly the "frequency ramps linearly" of the algorithm:

```python
def lfm_chirp(cfg):
    n = _n_pulse_samples(cfg)
    t = np.arange(n) / cfg.fs_hz  # 0..20 us
    k = cfg.bandwidth_hz / cfg.pulse_width_s  # B/tau = 2.5e11 Hz/s
    return np.exp(1j * np.pi * k * t**2)
```

**Step 3 — pulse train** — `[64, 20000]`, pulse embedded at the start of each
row, silence elsewhere. The broadcasting (`train[:, :pulse.size] = pulse`)
is the vectorized version of "copy the same pulse into every row":

```python
def pulse_train(cfg):
    pulse = rectangular_pulse(cfg) if cfg.pulse_type == "rect" else lfm_chirp(cfg)
    train = np.zeros((cfg.n_pulses, _samples_per_pulse(cfg)), dtype=complex)
    train[:, : pulse.size] = pulse
    return train
```

**Step 4 — transmit waveform** — a thin wrapper selecting the type (identity
for now; exists so the CLI and later stages call one entry point):

```python
def transmit_waveform(cfg):
    return pulse_train(cfg)
```

The CLI wiring (`cli.py::plot`) generates the waveform, plots the first pulse,
and saves it to `out/stage1/pulse.png` via the existing `viz.save_plot` — the
reproducibility discipline (§5) is inherited, not reimplemented.

## Key numbers

| Quantity | Value | Source |
|---|---|---|
| Samples per pulse | `τ·fs = 400` | `20 µs × 20 MHz` |
| Samples per PRI | `T·fs = 20,000` | `1 ms × 20 MHz` |
| Chirp rate | `k = B/τ = 2.5e11 Hz/s` | `5 MHz / 20 µs` |
| Time–bandwidth product | `τ·B = 100` | the Stage 3 SNR gain |
| Frequency sweep | ~0 → 5 MHz | measured: 6 kHz → 4.98 MHz |
| Duty cycle | 2% | `τ/T` |
| Range resolution (post-compression) | `ΔR = c/(2B) = 30 m` | why the chirp matters |

## Verification

- `uv run pytest tests/test_signal_gen.py` → **12 passed**.
- Run the tests one by one (see each pass in sequence):
  `uv run pytest tests/test_signal_gen.py -v`
- Run a single test (debugging a specific behavior):
  `uv run pytest tests/test_signal_gen.py::test_lfm_chirp_sweeps_bandwidth -v`
- `uv run ruff check .` → clean.
- Chirp frequency sweep spans `B`: instantaneous frequency (from unwrapped
  phase) rises monotonically from ~6 kHz to ~4.98 MHz.
- `uv run radar plot --config configs/baseline.yaml` → `out/stage1/pulse.png`,
  a 20 µs pulse at 20 MHz.
- Full suite: `uv run pytest` → 12 passed (only Stage 1 has tests yet).

### Why these 12 tests

Tests exist to lock down the *properties the rest of the pipeline depends on*,
not to make the suite long. Each one protects a contract a later stage assumes.
They group into four aims:

**1 · Timing/shape — the sample counts must be right.**
Every later stage indexes arrays by sample (echo delay, range bins), so the
`τ·fs = 400` and `T·fs = 20,000` split is load-bearing.

| Test | Verifies | Why it matters |
|---|---|---|
| `test_rectangular_pulse_length` | pulse is exactly `τ·fs` samples | wrong length = wrong pulse duration = every delay/range downstream misreads time |
| `test_lfm_chirp_length` | chirp is exactly `τ·fs` samples | same timing check on the chirp path |

**2 · Waveform quality — the pulse really is what we claim.**
The chirp is only useful if it carries the modulation that pulse compression
later exploits.

| Test | Verifies | Why it matters |
|---|---|---|
| `test_rectangular_pulse_unit_amplitude` | envelope is flat, `|s|=1` | a rectangular pulse is *defined* by constant amplitude; any taper here is a bug |
| `test_rectangular_pulse_complex` | dtype is complex | contracts fix complex everywhere; phase appears in stages 4/6 |
| `test_lfm_chirp_complex_analytic` | unit magnitude **and** non-zero imaginary part | catches the classic mistake of building a *real* chirp — magnitude-only testing would miss it (both waveforms have `|s|=1`) |
| `test_lfm_chirp_sweeps_bandwidth` | instantaneous frequency ≈ 0 → `B` | **the** physical property: the sweep spanning `B` is what buys `ΔR = c/2B = 30 m` and the `τ·B = 100` gain |
| `test_lfm_chirp_monotonic_frequency` | frequency only rises | verifies `k = B/τ > 0` (linear, positive slope) — the "linear" in LFM |

**3 · Frame structure — the train is a usable CPI.**
Stage 2 (channel) and Stage 4 (Doppler) consume the *train*, so its layout is
a contract of its own.

| Test | Verifies | Why it matters |
|---|---|---|
| `test_pulse_train_shape` | `(n_pulses, samples_per_pulse)` = `(64, 20000)` | the matrix shape later stages index; 64 is a power of two → clean FFT in stage 4 |
| `test_pulse_train_silent_between_pulses` | only the first 400 samples per row carry energy | the quiet listen window — an echo must land in *silence*, not on self-transmission |
| `test_pulse_train_embeds_chirp` | row 0 equals `lfm_chirp` exactly | the embedding copies the real waveform, not a mangled slice |
| `test_pulse_train_rows_identical` | all 64 rows identical | coherence: coherent Doppler integration (stage 4) assumes identical pulses with stable phase |

**4 · Config selection — the switch works.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_transmit_waveform_selects_type` | `pulse_type="rect"` → real pulse, `"lfm"` → phase-modulated | the API promises two waveform paths; this proves the selector honors the config |

Method note: every test checks against an **analytical** expectation (length
formula, `0→B` sweep, `|s|=1`) rather than a saved "previous run" — that is
the testing discipline's core rule (§4). The sweep test measures phase with
`np.unwrap(np.angle(...))` and differs by one sample (4.98 vs 5.0 MHz), which
is why tolerances (`rel=0.05`) are explicit.

## Gotchas / stretch notes

- **Magnitude ≠ identity**: `|exp(jπkt²)| = 1` everywhere, so a chirp and a
  rectangular pulse look identical in magnitude. Phase (or a spectrum) is what
  shows the modulation.
- The `f_inst[-1]` sample reads 4.98 MHz, not 5.0 — the discrete chirp stops
  one sample short of `t = τ`; within the 5% tolerance the test allows.
- **Stretch (roadmap ◇)**: plot the *matched-filter-compressed* chirp and
  measure the main-lobe width (expected ~`1/B`). This previews Stage 3; we'll
  return to it when the receiver exists.
- **Alternative sweep**: `−B/2 → +B/2` is equally valid and some texts prefer
  it; it only changes the constant phase of the waveform.

## Slide-ready takeaway

- A radar transmits short pulses of energy and listens in the quiet gaps —
  pulse width `τ` and PRI `T` define the timing; at `τ=20 µs`, `T=1 ms` we get
  a 2% duty cycle.
- A plain pulse resolves targets to `c·τ/2 = 3 km` — too coarse; an **LFM
  chirp** sweeps `0→5 MHz` across the pulse and buys 30 m resolution at the
  same energy, via its time–bandwidth product `τ·B = 100`.
- We model complex baseband only (no 2.45 GHz carrier): the chirp is the
  one-liner `exp(jπkt²)`, and its conjugate-reversed copy becomes the matched
  filter in Stage 3.