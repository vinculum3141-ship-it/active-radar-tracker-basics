from __future__ import annotations

import numpy as np

from .math import wavelength_m


def doppler_frequency_hz(velocity_mps: float, fc_hz: float) -> float:
    """Return the Doppler frequency shift of a radial velocity, in Hz.

    For a monostatic radar the two-way Doppler shift is 2*v/lambda.
    """

    return 2.0 * velocity_mps / wavelength_m(fc_hz)


def velocity_from_doppler(fd_hz: float, fc_hz: float) -> float:
    """Return the radial velocity (m/s) implied by a Doppler frequency shift."""

    return fd_hz * wavelength_m(fc_hz) / 2.0


def build_pulse_stack(
    template: np.ndarray,
    n_pulses: int,
    pri_s: float,
    doppler_hz: float,
    delay_samples: int,
    amplitude: float = 1.0,
) -> np.ndarray:
    """Return a slow-time stack of ``n_pulses`` echoes with a constant Doppler shift.

    Each row is one PRI of fast time. The echo is placed at ``delay_samples``
    and its phase advances by ``2*pi*doppler_hz*pri_s`` from one pulse to the
    next, which is how a moving target shows up across slow time.
    """

    fast_len = delay_samples + len(template)
    stack = np.zeros((n_pulses, fast_len), dtype=complex)
    for k in range(n_pulses):
        phase = np.exp(1j * 2.0 * np.pi * doppler_hz * k * pri_s)
        stack[k, delay_samples : delay_samples + len(template)] = amplitude * template * phase
    return stack


def range_doppler_map(
    range_profiles: np.ndarray,
    pri_s: float,
    fc_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (doppler_hz_axis, velocity_mps_axis, magnitude_map).

    ``range_profiles`` has shape (n_pulses, n_fast_samples), i.e. one matched
    filter output per pulse stacked along slow time. An FFT along axis 0 gives
    the Doppler spectrum at every range bin. The velocity axis remaps the
    Doppler axis using the carrier wavelength.
    """

    n_pulses = range_profiles.shape[0]
    fft_map = np.fft.fftshift(np.fft.fft(range_profiles, axis=0), axes=0)
    doppler_hz_axis = np.fft.fftshift(np.fft.fftfreq(n_pulses, pri_s))

    lam = wavelength_m(fc_hz)
    velocity_mps_axis = doppler_hz_axis * lam / 2.0
    return doppler_hz_axis, velocity_mps_axis, np.abs(fft_map)
