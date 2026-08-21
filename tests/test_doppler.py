"""Tests for doppler.py (roadmap stage 4)."""

import numpy as np
import pytest

from radar import channel, doppler, receiver, signal_gen
from radar.config import RadarConfig


@pytest.fixture
def cfg() -> RadarConfig:
    """Baseline config (defaults; fixed numbers expected)."""
    return RadarConfig()


@pytest.fixture
def rng(cfg: RadarConfig) -> np.random.Generator:
    return np.random.default_rng(cfg.seed)


def _rd_map(cfg: RadarConfig, velocity_mps: float, rng) -> np.ndarray:
    """Build the range-Doppler map for a single target at 1000 m, `velocity`."""
    pulse = signal_gen.lfm_chirp(cfg)
    tx = signal_gen.transmit_waveform(cfg)
    tgt = channel.Target(range_m=1000.0, velocity_mps=velocity_mps, snr_db=20.0)
    rx = channel.simulate_channel(tx, [tgt], cfg, rng, apply_doppler=True)
    mf = receiver.matched_filter(rx, pulse)
    return doppler.range_doppler_map(mf, cfg)


def _folded_velocity(velocity_mps: float, cfg: RadarConfig) -> float:
    """Analytic apparent velocity after slow-time aliasing (01-physics.md §4).

    The Doppler FFT sees a folded frequency: ``f_app = ((f_d + PRF/2) mod PRF)
    - PRF/2`` with ``f_d = 2v/lambda`` and ``PRF = 1/T``; converted back to
    velocity this is the value the map must show.
    """
    wavelength = 3e8 / cfg.fc_hz
    fd = 2.0 * velocity_mps / wavelength
    prf = 1.0 / cfg.pri_s
    f_app = (fd + prf / 2.0) % prf - prf / 2.0
    return f_app * wavelength / 2.0


def test_map_dimensions(cfg: RadarConfig, rng) -> None:
    """RD map keeps the [n_pulses, samples_per_pulse] shape of the input."""
    rd = _rd_map(cfg, 40.0, rng)
    n_samples = round(cfg.pri_s * cfg.fs_hz)
    assert rd.shape == (cfg.n_pulses, n_samples)


def test_velocity_axis_resolution(cfg: RadarConfig) -> None:
    """Doppler bin width matches Delta_v = lambda/(2*N*T); axis centered at 0."""
    v = doppler.velocity_axis(cfg)
    assert v.size == cfg.n_pulses
    delta_v = v[1] - v[0]
    wavelength = 3e8 / cfg.fc_hz
    expected_delta = wavelength / (2.0 * cfg.n_pulses * cfg.pri_s)
    assert delta_v == pytest.approx(expected_delta, rel=1e-9)
    # fftshift axis: lower half negative, upper half positive, center ~0
    assert v[cfg.n_pulses // 2] == pytest.approx(0.0, abs=1e-9)


def test_range_axis_centered_on_target(cfg: RadarConfig) -> None:
    """Range axis puts the 1000 m target at ~1000 m (matches range profile)."""
    r = doppler.range_axis(cfg)
    assert r.size == round(cfg.pri_s * cfg.fs_hz)
    assert r[np.argmin(np.abs(r - 1000.0))] == pytest.approx(1000.0, abs=7.5)


def test_peak_velocity_aliased(cfg: RadarConfig, rng) -> None:
    """Baseline 40 m/s target aliases; peak within Delta_v/2 of folded v."""
    rd = _rd_map(cfg, 40.0, rng)
    v = doppler.velocity_axis(cfg)
    r = doppler.range_axis(cfg)
    r_idx = int(np.argmin(np.abs(r - 1000.0)))
    d_idx = int(np.argmax(np.abs(rd[:, r_idx])))
    measured_v = v[d_idx]
    folded = _folded_velocity(40.0, cfg)
    delta_v = v[1] - v[0]
    assert measured_v == pytest.approx(folded, abs=delta_v / 2.0)


def test_peak_velocity_unambiguous(cfg: RadarConfig, rng) -> None:
    """A sub-v_max velocity (15 m/s) appears at its true velocity cell."""
    rd = _rd_map(cfg, 15.0, rng)
    v = doppler.velocity_axis(cfg)
    r = doppler.range_axis(cfg)
    r_idx = int(np.argmin(np.abs(r - 1000.0)))
    d_idx = int(np.argmax(np.abs(rd[:, r_idx])))
    measured_v = v[d_idx]
    delta_v = v[1] - v[0]
    assert measured_v == pytest.approx(15.0, abs=delta_v / 2.0)


def test_zero_velocity_peak_at_center(cfg: RadarConfig, rng) -> None:
    """A stationary target sits at zero Doppler (center bin)."""
    rd = _rd_map(cfg, 0.0, rng)
    r = doppler.range_axis(cfg)
    r_idx = int(np.argmin(np.abs(r - 1000.0)))
    d_idx = int(np.argmax(np.abs(rd[:, r_idx])))
    assert d_idx == cfg.n_pulses // 2
