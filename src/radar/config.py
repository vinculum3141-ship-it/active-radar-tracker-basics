"""Configuration: dataclasses + YAML/TOML loaders for radar parameters.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 1.
"""

from dataclasses import dataclass


@dataclass
class RadarConfig:
    """Baseline radar parameters (see 01-physics.md parameter rationale)."""

    fc_hz: float = 2.45e9
    bandwidth_hz: float = 5e6
    pulse_width_s: float = 20e-6
    pri_s: float = 1e-3
    fs_hz: float = 20e6
    n_pulses: int = 64
    pulse_type: str = "lfm"  # "rect" | "lfm"
    target_range_m: float = 1000.0
    target_velocity_mps: float = 40.0
    snr_db: float = 20.0
    seed: int = 42
    n_elements: int = 4  # stages 6+
    array_spacing_lambda: float = 0.5
    target_angle_deg: float = 20.0
    interferer_angle_deg: float = -30.0  # stages 8+


def load_config(path: str | None = None) -> RadarConfig:
    """Load config from YAML/TOML if a path is given, else defaults."""
    raise NotImplementedError("roadmap stage 1")
