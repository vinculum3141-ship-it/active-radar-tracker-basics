from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BaselineRadarSpec:
    fc_hz: float = 2.45e9
    bandwidth_hz: float = 5e6
    pulse_width_s: float = 20e-6
    pri_s: float = 1e-3
    fs_hz: float = 20e6
    n_pulses: int = 64
    target_range_m: float = 1000.0
    target_velocity_mps: float = 40.0
    snr_db: float = 20.0
    target_angle_deg: float = 20.0
    interferer_angle_deg: float = -30.0


RADAR_CONSTANTS = BaselineRadarSpec()


def baseline_spec() -> BaselineRadarSpec:
    """Return the default beginner baseline radar specification."""

    return RADAR_CONSTANTS
