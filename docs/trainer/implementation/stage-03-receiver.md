# Stage 3 — Range estimation (matched filter)

## In one sentence

We turn the noisy echo into a single clean spike whose position *is* the
target's range — the matched filter coherently sums the pulse energy so a
range estimate falls out of one `argmax`.

## The problem

Stage 2 left us with the echo: a 400-sample pulse at sample 133, amplitude 10,
buried in unit noise. Three problems stand between that and "the target is at
1000 m":

1. **The echo is spread over 400 samples** — where exactly *is* it? The pulse
   is flat, so `argmax` of the raw echo lands on noise, not on the target.
2. **SNR is low** — 20 dB *per sample*; any single-sample decision is noise.
3. **Range must be exact** — the course's first deliverable is a range within
   one range bin (7.5 m) of truth.

The matched filter solves all three at once: correlate the received signal
with the transmit pulse. Where the pulse is present, the 400 samples add up
coherently (peak ∝ 400); where it isn't, noise adds incoherently (∝ √400).
The result is a spike ~4 samples wide (the compressed pulse) whose position
is the round-trip delay, plus a processing gain of `N = 400` (26 dB) — enough
to lift a 20 dB echo to a 46 dB detection.

**Deliverable:** `receiver.py` (`matched_filter`, `range_from_delay`,
`detect_peaks`) + the `Detection` data object, and `viz.plot_echo` /
`viz.plot_range_profile` for the milestone plot set.

## Approach — the algorithm in words

1. **Match-filter** each received pulse row against the transmit pulse
   (`scipy.signal.correlate`, `mode="same"` so the time axis is unchanged).
   The compressed peak lands at `delay + len(pulse)//2` (empirically pinned:
   'same' mode centers the kernel, shifting the peak by half its length).
2. **Convert the peak index to delay** by subtracting that constant offset
   (`len(pulse)//2 = 200`).
3. **Convert delay to range** with `R = c·t/2`: `range_from_delay(delay) =
   delay · c/(2·fs)`, 7.5 m per sample.
4. **Detect peaks**: find local maxima of `|matched|` whose power is
   `threshold_db` above a noise floor, keeping the strongest per
   pulse-length window (chirp sidelobes are ~13 dB below the mainlobe and
   live inside that window). Report range + SNR per detection.

## What we built

`src/radar/receiver.py` per the API spec (`04-python-discipline.md` §3):

| Algorithm step | Function |
|---|---|
| 1 · correlate | `matched_filter(rx, tx_pulse)` |
| 3 · delay → range | `range_from_delay(delay_samples, cfg)` |
| 4 · peaks + SNR | `detect_peaks(matched, cfg, threshold_db=10.0)` |
| result object | `Detection` (dataclass: `range_m`, `velocity=None`, `snr_db=None`, `angle_deg=None`) |

Plus `viz.plot_echo(rx, matched, cfg)` (echo vs matched two-panel) and
`viz.plot_range_profile(matched, cfg)` (magnitude vs range in km).

**Files touched:** `src/radar/receiver.py`, `src/radar/viz.py`,
`src/radar/cli.py` (the `plot` command now emits the full week-1 plot set),
`tests/test_receiver.py`.

## Physics in play

- **Matched filter** (`01-physics.md` §2): for a known signal in white noise,
  the filter that maximizes output SNR is the cross-correlation with the
  transmit signal. It coherently sums signal energy (∝ `τ`) while noise sums
  incoherently (∝ `√τ`).
- **Pulse compression** (§3): the LFM chirp compresses to a ~`1/B`-wide spike;
  `ΔR = c/(2B) = 30 m`, versus 3 km for the raw 20 µs pulse.
- **Range–delay** (§1): `R = c·τ/2` — the compressed peak's position is the
  round-trip time, halved and sped up.

**Processing gain — a nuance worth teaching.** The textbook gain is the
time–bandwidth product `τ·B = 100` (20 dB). We measure 26 dB
(`N = τ·fs = 400`). Both are right: the gain is the number of samples
integrated coherently, and we oversample 4× (fs = 20 MHz vs B = 5 MHz). At
critical sampling `fs = B` the two numbers coincide; our 4× oversampling buys
4× extra gain. If the learner asks "why 46 dB not 40 dB?" — that's the answer.

## Design decisions

| Decision | Choice | Why |
|---|---|---|
| Correlation mode | `scipy.signal.correlate(..., mode="same")` | output length = input, so the time axis is preserved for plotting and peak-index math |
| Peak-index convention | peak at `delay + len(pulse)//2` | pinned empirically (full/valid modes shift differently); the offset is a constant derived from `cfg`, so `detect_peaks` never sees the raw pulse |
| Noise floor | median of `|matched|²`, corrected by `1/ln(2)` | median is robust to the narrow compressed-signal region (its sidelobe energy would bias a mean); the chi-square correction turns the median into a true mean-power estimate |
| Peak separation | `find_peaks(distance=len(pulse))` | chirp autocorrelation sidelobes (~-13 dB) sit within one pulse length of the mainlobe; keeping the strongest peak per window yields one detection per resolved target |
| Detection result | `Detection` dataclass with `range_m`, `snr_db`, `velocity`/`angle` as `None` | §2 convention (dataclasses for data objects); the unused fields are filled by stages 4+ |
| Threshold | power ratio `threshold_db` (default 10) over the floor | standard CFAR-style gate; nonzero false-alarm rate at 10 dB is *real* behavior, see gotchas |

Rejected: thresholding `|matched|` by absolute height (config-dependent, not
reproducible across SNR); a per-target loop in `matched_filter` over 2D rows
is fine (64 rows), but full vectorization is deferred to the array stages.

## Implementation

The three public functions are small because the heavy lifting is
`scipy.signal.correlate` and `find_peaks`:

