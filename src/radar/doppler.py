"""Doppler: slow-time FFT, range-Doppler map, range/velocity axes.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 4.
"""

import numpy as np

from radar.channel import C_MPS
from radar.config import RadarConfig


def range_doppler_map(matched: np.ndarray, cfg: RadarConfig) -> np.ndarray:
    """Return the range-Doppler map from matched-filter outputs.

    ``matched`` is ``[n_pulses, samples_per_pulse]`` (the stacked
    matched-filter output, one row per PRI). FFT is taken along the slow-time
    (pulse) axis and ``fftshift``-ed so zero Doppler sits at the center of the
    returned axis — i.e. the map is indexed ``[doppler_bin, range_bin]`` and
    lines up with ``velocity_axis`` / ``range_axis``.

    Parameters
    ----------
    matched : np.ndarray
        Matched-filter output ``[n_pulses, samples_per_pulse]`` (complex).
    cfg : RadarConfig
        Radar configuration.

    Returns
    -------
    np.ndarray
        Range-Doppler map ``[n_pulses, samples_per_pulse]`` (complex).
    """
    return np.fft.fftshift(np.fft.fft(matched, axis=0), axes=0)


def range_axis(cfg: RadarConfig) -> np.ndarray:
    """Return the range axis in meters.

    Mirrors the range-profile convention (receiver.py / viz.py): sample index
    minus the matched-filter correlation offset ``len(pulse)//2``, converted via
    ``R = c*t/2``. The baseline 1000 m target therefore falls at ~1000 m.
    """
    n_pulse = round(cfg.pulse_width_s * cfg.fs_hz)
    n_samples = round(cfg.pri_s * cfg.fs_hz)
    return (np.arange(n_samples) - n_pulse // 2) * C_MPS / (2.0 * cfg.fs_hz)


def velocity_axis(cfg: RadarConfig) -> np.ndarray:
    """Return the velocity axis in m/s.

    After ``fftshift`` the central Doppler bin is zero velocity; bin ``k`` is
    offset by ``(k - N/2)`` cells of width ``Delta_v = lambda/(2*N*T)``
    (01-physics.md §4).
    """
    n_pulses = cfg.n_pulses
    wavelength = C_MPS / cfg.fc_hz
    delta_v = wavelength / (2.0 * n_pulses * cfg.pri_s)
    return (np.arange(n_pulses) - n_pulses // 2) * delta_v
