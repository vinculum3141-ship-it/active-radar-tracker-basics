# Stage 2 — Moving target simulation (the channel)

## In one sentence

We build the "echo maker": the channel that takes the transmit pulse and
returns what the radar would actually receive — the pulse bounced off a target,
arriving a little late, much weaker, and buried in receiver noise.

## The problem

Stage 1 gave us the shout (the pulse train). Stage 2 answers: what comes back?
Radar is a *listening* problem — the receiver captures an energy that is tiny,
delayed, and noisy. Three physical facts define the received signal:

1. **Delay** — the wave travels out and back, so the echo of a target at range
   `R` arrives `2R/c` after transmission. At `R = 1000 m` that is 6.67 µs, or
   `round(2R/c·fs) = 133` samples. This single number is *the* bridge between
   the time axis and space, and everything downstream (Stage 3) depends on it.
2. **Attenuation** — the echo is far weaker than what was sent. In the sim we
   don't need the full `1/R⁴` range equation (the physics doc calls it an
   intuition tool, not a requirement); what matters is the **echo-to-noise
   ratio** (`SNR`), so we scale the echo to match a configured `snr_db`.
3. **Noise** — the receiver always adds random energy. We model complex
   Gaussian noise of unit power, so a 20 dB target has echo power 100× the
   noise power.

**Deliverable:** a module that, given the pulse train and a list of targets,
produces `rx_slow` — `[n_pulses, samples_per_pulse]` complex received data —
with echoes placed at their round-trip delays, scaled to their SNRs, and noise
matching.

## Approach — the algorithm in words

For each pulse in the CPI and each target:

1. **Place the echo.** Compute the round-trip delay `n_delay = round(2R/c·fs)`
   and write a scaled copy of the transmit pulse into the receive window
   starting at that sample. The window is one full PRI (20,000 samples), so the
   echo lands in the *silence* after the transmitted pulse.
2. **Scale by SNR.** The echo amplitude is `10^(snr_db/20)` against unit-power
   noise — power `10^(snr_db/10)`. At 20 dB that's an amplitude of 10.
3. **Add noise once.** Sum all targets' echoes into each PRI row, then add a
   single complex-Gaussian noise draw per row. Noise is a property of the
   *receiver*, not of each target — adding it per target would inflate
   multi-target SNR.
4. **Repeat over the CPI.** Do this for all 64 pulses and stack the rows into
   `[64, 20000]`.

The single-target case of steps 1–3 is exactly what `propagate` returns; the
multi-target, multi-pulse case is `simulate_channel`.

## What we built

`src/radar/channel.py` per the API spec (`04-python-discipline.md` §3):

| Algorithm step | Function |
|---|---|
| 1 · place echo (delay + scale) | `_echo` (private helper) |
| 3 · noise draw | `_complex_noise` (private helper) |
| 1–3 · one pulse, one target | `propagate(pulse, target, cfg, rng)` |
| 1–4 · whole CPI, all targets | `simulate_channel(tx, targets, cfg, rng)` |
| data object | `Target` (dataclass: `range_m`, `velocity_mps`, `angle_deg=None`, `snr_db=20.0`) |

**Files touched:** `src/radar/channel.py`, `tests/test_channel.py`.

## Physics in play

- **Range–delay** (`01-physics.md` §1): `R = c·τ_delay/2`, so delay in samples
  is `n_delay = round(2R/c·fs)`. One range bin = `c/(2fs) = 7.5 m`.
- **Radar range equation**: `P_r ∝ 1/R⁴` — why echoes are tiny in reality, but
  explicitly *not* needed for the sim; we parametrize the result directly as
  SNR.
- **Noise**: complex white Gaussian, unit power. Signal power relative to noise
  power is the SNR that Stage 3's matched filter will exploit.