```python
def matched_filter(rx, tx_pulse):
    if rx.ndim == 1:
        return correlate(rx, tx_pulse, mode="same")
    return np.array([correlate(row, tx_pulse, mode="same") for row in rx])
```

```python
def range_from_delay(delay_samples, cfg):
    return delay_samples * C_MPS / (2 * cfg.fs_hz)  # 7.5 m per sample
```

```python
def detect_peaks(matched, cfg, threshold_db=10.0):
    if matched.ndim == 2:
        matched = matched[0]
    mag = np.abs(matched)
    noise_power = float(np.median(mag**2) / np.log(2.0))
    threshold_power = noise_power * 10 ** (threshold_db / 10.0)
    peak_indices, _ = find_peaks(
        mag, height=np.sqrt(threshold_power), distance=_pulse_samples(cfg)
    )
    return [
        Detection(
            range_m=range_from_delay(i - _pulse_offset(cfg), cfg),
            snr_db=10 * np.log10(float(mag[i] ** 2) / noise_power),
        )
        for i in peak_indices
    ]
```

`C_MPS` is imported from `channel.py` (single source of truth for `c`).

## Key numbers

| Quantity | Value | Source |
|---|---|---|
| Compressed peak location | `delay + 200` (index 333 for 1000 m) | empirical correlate pinning |
| Compressed half-power width | ~6 samples (vs 400) | sharpness check |
| Matched-filter gain | `N = 400` → 26 dB (not `τ·B = 100`; 4× oversampling) | physics §2 + measurement |
| Detection range @ 20 dB | 997.5 m (2.5 m from truth, < 7.5 m bin) | verify |
| Detected SNR @ 20 dB in | 45.8 dB | 20 + 26 dB |
| Range axis | `(i - 200) · 7.5 m`, spans ~150 km | `plot_range_profile` |
| False alarms @ 10 dB | ~1 per 20000-sample scan | CFAR reality (see gotchas) |

## Verification

- `uv run pytest tests/test_receiver.py` → **10 passed**.
- `uv run ruff check .`, `uv run ruff format --check .` → clean.
- Full suite: **33 passed** (stages 1-3). Week 1 milestone plot set + tests green.

### Why these 10 tests

**1 · Contract & sharpness — the filter does its job.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_matched_filter_shape_1d/2d` | output shape = input shape | `mode="same"` contract; stage 4 indexes these rows |
| `test_matched_filter_peak_at_delay_plus_offset` | argmax at 133 + 200 = 333 | pins the offset convention the whole stage rests on |
| `test_matched_filter_compresses_pulse` | half-power width < 40 vs 400 | the "visibly sharper" verification, quantified |
| `test_range_from_delay` | 133 → 997.5 m; 1 sample → 7.5 m | the delay→range bridge |

**2 · Detection — range and SNR must be right.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_detect_peaks_single_target` | one detection, 997.5 m (±7.5 m bin) | milestone: "within one range bin of truth at 20 dB" |
| `test_detect_peaks_snr_matches_gain` | SNR ≈ 46 dB (20 in + 26 gain) | the physics story, measured end to end |
| `test_detect_peaks_two_targets_stretch` | both 1000 m and 5000 m detected | roadmap stretch ◇ |
| `test_detect_peaks_noise_only` | empty at 15 dB threshold | no false alarms when there's no target (deterministic) |
| `test_detect_peaks_threshold_gates_by_height` | synthetic spike: seen at 20 dB, gated at 30 dB | isolates the threshold mechanism from noise |

Method notes: the noise-only and height-gate tests are built to be
**deterministic** — a real noisy weak target is *not* used for the gate test
because at a 3 dB threshold noise peaks legitimately outcompete it (that's the
false-alarm story, not a gate failure).

## Gotchas / stretch notes

- **The `mode="same"` offset is real.** Empirically: `full` shifts by
  `len(pulse)-1`, `same` by `len(pulse)//2`, `valid` by 0 but shortens the
  output. We chose `same` for the preserved axis and subtract the constant —
  but a learner implementing with `full` or `argmax` without the offset will
  silently report a range that's 200 samples (1.5 km) off. Test #2 pins it.
- **Mean noise floor is biased by the compressed target.** The chirp
  autocorrelation carries `N² = 160000` units of energy in its sidelobes;
  averaged over the scan it inflates the noise floor and under-reports SNR by
  ~10 dB. Median + chi-square correction (`1/ln2`) fixes it. Test #6 would
  fail without it.
- **False alarms are real.** At the default 10 dB threshold, a 20000-sample
  noise-only scan produces ~1 false detection (we observed one at 59 km, SNR
  10.8 dB). That is correct CFAR behavior — the threshold trades sensitivity
  against false alarms. The noise test uses 15 dB for a clean empty answer;
  the teaching point is "lower the threshold, more false alarms."
- **Stretch (roadmap ◇):** two targets is done (`test_detect_peaks_two_targets_stretch`).
  Natural follow-ups: Taylor/Hamming windowing to cut sidelobes below
  `threshold_db` (so closer targets resolve), and an SNR-vs-range curve —
  which is exactly Lab L1's sweep.

## Slide-ready takeaway

- The matched filter turns the 400-sample echo into a **6-sample spike whose
  position is the range**: peak at `delay + 200`, converted via `R = c·t/2`.
- One `argmax` after correlation beats staring at a noisy echo: the 20 dB
  echo becomes a **46 dB detection** — the `N = 400` coherent-processing gain
  (26 dB), more than the textbook `τ·B` because we oversample 4×.
- The range estimate is **997.5 m for a 1000 m target** — within one 7.5 m
  range bin — and the milestone plot set (pulse, echo, matched, range
  profile) is complete.