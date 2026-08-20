"""Receiver: matched filter, peak detection, range estimation.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 3.
"""

from dataclasses import dataclass

import numpy as np
from scipy.signal import correlate, find_peaks

from radar.channel import C_MPS
from radar.config import RadarConfig


@dataclass
class Detection:
    """A detected target: range, velocity, SNR, angle."""

    range_m: float
    velocity: float | None = None
    snr_db: float | None = None
    angle_deg: float | None = None


def _pulse_samples(cfg: RadarConfig) -> int:
    """Number of fast-time samples in the transmit pulse (tau * fs)."""
    return round(cfg.pulse_width_s * cfg.fs_hz)


def _pulse_offset(cfg: RadarConfig) -> int:
    """Index shift of the 'same'-mode correlation peak from the true delay.

    scipy.signal.correlate(a, b, mode="same") aligns the output to the center
    of ``a``, so the cross-correlation peak for an echo at delay ``d`` appears
    at index ``d + len(b)//2``. Subtracting this recovers the delay.
    """
    return _pulse_samples(cfg) // 2


def matched_filter(rx: np.ndarray, tx_pulse: np.ndarray) -> np.ndarray:
    """Matched-filter the received signal with the transmit pulse.

    For a known signal in white noise the matched filter is the
    cross-correlation with the transmit pulse; scipy.signal.correlate already
    conjugates its kernel, so ``tx_pulse`` is passed through directly (see the
    stage-1 doc's correlate-conjugation gotcha). ``mode="same"`` keeps the
    output length equal to the input, so the time axis is preserved.

    The peak for an echo at delay ``d`` lands at ``d + len(tx_pulse)//2``.
    """
    if rx.ndim == 1:
        return correlate(rx, tx_pulse, mode="same")
    return np.array([correlate(row, tx_pulse, mode="same") for row in rx])


def range_from_delay(delay_samples: int, cfg: RadarConfig) -> float:
    """Convert a delay in samples to range in meters (R = c*dt/2)."""
    return delay_samples * C_MPS / (2 * cfg.fs_hz)


def detect_peaks(
    matched: np.ndarray, cfg: RadarConfig, threshold_db: float = 10.0
) -> list[Detection]:
    """Return a list of Detections from matched-filter peaks.

    Uses the first pulse row if ``matched`` is 2D. The noise floor is the
    median matched-filter power, corrected to a mean (median is robust to the
    narrow compressed-signal region; for unit-variance complex noise the
    median of |y|^2 is 2*ln(2)/2 = ln(2) of the mean). A peak is kept when its
    power exceeds the floor by ``threshold_db`` and it is the strongest local
    maximum within one pulse length (chirp autocorrelation sidelobes are
    ~13 dB below the mainlobe and sit inside this window, so this keeps one
    detection per resolved target). Range is the peak index minus the
    correlation offset, converted via ``range_from_delay``; SNR is the
    peak-to-floor power ratio.
    """
    if matched.ndim == 2:
        matched = matched[0]
    mag = np.abs(matched)
    noise_power = float(np.median(mag**2) / np.log(2.0))
    threshold_power = noise_power * 10 ** (threshold_db / 10.0)

    peak_indices, _ = find_peaks(
        mag, height=np.sqrt(threshold_power), distance=_pulse_samples(cfg)
    )

    detections = []
    offset = _pulse_offset(cfg)
    for i in peak_indices:
        delay = i - offset
        if delay < 0:
            continue
        snr_db = 10 * np.log10(float(mag[i] ** 2) / noise_power)
        detections.append(
            Detection(range_m=range_from_delay(delay, cfg), snr_db=snr_db)
        )
    return detections
