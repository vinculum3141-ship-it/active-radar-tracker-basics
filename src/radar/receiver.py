"""Receiver: matched filter, peak detection, range estimation.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 3.
"""


class Detection:
    """A detected target: range, velocity, SNR, angle."""

    def __init__(self, range_m, velocity=None, snr_db=None, angle_deg=None):
        self.range_m = range_m
        self.velocity = velocity
        self.snr_db = snr_db
        self.angle_deg = angle_deg


def matched_filter(rx, tx_pulse):
    """Return the matched-filtered signal (correlation with transmit pulse)."""
    raise NotImplementedError("roadmap stage 3")


def range_from_delay(delay_samples, cfg):
    """Convert a delay in samples to range in meters."""
    raise NotImplementedError("roadmap stage 3")


def detect_peaks(matched, cfg, threshold_db=10.0):
    """Return a list of Detections from matched-filter peaks."""
    raise NotImplementedError("roadmap stage 3")
