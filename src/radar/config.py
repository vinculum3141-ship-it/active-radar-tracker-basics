"""Configuration: dataclasses + YAML/TOML loaders for radar parameters.

API spec: docs/training/04-python-discipline.md §3.
Reproducibility: load_config/config_summary wired in (see §5).
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
    out_dir: str = "out"  # plots land in <out_dir>/<stage>/ (§5)


def load_config(path: str | None = None) -> RadarConfig:
    """Load config from a YAML file if a path is given, else defaults.

    Unknown keys are ignored so experiment files can carry extra metadata.
    """
    if path is None:
        return RadarConfig()
    import yaml

    with open(path) as f:
        overrides = yaml.safe_load(f) or {}
    valid = {
        k: v for k, v in overrides.items() if k in RadarConfig.__dataclass_fields__
    }
    return RadarConfig(**valid)


def config_summary(cfg: RadarConfig) -> str:
    """Stable, diffable one-line summary of the active config.

    Printed by the CLI on every run (§5). The dataclass repr is already
    deterministic, so diffing two runs is a text diff.
    """
    return str(cfg)
