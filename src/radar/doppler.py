"""Doppler: slow-time FFT, range-Doppler map, range/velocity axes.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 4.
"""


def range_doppler_map(matched, cfg):
    """Return the range-Doppler map from matched-filter outputs."""
    raise NotImplementedError("roadmap stage 4")


def range_axis(cfg):
    """Return the range axis in meters."""
    raise NotImplementedError("roadmap stage 4")


def velocity_axis(cfg):
    """Return the velocity axis in m/s."""
    raise NotImplementedError("roadmap stage 4")
