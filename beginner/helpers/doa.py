"""Direction-of-arrival and adaptive beamforming helpers.

These functions intentionally mirror the classroom progression from a simple
Bartlett spectrum to the adaptive MVDR spectrum. The point is to show learners
that spatial filtering is not magic: it is a covariance-based weighting problem
built from steering vectors and measured array data.
"""

from __future__ import annotations

import numpy as np

from .array import steering_vector


def sample_covariance(
    source_angles_rad: list[float],
    source_amps: list[float],
    n_elements: int,
    spacing_m: float,
    wavelength_m: float,
    n_snapshots: int = 256,
    noise_power: float = 1.0,
    seed: int | None = 42,
) -> np.ndarray:
    """Estimate the array covariance from snapshots.

    Each snapshot is the sum of scaled steering vectors (one per source) plus
    additive white noise. Averaging ``x x^H`` over many snapshots gives the
    sample covariance ``R`` that both beamformers consume.
    """

    rng = np.random.default_rng(seed)
    n = n_elements
    Rsum = np.zeros((n, n), dtype=complex)
    for _ in range(n_snapshots):
        x = np.zeros(n, dtype=complex)
        for ang, amp in zip(source_angles_rad, source_amps):
            # Independent sources carry their own random phase each snapshot.
            phase = np.exp(1j * rng.uniform(0.0, 2.0 * np.pi))
            x = x + amp * phase * steering_vector(ang, n_elements, spacing_m, wavelength_m)
        noise = np.sqrt(noise_power / 2.0) * (
            rng.standard_normal(n) + 1j * rng.standard_normal(n)
        )
        Rsum = Rsum + np.outer(x + noise, np.conj(x + noise))
    return Rsum / n_snapshots


def bartlett_spectrum(
    R: np.ndarray,
    angles_rad: np.ndarray,
    n_elements: int,
    spacing_m: float,
    wavelength_m: float,
) -> np.ndarray:
    """Return the Bartlett (delay-and-sum) spatial spectrum.

    The power at each angle is ``a^H R a`` with the steering vector used as the
    weight, normalised so its peak is near the printed source power. Bartlett
    cannot beat the array's intrinsic beamwidth, so close targets blur together.
    """

    power = np.zeros(len(angles_rad))
    for i, th in enumerate(angles_rad):
        a = steering_vector(th, n_elements, spacing_m, wavelength_m).reshape(-1, 1)
        power[i] = np.real(a.conj().T @ R @ a).item()
    return power


def mvdr_spectrum(
    R: np.ndarray,
    angles_rad: np.ndarray,
    n_elements: int,
    spacing_m: float,
    wavelength_m: float,
    reg: float = 1e-6,
) -> np.ndarray:
    """Return the Capon / MVDR spatial spectrum.

    Capon adapts the weight to pass a chosen direction while nulling everything
    else, giving much sharper peaks than Bartlett. ``reg`` keeps the matrix
    inversion stable when the sample covariance is noisy.
    """

    n = n_elements
    Rinv = np.linalg.pinv(R + reg * np.eye(n))
    power = np.zeros(len(angles_rad))
    for i, th in enumerate(angles_rad):
        a = steering_vector(th, n_elements, spacing_m, wavelength_m).reshape(-1, 1)
        denom = np.real(a.conj().T @ Rinv @ a).item()
        power[i] = 1.0 / denom
    return power
