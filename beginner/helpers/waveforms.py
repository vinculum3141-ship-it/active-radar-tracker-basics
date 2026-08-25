from __future__ import annotations

import numpy as np


def rectangular_pulse(n_samples: int) -> np.ndarray:
    """Return a unit-amplitude rectangular pulse of ``n_samples`` points."""

    return np.ones(n_samples, dtype=float)


def lfm_chirp(
    n_samples: int,
    bandwidth_hz: float,
    pulse_width_s: float,
    fs_hz: float,
) -> np.ndarray:
    """Return a baseband LFM (linear-frequency-modulation) up-chirp.

    The instantaneous frequency sweeps linearly from ``0`` to ``bandwidth_hz``
    across the pulse. The matched filter of this chirp compresses to a narrow
    peak whose width is set by the bandwidth, not the pulse length.
    """

    t = np.arange(n_samples) / fs_hz
    chirp_rate_hz_per_s = bandwidth_hz / pulse_width_s
    phase = np.pi * chirp_rate_hz_per_s * t**2
    return np.exp(1j * phase)


def instantaneous_frequency_hz(
    chirp: np.ndarray,
    fs_hz: float,
) -> np.ndarray:
    """Estimate the instantaneous frequency of a baseband complex chirp in Hz.

    Uses the unwrapped phase derivative, which is the most direct way to show
    the linear sweep to a learner who has just seen the waveform.
    """

    phase = np.unwrap(np.angle(chirp))
    return np.diff(phase) / (2.0 * np.pi) * fs_hz


def matched_filter(received: np.ndarray, template: np.ndarray) -> np.ndarray:
    """Return the matched-filter output of ``received`` against ``template``.

    The template is conjugated and time-reversed (the optimal filter for a
    known waveform in white noise), then correlated with the received signal.
    """

    return np.correlate(received, np.conj(template)[::-1], mode="full")
