from __future__ import annotations

import numpy as np

from .array import steering_vector


def steering_weights(
    look_angle_rad: float,
    n_elements: int,
    spacing_m: float,
    wavelength_m: float,
) -> np.ndarray:
    """Return the weight vector that steers the main lobe to ``look_angle_rad``.

    The weights are the steering vector of the look direction scaled to unit
    response, so that ``w^H a(look_angle) = 1``. Combining the elements with
    these weights phases them to line up a wave from the look angle, which is
    exactly how a beam is pointed. The response at any angle is
    ``w.conj() @ a(theta)``.
    """

    a = steering_vector(look_angle_rad, n_elements, spacing_m, wavelength_m)
    return a / n_elements


def lcmv_weights(
    look_angle_rad: float,
    null_angles_rad: list[float],
    n_elements: int,
    spacing_m: float,
    wavelength_m: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (constraint_matrix, desired_response, weights) for LCMV nulling.

    The constraints force a unit response at the look angle and a zero response
    at each null angle. Solving C^H w = f in the least-squares sense with the
    minimal-norm weight vector gives

        w = C (C^H C)^{-1} f

    which keeps the target at full gain while driving a deep null on the
    interferer. ``null_angles_rad`` is a list so you can null several sources at
    once (e.g. [steering, ...]).
    """

    cols = [steering_vector(look_angle_rad, n_elements, spacing_m, wavelength_m)]
    cols += [steering_vector(a, n_elements, spacing_m, wavelength_m) for a in null_angles_rad]
    C = np.column_stack(cols)
    f = np.zeros(C.shape[1], dtype=complex)
    f[0] = 1.0  # unit gain on the look (target) direction
    w = C @ np.linalg.pinv(C.conj().T @ C) @ f
    # Normalise so the response at the look angle is exactly 1.0.
    r = (cols[0].conj() @ w).real
    if abs(r) > 1e-12:
        w = w / r
    return C, f, w