- **Velocity** is carried on `Target` but **deliberately unused here**: within
  one CPI the target moves a fraction of a sample and its *delay* is
  effectively constant. The per-pulse *phase rotation* (Doppler) is the Stage 4
  concept; keeping the channel a pure delay/attenuation/noise model keeps this
  stage focused (the roadmap puts Doppler in Stage 4).

## Design decisions

| Decision | Choice | Why |
|---|---|---|
| Where noise is added | once per PRI row in `simulate_channel`; `propagate` adds it for its own single-target path | noise is a receiver property; adding per-target would double noise power for two targets and break the stretch |
| Shared `_echo` helper | `_echo` = noiseless delay+scale; `propagate` = `_echo` + noise; `simulate_channel` = Σ `_echo` + noise | honors the API ("propagate → noisy echo") *and* keeps multi-target SNR correct — no duplicated logic |
| Attenuation | amplitude `10^(snr_db/20)` vs unit noise | directly satisfies "noise power matches SNR"; range equation deferred as an intuition tool |
| Delay per pulse | constant within the CPI | target moves < 1 sample over 64 pulses; Doppler phase deferred to Stage 4 |
| Noise model | complex Gaussian, variance 1/2 per quadrature (unit total power) | standard complex-baseband receiver noise; reproducible via `rng` |
| `Target` fields | `velocity_mps` and `angle_deg` present but only `range_m`/`snr_db` used | the data contract is fixed up front (contracts-first); stages 4 and 6+ consume them |

Rejected: adding noise inside `propagate` and summing `propagate` outputs in
`simulate_channel` — correct for one target, but two targets would see double
noise power (SNR halved). The `_echo` split avoids that trap.

## Implementation

The four building blocks are small. The echo for one pulse + one target
(noiseless):

```python
def _echo(pulse, target, cfg):
    n_delay = round(2 * target.range_m / C_MPS * cfg.fs_hz)  # 133 for 1000 m
    amplitude = 10 ** (target.snr_db / 20.0)  # 10 at 20 dB
    rx = np.zeros(_samples_per_pulse(cfg), dtype=complex)  # 20000 samples
    n = min(pulse.size, rx.size - n_delay)
    if n > 0:
        rx[n_delay : n_delay + n] = amplitude * pulse[:n]
    return rx
```

Unit-power complex noise (variance 1/2 in each quadrature adds to 1):

```python
def _complex_noise(shape, rng):
    return rng.normal(0.0, 1.0 / np.sqrt(2.0), shape) + 1j * rng.normal(
        0.0, 1.0 / np.sqrt(2.0), shape
    )
```

The two public paths. Single pulse, single target:

```python
def propagate(pulse, target, cfg, rng):
    return _echo(pulse, target, cfg) + _complex_noise(_samples_per_pulse(cfg), rng)
```

Whole CPI, all targets — sum echoes, then one noise draw per row:

```python
def simulate_channel(tx, targets, cfg, rng):
    rx = np.zeros_like(tx)  # [n_pulses, samples_per_pulse]
    for target in targets:
        for n in range(cfg.n_pulses):
            rx[n] += _echo(tx[n], target, cfg)
    rx += _complex_noise(rx.shape, rng)
    return rx
```

