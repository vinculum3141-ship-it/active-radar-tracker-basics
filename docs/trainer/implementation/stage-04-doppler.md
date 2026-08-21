# Stage 4 — Doppler / velocity (range-Doppler)

## In one sentence

We stack the 64 matched-filter pulses and take a Fourier transform along slow
time, turning "phase rotation from pulse to pulse" into a velocity axis — so the
target shows up as a blob at its range *and* its (possibly folded) velocity.

## The problem

Stages 1–3 give us range, but not motion. A target at 1000 m could be sitting
still or closing at 40 m/s — the range profile looks identical either way. The
only thing the radial velocity changes is the *phase* of the echo from one PRI
to the next (§4: within a 20 µs pulse the target moves a fraction of a
wavelength, so fast-time is static; across a 1 ms PRI it moves enough to rotate
the phase).

So three things are missing:

1. **No motion in the channel yet.** Stage 2 placed the echo at a fixed delay
   for every pulse, so `velocity_mps` was carried but never *exercised*. We must
   inject a per-pulse phase ramp.
2. **No slow-time spectrum.** We have 64 rows of matched-filter output; we need
   a Doppler spectrum per range bin.
3. **A velocity axis + a 2-D map** to *see* the target blob (the Week 2
   milestone artifact).

**Deliverable:** `doppler.py` (`range_doppler_map`, `range_axis`,
`velocity_axis`) + `viz.plot_rd_map`, and the slow-time phase ramp added to
`channel.simulate_channel`.

## Approach — the algorithm in words

1. **Encode velocity in the channel.** For pulse `n`, rotate the echo phase by
   `2π·f_d·T·n` where `f_d = 2v/λ`, `T = PRI`, `λ = c/f_c`. This is the only
   place velocity enters the simulation.
2. **Match-filter every pulse** (already done in Stage 3) → a
   `[n_pulses, samples]` matrix.
3. **FFT along slow time (axis 0)** and `fftshift` so zero Doppler is centered
   → the range-Doppler map `[doppler_bin, range_bin]`.
4. **Label the axes.** Range axis mirrors the range profile (`(i - N_pulse//2)·
   c/(2fs)`); velocity axis is `(k - N/2)·Δv` with `Δv = λ/(2NT)`.
5. **Find the peak** in the map at the target's range bin; its Doppler cell is
   the (possibly aliased) velocity.

## What we built

`src/radar/doppler.py` per the API spec (`04-python-discipline.md` §3):

| Algorithm step | Function |
|---|---|
| 1 · slow-time phase | `channel.simulate_channel(..., apply_doppler=True)` (opt-in `phase = exp(j2π f_d T n)`) |
| 3 · slow-time FFT | `range_doppler_map(matched, cfg)` |
| 4 · axis labels | `range_axis(cfg)`, `velocity_axis(cfg)` |
| plot | `viz.plot_rd_map(rd_map, cfg)` (dB magnitude, range × velocity) |

**Files touched:** `src/radar/channel.py` (slow-time phase ramp in
`simulate_channel` + helpers `_wavelength_m`, `_doppler_hz`),
`src/radar/doppler.py`, `src/radar/viz.py`, `tests/test_doppler.py`.

> **Note on scope vs. the roadmap listing.** The roadmap Stage 4 "code task"
> names only `doppler.py` + `viz.py`, but a Doppler peak cannot appear unless
> the channel actually imparts the per-pulse phase. So this stage *also* extends
> `channel.simulate_channel` — but **opt-in**, not unconditional: the new
> `apply_doppler: bool = False` keyword defaults to the exact Stage 1–3
> behavior (delay + attenuation + noise, no slow-time phase), so earlier stages
> are byte-for-byte untouched. Stage 4 passes `apply_doppler=True`. The factor
> is unit-modulus, so when enabled magnitude/delay/power (and thus Stage 2/3
> checks) are still unaffected.

## Physics in play

- **Doppler shift** (§4): `f_d = 2v/λ`, `λ = c/f_c or f_c`. With `f_c =
  2.45 GHz`, `λ ≈ 12.2 cm`, so `f_d ≈ 16.3 Hz per m/s`.
