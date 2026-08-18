"""Tracking: Kalman filter predict/update, track state.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 5.
"""


class State:
    """Kalman-filtered state: range and velocity."""

    def __init__(self, range_m, velocity_mps):
        self.range_m = range_m
        self.velocity_mps = velocity_mps


class KalmanTracker:
    """Constant-velocity Kalman filter for range/velocity tracking."""

    def __init__(self, dt_s, q, r):
        raise NotImplementedError("roadmap stage 5")

    def predict(self):
        raise NotImplementedError("roadmap stage 5")

    def update(self, measurement):
        raise NotImplementedError("roadmap stage 5")

    @property
    def track(self):
        raise NotImplementedError("roadmap stage 5")
