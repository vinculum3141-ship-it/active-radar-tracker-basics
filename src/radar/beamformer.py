"""Beamforming: Bartlett/Capon scan, LCMV null-steering weights.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stages 7+.
"""


def bartlett_scan(array_data, thetas_deg, cfg):
    """Return Bartlett beamscan power vs angle."""
    raise NotImplementedError("roadmap stage 7")


def capon_weights(array_data, theta_deg, cfg):
    """Return Capon (MVDR) weights for look direction theta_deg."""
    raise NotImplementedError("roadmap stage 7")


def lcmv_weights(array_data, target_deg, interferer_deg, cfg):
    """Return LCMV weights: unit gain at target, null at interferer."""
    raise NotImplementedError("roadmap stage 10")


def apply_weights(array_data, weights):
    """Apply beamformer weights to array data."""
    raise NotImplementedError("roadmap stage 9")