The double loop is `n_pulses × n_targets` — deliberately simple; the array
version (stage 8's interferer extension) can vectorize later.

## Key numbers

| Quantity | Value | Source |
|---|---|---|
| Delay at 1000 m | `2R/c·fs = 133` samples (6.67 µs) | the course's first analytic truth |
| Delay at 500 m | `67` samples | scale check on the formula |
| One range bin | `c/(2fs) = 7.5 m` | fast-time sampling |
| Noise power | 1 (unit complex Gaussian) | variance 1/2 per quadrature |
| Echo amplitude @ 20 dB | `10^(20/20) = 10` | power `10^(20/10) = 100` |
| Unambiguous range | `c·T/2 = 150 km` | no range aliasing at our ranges |
| Received shape | `[64, 20000]` complex | `rx_slow` data contract |

## Verification

- `uv run pytest tests/test_channel.py` → **11 passed**.
- `uv run ruff check .`, `uv run ruff format --check .` → clean.
- Full suite: **23 passed** (stage 1 + stage 2).

### Why these 11 tests

**1 · Contract & shape — the output must match what the pipeline consumes.**
Stage 3's receiver indexes these rows; `rx_slow` must be `[64, 20000]` complex.

| Test | Verifies | Why it matters |
|---|---|---|
| `test_target_defaults` | `angle_deg=None`, `snr_db=20.0` | the data contract's defaults; stages 6+ add angle |
| `test_simulate_channel_shape` | output `(64, 20000)` | the `rx_slow` shape every downstream stage indexes |
| `test_complex_dtype` | complex128 | phase is required from Stage 4 on |

**2 · Delay — the range→time mapping must be exact.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_delay_1000m` | echo onset at **133** | the whole point of the stage; Stage 3 measures range *from this* |
| `test_delay_500m` | onset at 67 = `round(2·500/c·fs)` | proves the formula scales, not a hard-coded 133 |

**3 · Noise & SNR — the numbers must mean what they claim.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_noise_power_unit` | quiet-region power ≈ 1 | the SNR scale factor is only meaningful against known noise |
| `test_signal_power_matches_snr` | echo power ≈ 100 at 20 dB | amplitude `10^(snr/20)` gives exactly the promised power |
| `test_measured_snr_matches` | measured SNR ≈ 20 dB (power ratio) | the receiver actually delivers the configured SNR |

**4 · Reproducibility & single-target path.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_deterministic_seed` | same seed → identical output | reproducibility discipline (§2); makes the lab's error-vs-SNR curve reproducible |
| `test_propagate_single_pulse` | `propagate` = echo + noise, onset 133 | the API's self-contained single-pulse path behaves like the full one |

**5 · Stretch (roadmap ◇) — two targets.**

| Test | Verifies | Why it matters |
|---|---|---|
| `test_two_targets_stretch` | echoes at *both* delays (1000 m & 5000 m) | multi-target channel; ranges spaced > 3 km so the 400-sample echoes don't overlap |

Method notes: echoes are detected by a **half-amplitude onset threshold**, not
`argmax` — noise can shift the max, and overlapping echoes would merge into one
peak. Real multi-target detection is the matched filter's job (Stage 3).

## Gotchas / stretch notes

- **Noise placement**: adding noise per *target* quietly doubles noise power
  for two targets — the `_echo`/single-noise-draw split exists to prevent this.
  The doc for this lives in the design-decision table above.
- **Echo detection**: `argmax` of a noisy echo can be a few samples off;
  threshold-on-onset is robust. Overlapping echoes (targets closer than
  `c·τ/2 = 3 km`) can't be separated by inspection — that's exactly why Stage 3
  exists.
- **Velocity is dormant**: `velocity_mps` is carried but does nothing yet.
  Stage 4 adds the per-pulse phase ramp that turns it into Doppler. A learner
  who tries to see velocity in the stage-2 echo won't — correct.
- **Stretch (roadmap ◇)**: two targets is done (`test_two_targets_stretch`);
  a natural follow-up is to make the interferer (Stage 8) a `Target` with an
  `angle_deg` — the dataclass already has the field.

## Slide-ready takeaway

- The echo of `R = 1000 m` arrives exactly **133 samples** late (`round(2R/c·fs)`);
  delay is the language that turns time into distance.
- The received signal is *echo scaled to SNR + receiver noise*: amplitude
  `10^(snr_db/20)` against unit-power noise, so a 20 dB target is 100× the
  noise floor.
- Noise is added **once per PRI**, not per target — a receiver sees one noise
  field, and summing per-target noise would quietly halve multi-target SNR.
- Velocity travels on `Target` now but is deliberately unused until Stage 4's
  Doppler — a clean contract-first boundary between stages.