- **Slow vs. fast time:** fast time (within a pulse) → delay → range; slow time
  (pulse index) → phase rotation → Doppler → velocity.
- **Range-Doppler map:** FFT of the slow-time sequence in each range bin;
  `v = λ·f_d/2`.
- **Resolution & ambiguity:**
  - `Δv = λ/(2·N·T) = 0.96 m/s` (bin width).
  - `v_max = λ/(4·T) ≈ 30.6 m/s` (±, the slow-time Nyquist).

**The deliberate friction (teaching point).** The baseline target is `v = 40
m/s > v_max ≈ 30.6 m/s`, so it **aliases**. `f_d = 653.3 Hz` exceeds the ±500
Hz slow-time Nyquist; the FFT folds it to `653.3 − 1000 = −346.7 Hz`, which
reads as `v ≈ −21.2 m/s`. The map is *correctly* reporting a folded velocity —
that is the exercise, resolved in Lab L2 by raising the PRF.

## Design decisions

| Decision | Choice | Why |
|---|---|---|
| Where Doppler enters | per-pulse phase in `simulate_channel` | velocity is a channel effect (radial motion); one place, physically honest |
| Phase multiplies echo (not added) | `rx[n] += phase * _echo(...)` | `|phase| = 1`, so magnitude/delay/power are unchanged → Stages 1–3 stay green |
| FFT axis | `np.fft.fft(matched, axis=0)` (slow time) | rows = pulses; columns = range bins; this yields a Doppler spectrum per range cell |
| `fftshift` on Doppler axis | applied in `range_doppler_map` | centers zero velocity; pairs with `velocity_axis` so the peak bin maps to the right sign |
| Range axis convention | identical to `plot_range_profile` | target at 1000 m lands at ~1000 m in both the 1-D and 2-D views (no offset surprises) |
| `velocity_axis` zero center | `(k - N//2)·Δv` | fftshift axis: bin `N//2` = 0 m/s, lower half negative, upper half positive |

