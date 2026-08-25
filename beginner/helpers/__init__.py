"""Beginner notebook helpers."""

from .channel import add_echo, awgn, single_target_channel
from .constants import RADAR_CONSTANTS, BaselineRadarSpec
from .math import (
    baseline_spec,
    delay_samples_for_range,
    duty_cycle,
    range_from_delay_samples,
    range_resolution_from_bandwidth,
    range_resolution_from_pulse_width,
    wavelength_m,
)
from .waveforms import (
    instantaneous_frequency_hz,
    lfm_chirp,
    matched_filter,
    rectangular_pulse,
)

__all__ = [
    "RADAR_CONSTANTS",
    "BaselineRadarSpec",
    "add_echo",
    "awgn",
    "baseline_spec",
    "delay_samples_for_range",
    "duty_cycle",
    "instantaneous_frequency_hz",
    "lfm_chirp",
    "matched_filter",
    "range_from_delay_samples",
    "range_resolution_from_bandwidth",
    "range_resolution_from_pulse_width",
    "rectangular_pulse",
    "single_target_channel",
    "wavelength_m",
]
