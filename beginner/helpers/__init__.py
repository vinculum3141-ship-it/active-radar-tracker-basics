"""Beginner notebook helpers."""

from .channel import add_echo, awgn, single_target_channel
from .constants import RADAR_CONSTANTS, BaselineRadarSpec, baseline_spec
from .doppler import (
    build_pulse_stack,
    doppler_frequency_hz,
    range_doppler_map,
    velocity_from_doppler,
)
from .kalman import (
    predict,
    run_kalman_track,
    state_transition_matrix,
    update,
)
from .math import (
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
    "build_pulse_stack",
    "delay_samples_for_range",
    "doppler_frequency_hz",
    "duty_cycle",
    "instantaneous_frequency_hz",
    "lfm_chirp",
    "matched_filter",
    "predict",
    "range_from_delay_samples",
    "range_doppler_map",
    "range_resolution_from_bandwidth",
    "range_resolution_from_pulse_width",
    "rectangular_pulse",
    "run_kalman_track",
    "single_target_channel",
    "state_transition_matrix",
    "update",
    "velocity_from_doppler",
    "wavelength_m",
]
