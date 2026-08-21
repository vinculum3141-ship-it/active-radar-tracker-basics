"""Tracking: Kalman filter predict/update, track state.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 5.
"""

from dataclasses import dataclass

import numpy as np

from radar.receiver import Detection


@dataclass
class State:
    """Kalman-filtered state: range and velocity."""

    range_m: float
    velocity_mps: float


class KalmanTracker:
    """Constant-velocity Kalman filter for 1-D radial range/velocity tracking.

    State ``x = [range, velocity]``; constant-velocity motion model
    ``F = [[1, dt], [0, 1]]`` (01-physics.md §5). Per CPI call ``predict`` to
    advance the state by ``dt``, then ``update`` to fuse one ``Detection``
    (range and/or velocity). The filtered estimates accumulate in ``track``.
    """

    def __init__(self, dt_s: float, q: float, r: float) -> None:
        self.dt = float(dt_s)
        self.q = float(q)
        self.r = float(r)
        self.F = np.array([[1.0, self.dt], [0.0, 1.0]])
        # Q/R are diagonal; scalar q, r are the per-channel variances.
        self.Q = np.eye(2) * self.q
        self.R = np.eye(2) * self.r
        self.x = np.zeros(2)
        self.P = np.eye(2)
        self._track: list[State] = []

    def predict(self) -> State:
        """Advance the state by ``dt`` (motion model); return the prediction."""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return State(self.x[0], self.x[1])

    def update(self, measurement: Detection) -> State:
        """Fuse one ``Detection`` (range and/or velocity); return the estimate.

        Builds the measurement vector/matrix from whichever fields are present,
        so a range-only or velocity-only detection is accepted (01-physics.md
        §5 measurement model). Appends the corrected state to ``track``.
        """
        # Seed the state from the first measurement so there is no large
        # initial jump (the filter then converges from there).
        if not self._track:
            self.x = np.array([measurement.range_m or 0.0, measurement.velocity or 0.0])

        z_rows: list[float] = []
        H_rows: list[list[float]] = []
        if measurement.range_m is not None:
            z_rows.append(float(measurement.range_m))
            H_rows.append([1.0, 0.0])
        if measurement.velocity is not None:
            z_rows.append(float(measurement.velocity))
            H_rows.append([0.0, 1.0])

        z = np.array(z_rows)
        H = np.array(H_rows)
        R = np.eye(len(z_rows)) * self.r

        # Kalman gain + update (01-physics.md §5).
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ (z - H @ self.x)
        self.P = (np.eye(2) - K @ H) @ self.P

        state = State(self.x[0], self.x[1])
        self._track.append(state)
        return state

    @property
    def track(self) -> list[State]:
        """Chronological list of post-update states (one per measurement)."""
        return self._track
