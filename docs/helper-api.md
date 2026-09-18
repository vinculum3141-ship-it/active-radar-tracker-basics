# Helper scripts for beginner notebooks

This page is a notebook-user guide to the small helper package used throughout the beginner radar course.

The goal is not to be a formal public API. The goal is to help a learner quickly answer: "Which helper do I use for this chapter?" and "What does this helper actually represent in the physics?"

## What these helpers are for

The helper scripts keep the notebook code readable while keeping the math transparent.
They are intentionally narrow and focused on specific radar concepts:

- wavelength and range math
- pulse and chirp generation
- channel and noise modeling
- Doppler and range-Doppler processing
- array geometry and beamforming
- Kalman tracking

The philosophy is simple: the helper should make the notebook easier to follow without hiding the physics behind a black box.

## Quick start by notebook chapter

Use this map when you are working chapter by chapter:

- Chapter 00 — `constants`, `math`
- Chapter 01 — `waveforms`, `math`
- Chapter 02 — `math`, `constants`
- Chapter 03 — `channel`, `math`
- Chapter 04 — `waveforms`, `math`
- Chapter 05 — `doppler`, `channel`, `math`
- Chapter 06 — `kalman`, `math`
- Chapter 07 — `array`, `steering`
- Chapter 08 — `doa`, `array`, `steering`
- Chapter 09 — `steering`, `doa`, `array`
- Chapter 10 — `plotting`, `channel`, `kalman`, `array`

If you are unsure where to start, begin with `constants` and `math`. Those are the baseline helpers used across most notebooks.

## Helper cheat sheet

Use this as the fastest lookup table for the beginner notebooks.

| Need | Module | Typical notebook use |
| --- | --- | --- |
| Shared baseline parameters | `constants` | Chapter 00 onward |
| Range, delay, resolution, wavelength | `math` | 00, 02, 04, 05 |
| Pulses, chirps, matched filtering | `waveforms` | 01, 04, 05 |
| Echoes, attenuated return, AWGN | `channel` | 03, 05, 10 |
| Doppler and range-Doppler | `doppler` | 05 |
| Array geometry and beam pattern | `array` | 07, 08, 09 |
| Spatial spectra and DOA | `doa` | 08, 09 |
| Beam steering and adaptive nulling | `steering` | 07, 09 |
| Tracking state prediction and update | `kalman` | 06, 10 |
| Shared notebook plotting | `plotting` | 10 and other visuals |

## Helper modules and what they do

### `constants`

Purpose: baseline radar values and teaching-friendly default system parameters.

Typical use:

- set the shared value set for all later notebooks
- keep chapter-to-chapter numbers consistent
- avoid repeating the same reference values in every notebook

Useful functions:

- `baseline_spec()`
- `BaselineRadarSpec`
- `RADAR_CONSTANTS`

### `math`

Purpose: the core range, delay, wavelength, and resolution formulas that appear repeatedly.

Typical use:

- convert delay to range
- calculate wavelength from carrier frequency
- compute duty cycle and resolution

Useful functions:

- `wavelength_m()`
- `duty_cycle()`
- `delay_samples_for_range()`
- `range_from_delay_samples()`
- `range_resolution_from_bandwidth()`
- `range_resolution_from_pulse_width()`

### `waveforms`

Purpose: pulse generation, chirp generation, and matched filtering.

Typical use:

- generate an LFM chirp
- create a rectangular pulse
- run matched filtering on received data

Useful functions:

- `rectangular_pulse()`
- `lfm_chirp()`
- `matched_filter()`
- `instantaneous_frequency_hz()`

### `channel`

Purpose: model echoes, delay, attenuation, and noise in the radar channel.

Typical use:

- add a delayed return signal
- create a simple target echo model
- add AWGN to the received waveform

Useful functions:

- `single_target_channel()`
- `add_echo()`
- `awgn()`

### `doppler`

Purpose: compute Doppler shifts and build range-Doppler views.

Typical use:

- convert velocity into Doppler frequency
- estimate Doppler from a pulse stack
- visualize the range-Doppler map

Useful functions:

- `doppler_frequency_hz()`
- `velocity_from_doppler()`
- `build_pulse_stack()`
- `range_doppler_map()`

### `array`

Purpose: model array geometry and steering phases.

Typical use:

- compute inter-element phase shift
- build steering vectors
- compute array factor patterns

Useful functions:

- `inter_element_phase_rad()`
- `steering_vector()`
- `array_factor()`
- `first_null_angle_deg()`

### `doa`

Purpose: spatial spectrum estimation for direction-of-arrival problems.

Typical use:

- estimate the arrival angle from received snapshots
- compare Bartlett and MVDR-style spatial spectra

Useful functions:

- `sample_covariance()`
- `bartlett_spectrum()`
- `mvdr_spectrum()`

### `steering`

Purpose: beam pointing and adaptive nulling weights.

Typical use:

- point the beam in a chosen direction
- compute nulling weights for interference suppression

Useful functions:

- `steering_weights()`
- `lcmv_weights()`

### `kalman`

Purpose: simple constant-velocity tracking logic used in the tracking notebook.

Typical use:

- predict state forward in time
- update the estimate using a measurement
- run a complete tracking loop

Useful functions:

- `state_transition_matrix()`
- `predict()`
- `update()`
- `run_kalman_track()`

### `plotting`

Purpose: shared plotting style and notebook-friendly display helpers.

Typical use:

- keep the plots visually consistent across notebooks
- shorten repetitive plotting code in classroom examples

Useful functions:

- look for the plotting helpers used in the notebook examples and keep their names aligned with the chapter visuals

## Typical usage pattern

The usual beginner pattern is straightforward:

```python
from beginner.helpers import baseline_spec, lfm_chirp, matched_filter

spec = baseline_spec()
chirp = lfm_chirp(
    n_samples=400,
    bandwidth_hz=spec.bandwidth_hz,
    pulse_width_s=spec.pulse_width_s,
    fs_hz=spec.fs_hz,
)
output = matched_filter(received_signal, chirp)
```

This pattern is intentionally simple. It keeps the radar math explicit, but removes the burden of rewriting the same helper logic in every notebook.

## How to think about these helpers

A learner should be able to connect each helper call back to a visible equation in the chapter.

If a helper hides too much detail, it becomes hard to teach. If it is too low-level, it becomes noisy. The beginner package sits in the middle:

- it keeps the repeated code compact,
- it names the concept clearly,
- and it keeps the physics visible enough to learn from.

## Recommended usage

- Use the helper package when you want consistency across notebook cells.
- Read the helper function docstrings when you need the exact formula.
- Keep the notebook itself as the place where the engineering story is explained.
- Treat the helper modules as teaching tools, not as a production radar library.

This is the scope we want for now: practical, chapter-aware, and useful to notebook users without pretending it is a formal public API.
