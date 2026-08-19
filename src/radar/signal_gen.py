"""Transmit waveform generation: rectangular pulse, LFM chirp, pulse train.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 1.
"""

import numpy as np

from radar.config import RadarConfig


def _n_pulse_samples(cfg: RadarConfig) -> int:
    """Number of fast-time samples inside one pulse width (tau * fs)."""
    return round(cfg.pulse_width_s * cfg.fs_hz)


def _samples_per_pulse(cfg: RadarConfig) -> int:
    """Number of fast-time samples in one PRI (T * fs)."""
    return round(cfg.pri_s * cfg.fs_hz)


def rectangular_pulse(cfg: RadarConfig) -> np.ndarray:
    """Return one rectangular pulse as complex fast-time samples.

    A unit-amplitude complex envelope of length ``tau * fs`` samples
    (400 for the baseline config), modelling the baseband pulse with no
    carrier (02-architecture.md §5: complex baseband throughout).

    Parameters
    ----------
    cfg : RadarConfig
        Radar configuration (pulse width, sampling rate).

    Returns
    -------
    np.ndarray
        Complex baseband pulse, length ``round(pulse_width_s * fs_hz)``.
    """
    return np.ones(_n_pulse_samples(cfg), dtype=complex)


def lfm_chirp(cfg: RadarConfig) -> np.ndarray:
    """Return one complex analytic LFM chirp (fast-time samples).

    Sweeps instantaneous frequency from 0 to ``bandwidth_hz`` across the
    pulse using ``s(t) = exp(j*pi*k*t^2)`` with chirp rate ``k = B/tau``
    (01-physics.md §3). The sweep spans the full bandwidth B, which is the
    time-bandwidth product that pulse compression exploits (stage 3).

    Parameters
    ----------
    cfg : RadarConfig
        Radar configuration (bandwidth, pulse width, sampling rate).

    Returns
    -------
    np.ndarray
        Complex analytic chirp, length ``round(pulse_width_s * fs_hz)``.
    """
    n = _n_pulse_samples(cfg)
    t = np.arange(n) / cfg.fs_hz
    k = cfg.bandwidth_hz / cfg.pulse_width_s
    return np.exp(1j * np.pi * k * t**2)


def pulse_train(cfg: RadarConfig) -> np.ndarray:
    """Return the pulse train as [n_pulses, samples_per_pulse].

    Each row covers one PRI of fast-time samples; the transmit pulse sits
    in the first ``tau * fs`` samples of the row and the remainder is
    silence (the receive/quiet window of the monostatic pulse radar).

    Parameters
    ----------
    cfg : RadarConfig
        Radar configuration.

    Returns
    -------
    np.ndarray
        Complex pulse train, shape ``(n_pulses, pri_s * fs_hz)``.
    """
    pulse = rectangular_pulse(cfg) if cfg.pulse_type == "rect" else lfm_chirp(cfg)
    train = np.zeros((cfg.n_pulses, _samples_per_pulse(cfg)), dtype=complex)
    train[:, : pulse.size] = pulse
    return train


def transmit_waveform(cfg: RadarConfig) -> np.ndarray:
    """Return the full transmit waveform for one CPI.

    Selects rectangular vs LFM pulse via ``cfg.pulse_type``; returns the
    pulse train that feeds the channel (the ``tx`` in data contracts).

    Parameters
    ----------
    cfg : RadarConfig
        Radar configuration.

    Returns
    -------
    np.ndarray
        Complex pulse train, shape ``(n_pulses, samples_per_pulse)``.
    """
    return pulse_train(cfg)