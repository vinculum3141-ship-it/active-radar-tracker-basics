# Helper scripts for beginner notebooks

This section documents the shared Python helper scripts used across the beginner
radar notebooks. The goal is to make the support code easy to recognise and easy
to connect back to the lesson material.

## Purpose

The helper scripts exist to do two things:

- keep repeated calculations consistent across notebooks,
- preserve the physical meaning of each formula as the learner progresses.

This means functions are deliberately narrow and named in a way that matches the
radar story: wavelength, delay, chirp, matched filter, Doppler, covariance, and
steering.

## Main helper modules

- `constants`: baseline radar specification
- `math`: range, wavelength, delay, and resolution helpers
- `waveforms`: pulses, chirps, and matched filtering
- `channel`: delayed echoes, attenuation, and AWGN noise
- `doppler`: range-Doppler processing and velocity conversion
- `array`: array spacing and steering geometry
- `doa`: Bartlett and Capon spatial spectra
- `steering`: beam-pointing and LCMV nulling weights
- `kalman`: constant-velocity state prediction and update
- `plotting`: shared notebook plotting style

## Typical usage

```python
from beginner.helpers import baseline_spec, matched_filter, lfm_chirp

spec = baseline_spec()
chirp = lfm_chirp(
    n_samples=400,
    bandwidth_hz=spec.bandwidth_hz,
    pulse_width_s=spec.pulse_width_s,
    fs_hz=spec.fs_hz,
)
output = matched_filter(received_signal, chirp)
```

## Teaching principle

The helper functions should make the course easier to teach, not hide the
physics. A learner should be able to connect a helper call back to a visible
equation in the chapter and understand what the code is doing before they use it
automatically.
