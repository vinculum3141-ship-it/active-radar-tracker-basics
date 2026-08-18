#!/usr/bin/env python3
"""Regenerate the array constants used by grc/radar_array.grc.

Reproduces the arrival phases, steering weights and (optionally) the LCMV
nulling weights described in docs/training/02-radar-basics.md and
03-hardware.md 2.4. Run with:

    uv run grc/gen_weights.py

The printed values are the ones baked into radar_array.grc so the learner
can check the beamformer math (src/radar/beamformer.py) against them.
"""

import numpy as np


def steering_vector(theta_deg, n_elements=4, d_over_lambda=0.5):
    """a(theta): plane-wave arrival phases at a ULA, complex128 vector."""
    theta = np.deg2rad(theta_deg)
    m = np.arange(n_elements)
    phi = 2 * np.pi * d_over_lambda * m * np.sin(theta)
    return np.exp(1j * phi)


def cbf_weights(theta_deg, n_elements=4, d_over_lambda=0.5):
    """Conventional beamformer weights: conj(a(theta)) (phase-align + sum)."""
    return np.conj(steering_vector(theta_deg, n_elements, d_over_lambda))


def lcmv_weights(theta_target_deg, theta_null_deg, n_elements=4, d_over_lambda=0.5):
    """Linearly constrained minimum variance weights.

    w = R_inv C (C^H R_inv C)^-1 g  with R = I (white noise), C the
    constraint matrix [a(theta_t), a(theta_i)] and g = [1, 0]^T.
    """
    C = np.column_stack(
        [
            steering_vector(theta_target_deg, n_elements, d_over_lambda),
            steering_vector(theta_null_deg, n_elements, d_over_lambda),
        ]
    )
    R_inv = np.eye(n_elements)
    g = np.array([1.0, 0.0])
    return R_inv @ C @ np.linalg.inv(C.conj().T @ R_inv @ C) @ g


def main():
    theta_t, theta_i = 20.0, -30.0
    m = np.arange(4)
    a_t = steering_vector(theta_t)
    a_i = steering_vector(theta_i)
    w_cbf = cbf_weights(theta_t)

    print("== Steering vector / arrival phases (theta_t = 20 deg, d = lambda/2) ==")
    for k in range(4):
        print(f"  a[{k}]   = {a_t[k]: .8f}")
    print(f"  phases  = {[round(x, 8) for x in np.angle(a_t)]}")

    print("\n== CBF weights (conj(a_t)) - used in radar_array.grc ==")
    for k in range(4):
        print(f"  w[{k}]   = {w_cbf[k]: .8f}")
    gain = np.sum(w_cbf * a_t)
    print(f"  sum(w*a_t) = {gain:.4f}  (coherent gain = {len(m)})")

    print("\n== LCMV nulling weights (target 20 deg, null -30 deg) ==")
    w_lcmv = lcmv_weights(theta_t, theta_i)
    for k in range(4):
        print(f"  w[{k}]   = {w_lcmv[k]: .8f}")
    print(f"  w^H a_t = {np.vdot(w_lcmv, a_t): .4f}")
    print(f"  w^H a_i = {np.vdot(w_lcmv, a_i): .6e}  (null)")


if __name__ == "__main__":
    main()
