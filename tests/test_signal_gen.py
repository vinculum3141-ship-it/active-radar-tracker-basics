"""Tests for signal_gen.py (roadmap stage 1)."""

import numpy as np
import pytest

from radar.config import RadarConfig
from radar.signal_gen import (
    lfm_chirp,
    pulse_train,
    rectangular_pulse,
    transmit_waveform,
)


@pytest.fixture
def cfg() -> RadarConfig:
    """Baseline config (defaults; deliberately not tiny for the fixed numbers)."""
    return RadarConfig()


def _n_pulse_samples(cfg: RadarConfig) -> int:
    return round(cfg.pulse_width_s * cfg.fs_hz)


def _samples_per_pulse(cfg: RadarConfig) -> int:
    return round(cfg.pri_s * cfg.fs_hz)


def _inst_freq_hz(chirp: np.ndarray, fs_hz: float) -> np.ndarray:
    """Instantaneous frequency (Hz) per sample, from unwrapped phase."""
    phase = np.unwrap(np.angle(chirp))
    return np.diff(phase) / (2.0 * np.pi) * fs_hz


def test_rectangular_pulse_length(cfg: RadarConfig) -> None:
    """One pulse spans exactly tau at fs: 20 us * 20 MHz = 400 samples."""
    pulse = rectangular_pulse(cfg)
    assert pulse.size == _n_pulse_samples(cfg)
    assert pulse.size == 400


def test_rectangular_pulse_unit_amplitude(cfg: RadarConfig) -> None:
    """A rectangular pulse is a unit-amplitude complex envelope."""
    assert np.allclose(np.abs(rectangular_pulse(cfg)), 1.0)


def test_rectangular_pulse_complex(cfg: RadarConfig) -> None:
    """The baseband pulse is complex (data contract says complex everywhere)."""
    assert rectangular_pulse(cfg).dtype == np.complex128


def test_lfm_chirp_length(cfg: RadarConfig) -> None:
    assert lfm_chirp(cfg).size == _n_pulse_samples(cfg)


def test_lfm_chirp_complex_analytic(cfg: RadarConfig) -> None:
    """Analytic chirp is unit magnitude, no DC/imag-only degeneracy."""
    chirp = lfm_chirp(cfg)
    assert np.allclose(np.abs(chirp), 1.0)
    assert np.any(chirp.imag != 0)


def test_lfm_chirp_sweeps_bandwidth(cfg: RadarConfig) -> None:
    """Instantaneous frequency starts near 0 and ends near B = 5 MHz."""
    f = _inst_freq_hz(lfm_chirp(cfg), cfg.fs_hz)
    assert f[0] < 50e3
    assert f[-1] == pytest.approx(cfg.bandwidth_hz, rel=0.05)


def test_lfm_chirp_monotonic_frequency(cfg: RadarConfig) -> None:
    """A linear chirp sweeps monotonically upward (k = B/tau > 0)."""
    f = _inst_freq_hz(lfm_chirp(cfg), cfg.fs_hz)
    assert np.all(np.diff(f) > 0)


def test_pulse_train_shape(cfg: RadarConfig) -> None:
    """Train is [n_pulses, samples_per_pulse] = (64, 20000)."""
    train = pulse_train(cfg)
    assert train.shape == (cfg.n_pulses, _samples_per_pulse(cfg))
    assert train.shape == (64, 20000)


def test_pulse_train_silent_between_pulses(cfg: RadarConfig) -> None:
    """Only the first tau*fs samples of each row carry energy."""
    train = pulse_train(cfg)
    n = _n_pulse_samples(cfg)
    assert np.all(train[:, n:] == 0)
    assert np.all(np.abs(train[:, :n]) > 0)


def test_pulse_train_embeds_chirp(cfg: RadarConfig) -> None:
    """Default (lfm) train embeds the chirp at the start of each row."""
    train = pulse_train(cfg)
    assert np.allclose(train[0, :400], lfm_chirp(cfg))


def test_pulse_train_rows_identical(cfg: RadarConfig) -> None:
    """Every pulse in the train is the same waveform (coherent CPI)."""
    train = pulse_train(cfg)
    assert np.allclose(train[1:], train[0])


def test_transmit_waveform_selects_type() -> None:
    """pulse_type='rect' gives a rectangular train, 'lfm' a chirp."""
    rect = transmit_waveform(RadarConfig(pulse_type="rect"))
    lfm = transmit_waveform(RadarConfig(pulse_type="lfm"))
    assert np.all(rect[:, :400].imag == 0)
    assert np.any(lfm[:, :400].imag != 0)
    assert np.allclose(lfm, pulse_train(RadarConfig(pulse_type="lfm")))
