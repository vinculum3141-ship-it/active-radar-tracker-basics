"""Array geometry and steering helpers for the beginner radar notebooks.

This module keeps the array math explicit: each element contributes a phase
shift tied to the extra path length from the incoming plane wave. That makes it
straightforward to teach steering vectors, beam pointing, and the relationship
between array spacing and null locations.
"""

from __future__ import annotations

import numpy as np


def inter_element_phase_rad(
    angle_rad: float, spacing_m: float, wavelength_m: float
) -> float:
    """Return the phase offset between adjacent array elements.

    For a plane wave arriving from ``angle_rad`` measured from broadside, the
    extra path to each successive element is ``d * sin(angle)``, giving a phase
    step ``k * d * sin(angle) = 2 pi d sin(angle) / wavelength``.
    """

    return 2.0 * np.pi * spacing_m * np.sin(angle_rad) / wavelength_m


def steering_vector(
    angle_rad: float, n_elements: int, spacing_m: float, wavelength_m: float
) -> np.ndarray:
    """Return the steering vector for a plane wave from ``angle_rad``.

    Element n carries the cumulative phase ``n * k * d * sin(angle)``, so the
    vector is ``[1, e^{j psi}, e^{j 2 psi}, ..., e^{j (N-1) psi}]`` with ``psi``
    the inter-element phase step.
    """

    psi = inter_element_phase_rad(angle_rad, spacing_m, wavelength_m)
    n = np.arange(n_elements)
    return np.exp(1j * n * psi)


def array_factor(
    angles_rad: np.ndarray,
    n_elements: int,
    spacing_m: float,
    wavelength_m: float,
    weights: np.ndarray | None = None,
) -> np.ndarray:
    """Return the (complex) array factor at each angle.

    The array factor sums the element contributions with their weights. With
    uniform weights this is the classical sinc-like pattern whose main lobe is
    at broadside and whose sidelobes scale with the number of elements.
    """

    if weights is None:
        weights = np.ones(n_elements)
    k = 2.0 * np.pi / wavelength_m
    psi = k * spacing_m * np.sin(angles_rad)  # shape (n_angles,)
    n = np.arange(n_elements)                 # shape (n_elements,)
    return weights @ np.exp(1j * np.outer(n, psi))


def first_null_angle_deg(n_elements: int, spacing_m: float, wavelength_m: float) -> float:
    """Return the first null of the uniform array, in degrees.

    The first null falls where ``N * psi / 2 = pi``, i.e. the main lobe spans
    ``+-arcsin(lambda / (N d))`` from broadside.
    """

    return float(np.degrees(np.arcsin(wavelength_m / (n_elements * spacing_m))))