Rejected: putting the Doppler phase in the receiver (it belongs to the channel
model — the radar doesn't *know* the velocity, the signal does); and
windowing slow time by default (it's the Stage 4 stretch ◇, left out of the
must-have so the bin width stays exactly `Δv`).

## Implementation

The channel edit — the slow-time phase ramp is **opt-in** (default off, so
Stage 1–3 behavior is preserved exactly):

```python
def simulate_channel(tx, targets, cfg, rng, *, apply_doppler=False):
    rx = np.zeros_like(tx)  # [n_pulses, samples_per_pulse]
    for target in targets:
        fd = _doppler_hz(target.velocity_mps, cfg) if apply_doppler else 0.0
        for n in range(cfg.n_pulses):
            phase = (
                np.exp(1j * 2.0 * np.pi * fd * cfg.pri_s * n) if apply_doppler else 1.0
            )
            rx[n] += phase * _echo(tx[n], target, cfg)
    rx += _complex_noise(rx.shape, rng)
    return rx
```

Stage 4 calls it with `apply_doppler=True`; Stages 1–3 (and their tests) call
it with the default and see no change.

The map and axes are short because the heavy lifting is `np.fft`:

```python
def range_doppler_map(matched, cfg):
    return np.fft.fftshift(np.fft.fft(matched, axis=0), axes=0)


def range_axis(cfg):
    n_pulse = round(cfg.pulse_width_s * cfg.fs_hz)
    n_samples = round(cfg.pri_s * cfg.fs_hz)
    return (np.arange(n_samples) - n_pulse // 2) * C_MPS / (2.0 * cfg.fs_hz)


def velocity_axis(cfg):
    wavelength = C_MPS / cfg.fc_hz
    delta_v = wavelength / (2.0 * cfg.n_pulses * cfg.pri_s)
    return (np.arange(cfg.n_pulses) - cfg.n_pulses // 2) * delta_v
```

`plot_rd_map` shows `20·log10(|rd|)` relative to the map peak (so the blob
sits well above the −60 dB floor) with range on x (km) and velocity on y (m/s).

## Key numbers

| Quantity | Value | Source |
|---|---|---|
| Wavelength `λ` | `0.12245 m` | `c / f_c` |
| Doppler `f_d` (40 m/s) | `653.3 Hz` (≈16.3 Hz/m/s · 40) | `2v/λ` |
| PRF / slow-time Nyquist | `1000 Hz` / `±500 Hz` | `1/T` |
| Folded apparent velocity (40 m/s) | `−21.2 m/s` (peak landed at −21.05 m/s) | `f_d − PRF` wrapped, `/2·λ` |
| Velocity bin width `Δv` | `0.957 m/s` | `λ/(2NT)` |
| Max unambiguous `v_max` | `30.6 m/s` | `λ/(4T)` |
| RD map shape | `(64, 20000)` | `[n_pulses, samples]` |
| Peak location (baseline) | range bin ~997.5 m, Doppler bin 10 | verify |
| Stationary target | peak at center Doppler bin (0 m/s) | verify |

## Verification

- `uv run pytest tests/test_doppler.py` → **6 passed**.
- `uv run ruff check .` → clean.
- Full suite: **39 passed** (stages 1–4). Week 1 still reproduces its notebook
  numbers (channel phase is unit-modulus, so magnitude-based checks unchanged).

### Why these 6 tests

**1 · Map contract & axes.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_map_dimensions` | shape `(n_pulses, samples)` | Stage 5 will index these rows/cols |
| `test_velocity_axis_resolution` | `Δv = λ/(2NT)`, center bin = 0 | the axis the peak is read against |
| `test_range_axis_centered_on_target` | 1000 m target at ~1000 m | matches range profile, no offset surprise |

**2 · The Doppler peak lands where physics says.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_peak_velocity_aliased` | 40 m/s → folded −21.2 m/s within `Δv/2` | the headline roadmap check; proves aliasing is modeled correctly |
| `test_peak_velocity_unambiguous` | 15 m/s → true 15 m/s within `Δv/2` | confirms a clean (sub-`v_max`) velocity reads true |
| `test_zero_velocity_peak_at_center` | 0 m/s → center Doppler bin | degenerate case; no drift |

Method note: the aliased test computes the *analytic* folded velocity
(`((f_d + PRF/2) mod PRF) − PRF/2` → velocity) and asserts the measured peak is
within half a bin — it does **not** compare against the raw 40 m/s, which would
be wrong (that's the aliasing lesson).

## Gotchas / stretch notes

- **No Doppler visible?** The phase ramp is the usual culprit (applied to the
  wrong path, or `fd = 0` because `velocity_mps` wasn't threaded into
  `simulate_channel`). Our channel edit is the fix.
- **Peak at the wrong sign/bin?** Forgot `fftshift` → the peak reads at `+21`
  instead of the folded `−21`, or vice-versa. `range_doppler_map` shifts;
  `velocity_axis` assumes it.
- **Aliasing is the point, not a bug.** The baseline 40 m/s *must* appear at
  −21.2 m/s; raising the PRF (Lab L2, `T: 1 ms → 0.5 ms`) doubles `v_max` to
  61.2 m/s so the same target then reads its true +40 m/s.
- **Stretch (roadmap ◇):** (a) the aliasing experiment above is demonstrable
  via `test_peak_velocity_aliased`; (b) add a slow-time window (e.g. Hamming)
  before the FFT to suppress Doppler sidelobes — left out of the must-have so
  `Δv` stays exact. `plot_rd_map` already renders the result.

## Slide-ready takeaway

- Velocity is **phase rotation from pulse to pulse**: `f_d = 2v/λ` — fast time
  gives range, slow time gives velocity.
- Stack 64 matched-filter pulses, FFT along slow time → a **range-Doppler map**;
  `Δv = λ/(2NT) = 0.96 m/s`, `v_max = λ/(4T) = 30.6 m/s`.
- The baseline 40 m/s target **aliases** to **−21.2 m/s** — the map is right,
  the velocity is folded (Lab L2 raises the PRF to un-wrap it).
