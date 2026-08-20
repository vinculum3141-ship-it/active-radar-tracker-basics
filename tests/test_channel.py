"""Tests for channel.py (roadmap stage 2)."""

import numpy as np
import pytest

from radar.channel import Target, propagate, simulate_channel
from radar.config import RadarConfig
from radar.signal_gen import transmit_waveform


@pytest.fixture
def cfg() -> RadarConfig:
    """Baseline config (defaults; fixed numbers expected)."""
    return RadarConfig()


@pytest.fixture
def rng(cfg: RadarConfig) -> np.random.Generator:
    return np.random.default_rng(cfg.seed)


def _echo_amplitude(snr_db: float) -> float:
    """Amplitude that yields snr_db against unit-power noise."""
    return 10 ** (snr_db / 20.0)


def _echo_onset(rx_row: np.ndarray, snr_db: float) -> int:
    """First sample where the echo is above half its expected amplitude."""
    idx = np.where(np.abs(rx_row) > _echo_amplitude(snr_db) / 2.0)[0]
    return int(idx[0]) if idx.size else -1


def _echo_onsets(rx_row: np.ndarray, snr_db: float) -> set[int]:
    """All rising-edge onsets (for the multi-target stretch)."""
    above = np.abs(rx_row) > _echo_amplitude(snr_db) / 2.0
    return {int(i) for i in np.where(above & ~np.roll(above, 1))[0]}


def _delay_samples(range_m: float, cfg: RadarConfig) -> int:
    return round(2 * range_m / 3e8 * cfg.fs_hz)


def test_target_defaults() -> None:
    """angle_deg is optional, snr_db defaults to 20 dB."""
    t = Target(range_m=1000.0, velocity_mps=40.0)
    assert t.angle_deg is None
    assert t.snr_db == 20.0


def test_delay_1000m(cfg: RadarConfig, rng) -> None:
    """Echo onset at round(2R/c * fs) = 133 for R = 1000 m."""
    tx = transmit_waveform(cfg)
    t = Target(range_m=1000.0, velocity_mps=40.0, snr_db=20.0)
    rx = simulate_channel(tx, [t], cfg, rng)
    assert _echo_onset(rx[0], t.snr_db) == 133


def test_delay_500m(cfg: RadarConfig, rng) -> None:
    """R = 500 m -> delay 67 samples (scale check on the 2R/c formula)."""
    tx = transmit_waveform(cfg)
    t = Target(range_m=500.0, velocity_mps=0.0, snr_db=20.0)
    rx = simulate_channel(tx, [t], cfg, rng)
    assert _echo_onset(rx[0], t.snr_db) == _delay_samples(500.0, cfg)


def test_noise_power_unit(cfg: RadarConfig, rng) -> None:
    """Quiet-region power is ~1 (unit-power complex noise)."""
    tx = transmit_waveform(cfg)
    rx = simulate_channel(tx, [Target(1000.0, 40.0)], cfg, rng)
    power = np.mean(np.abs(rx[:, 2000:]) ** 2)
    assert power == pytest.approx(1.0, rel=0.1)


def test_measured_snr_matches(cfg: RadarConfig, rng) -> None:
    """Echo-to-noise ratio at the receiver matches target.snr_db (20 dB)."""
    tx = transmit_waveform(cfg)
    t = Target(range_m=1000.0, velocity_mps=40.0, snr_db=20.0)
    rx = simulate_channel(tx, [t], cfg, rng)
    n_delay = _delay_samples(t.range_m, cfg)
    echo = rx[0, n_delay : n_delay + 400]
    noise_power = np.mean(np.abs(rx[0, 2000:]) ** 2)
    signal_power = np.mean(np.abs(echo) ** 2) - noise_power
    snr_db_measured = 10 * np.log10(signal_power / noise_power)
    assert snr_db_measured == pytest.approx(t.snr_db, abs=1.0)


def test_signal_power_matches_snr(cfg: RadarConfig, rng) -> None:
    """Echo power ~= 10^(snr/10) = 100 against unit noise (A = 10^(snr/20))."""
    tx = transmit_waveform(cfg)
    t = Target(range_m=1000.0, velocity_mps=40.0, snr_db=20.0)
    rx = simulate_channel(tx, [t], cfg, rng)
    n_delay = _delay_samples(t.range_m, cfg)
    power = np.mean(np.abs(rx[0, n_delay : n_delay + 400]) ** 2)
    assert power == pytest.approx(100.0, rel=0.1)


def test_simulate_channel_shape(cfg: RadarConfig, rng) -> None:
    """Output is [n_pulses, samples_per_pulse] = (64, 20000)."""
    tx = transmit_waveform(cfg)
    rx = simulate_channel(tx, [Target(1000.0, 40.0)], cfg, rng)
    assert rx.shape == (cfg.n_pulses, round(cfg.pri_s * cfg.fs_hz))


def test_complex_dtype(cfg: RadarConfig, rng) -> None:
    tx = transmit_waveform(cfg)
    rx = simulate_channel(tx, [Target(1000.0, 40.0)], cfg, rng)
    assert rx.dtype == np.complex128


def test_deterministic_seed(cfg: RadarConfig) -> None:
    """Same seed -> identical received signal (04-python-discipline.md §2)."""
    tx = transmit_waveform(cfg)
    t = Target(1000.0, 40.0)
    a = simulate_channel(tx, [t], cfg, np.random.default_rng(cfg.seed))
    b = simulate_channel(tx, [t], cfg, np.random.default_rng(cfg.seed))
    assert np.array_equal(a, b)


def test_two_targets_stretch(cfg: RadarConfig, rng) -> None:
    """Two targets at different ranges -> echoes at both delays.

    Ranges are spaced > 3000 m so the 400-sample echoes do not overlap and
    each onset is cleanly detectable (roadmap stretch, stage 2).
    """
    tx = transmit_waveform(cfg)
    t1 = Target(range_m=1000.0, velocity_mps=0.0, snr_db=20.0)
    t2 = Target(range_m=5000.0, velocity_mps=0.0, snr_db=20.0)
    rx = simulate_channel(tx, [t1, t2], cfg, rng)
    onsets = _echo_onsets(rx[0], t1.snr_db)
    assert _delay_samples(t1.range_m, cfg) in onsets
    assert _delay_samples(t2.range_m, cfg) in onsets


def test_propagate_single_pulse(cfg: RadarConfig, rng) -> None:
    """propagate is the single-pulse, single-target path (echo + noise)."""
    from radar.signal_gen import lfm_chirp

    pulse = lfm_chirp(cfg)
    t = Target(range_m=1000.0, velocity_mps=40.0, snr_db=20.0)
    rx = propagate(pulse, t, cfg, rng)
    assert rx.shape == (round(cfg.pri_s * cfg.fs_hz),)
    assert _echo_onset(rx, t.snr_db) == 133
