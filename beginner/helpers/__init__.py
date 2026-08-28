"""Beginner notebook helpers."""

from .array import (
    array_factor,
    first_null_angle_deg,
    inter_element_phase_rad,
    steering_vector,
)
from .channel import add_echo, awgn, single_target_channel
from .constants import RADAR_CONSTANTS, BaselineRadarSpec, baseline_spec
from .doppler import (
    build_pulse_stack,
    doppler_frequency_hz,
    range_doppler_map,
    velocity_from_doppler,
)
from .doa import (
    bartlett_spectrum,
    mvdr_spectrum,
    sample_covariance,
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
from .steering import lcmv_weights, steering_weights
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
    "array_factor",
    "awgn",
    "bartlett_spectrum",
    "baseline_spec",
    "build_pulse_stack",
    "delay_samples_for_range",
    "doppler_frequency_hz",
    "duty_cycle",
    "first_null_angle_deg",
    "instantaneous_frequency_hz",
    "inter_element_phase_rad",
    "lcmv_weights",
    "lfm_chirp",
    "matched_filter",
    "mvdr_spectrum",
    "predict",
    "range_from_delay_samples",
    "range_doppler_map",
    "range_resolution_from_bandwidth",
    "range_resolution_from_pulse_width",
    "rectangular_pulse",
    "run_kalman_track",
    "sample_covariance",
    "single_target_channel",
    "state_transition_matrix",
    "steering_vector",
    "steering_weights",
    "update",
    "velocity_from_doppler",
    "wavelength_m",
]
