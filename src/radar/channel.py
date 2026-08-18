"""Channel model: propagation delay, attenuation, noise, targets.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 2.
"""


class Target:
    """A moving target with range, velocity, and optional angle/SNR."""

    def __init__(self, range_m, velocity_mps, angle_deg=None, snr_db=20.0):
        self.range_m = range_m
        self.velocity_mps = velocity_mps
        self.angle_deg = angle_deg
        self.snr_db = snr_db


def propagate(pulse, target, cfg, rng):
    """Return the received echo for one pulse from one target."""
    raise NotImplementedError("roadmap stage 2")


def simulate_channel(tx, targets, cfg, rng):
    """Return received signal for a list of targets."""
    raise NotImplementedError("roadmap stage 2")
