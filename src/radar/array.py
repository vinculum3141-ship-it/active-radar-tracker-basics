"""Array: uniform linear array, steering vectors, beam pattern.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 6.
"""


def steering_vector(theta_deg, n_elements, spacing_lambda):
    """Return the ULA steering vector for angle theta_deg."""
    raise NotImplementedError("roadmap stage 6")


def array_response(x, theta_deg, cfg):
    """Return the array response (weighted sum) toward theta_deg."""
    raise NotImplementedError("roadmap stage 6")


def beam_pattern(weights, thetas_deg, cfg):
    """Return |w^H a(theta)|^2 over thetas_deg."""
    raise NotImplementedError("roadmap stage 6")
