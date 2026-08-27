from __future__ import annotations

import numpy as np


def state_transition_matrix(dt: float) -> np.ndarray:
    """Return the constant-velocity state transition matrix for a timestep ``dt``.

    The state is ``[range, velocity]``. In one timestep the range advances by
    ``velocity * dt`` while the velocity is unchanged::

        x[k+1] = [[1, dt], [0, 1]] @ x[k]
    """

    return np.array([[1.0, dt], [0.0, 1.0]])


def predict(x: np.ndarray, P: np.ndarray, F: np.ndarray, Q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Advance the state estimate and its covariance with the model only.

    No measurement is used here; this is the radar's guess based purely on how
    it believes the target moves. ``x`` is the state, ``P`` its covariance,
    ``F`` the transition matrix, and ``Q`` the process noise.
    """

    x_pred = F @ x
    P_pred = F @ P @ F.T + Q
    return x_pred, P_pred


def update(
    x_pred: np.ndarray,
    P_pred: np.ndarray,
    z: np.ndarray,
    H: np.ndarray,
    R: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Fuse a new measurement ``z`` into the prediction.

    ``H`` maps state to measurement space (here the identity, since we measure
    both range and velocity) and ``R`` is the measurement noise covariance.
    The Kalman gain ``K`` decides how much of the innovation ``z - H x_pred``
    to accept; the output is the blended state and its covariance.
    """

    S = H @ P_pred @ H.T + R
    K = P_pred @ H.T @ np.linalg.inv(S)
    y = z - H @ x_pred
    x = x_pred + K @ y
    P = (np.eye(len(x)) - K @ H) @ P_pred
    return x, P


def run_kalman_track(
    measurements: np.ndarray,
    F: np.ndarray,
    Q: np.ndarray,
    H: np.ndarray,
    R: np.ndarray,
    x0: np.ndarray,
    P0: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Run predict + update over a sequence of measurements.

    ``measurements`` is shape ``(n_steps, 2)`` with one range/velocity row per
    timestep. Returns the predicted states (before each update), the filtered
    states (after each update), the covariances after each update, and the
    Kalman gains (averaged over the two state components).
    """

    n = len(measurements)
    predicted = np.zeros_like(measurements)
    filtered = np.zeros_like(measurements)
    covariances = np.zeros((n, 2, 2))
    gains = np.zeros((n, 2))

    x, P = x0, P0
    for k in range(n):
        x_pred, P_pred = predict(x, P, F, Q)
        predicted[k] = x_pred
        x, P = update(x_pred, P_pred, measurements[k], H, R)
        filtered[k] = x
        covariances[k] = P

        S = H @ P_pred @ H.T + R
        gains[k] = (P_pred @ H.T @ np.linalg.inv(S)).diagonal()

    return predicted, filtered, covariances, gains
