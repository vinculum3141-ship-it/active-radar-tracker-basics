from __future__ import annotations

from .constants import RADAR_CONSTANTS, BaselineRadarSpec

C_MPS = 299_792_458.0


def wavelength_m(fc_hz: float) -> float:
    """Return wavelength in meters for a carrier frequency in hertz."""

    return C_MPS / fc_hz


def duty_cycle(pulse_width_s: float, pri_s: float) -> float:
    """Return radar duty cycle as a fraction."""

    return pulse_width_s / pri_s


def delay_samples_for_range(range_m: float, fs_hz: float, c_mps: float = C_MPS) -> int:
    """Convert a monostatic round-trip range into a sample delay."""

    return int(round((2.0 * range_m / c_mps) * fs_hz))


def range_from_delay_samples(delay_samples: int, fs_hz: float, c_mps: float = C_MPS) -> float:
    """Convert a sample delay into a monostatic range estimate."""

    return (delay_samples / fs_hz) * c_mps / 2.0


def baseline_spec() -> BaselineRadarSpec:
    """Return the default beginner baseline radar specification."""

    return RADAR_CONSTANTS
