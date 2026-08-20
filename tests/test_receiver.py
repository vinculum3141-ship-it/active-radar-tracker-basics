"""Tests for receiver.py (roadmap stage 3)."""

import numpy as np
import pytest

from radar.channel import Target, propagate, simulate_channel
from radar.config import RadarConfig
from radar.receiver import detect_peaks, matched_filter, range_from_delay
from radar.signal_gen import lfm_chirp, transmit_waveform


@pytest.fixture
def cfg() -> RadarConfig:
    return RadarConfig()


@pytest.fixture
def rng(cfg: RadarConfig) -> np.random.Generator:
    return np.random.default_rng(cfg.seed)


def _matched_for(cfg: RadarConfig, targets, rng) -> np.ndarray:
    tx = transmit_waveform(cfg)
    rx = simulate_channel(tx, targets, cfg, rng)
    return matched_filter(rx, lfm_chirp(cfg))


def test_matched_filter_shape_1d(cfg: RadarConfig, rng) -> None:
    """1D in -> 1D out, same length (mode='same' preserves the time axis)."""
    rx = propagate(lfm_chirp(cfg), Target(1000.0, 40.0), cfg, rng)
    y = matched_filter(rx, lfm_chirp(cfg))
    assert y.shape == rx.shape


def test_matched_filter_shape_2d(cfg: RadarConfig, rng) -> None:
    """2D [n_pulses, samples] in -> same shape out."""
    y = _matched_for(cfg, [Target(1000.0, 40.0)], rng)
    assert y.shape == (cfg.n_pulses, round(cfg.pri_s * cfg.fs_hz))


def test_matched_filter_peak_at_delay_plus_offset(cfg: RadarConfig, rng) -> None:
    """Peak lands at delay + len(pulse)//2 = 133 + 200 = 333 (mode='same')."""
    y = _matched_for(cfg, [Target(1000.0, 40.0)], rng)
    peak = int(np.argmax(np.abs(y[0])))
    n_delay = round(2 * 1000.0 / 3e8 * cfg.fs_hz)
    assert peak == n_delay + round(cfg.pulse_width_s * cfg.fs_hz) // 2


def test_matched_filter_compresses_pulse(cfg: RadarConfig, rng) -> None:
    """Compressed peak is far narrower than the 400-sample pulse (sharpness)."""
    y = np.abs(_matched_for(cfg, [Target(1000.0, 40.0, snr_db=30.0)], rng)[0])
    p = int(np.argmax(y))
    half = y[p] / 2
    left, right = p, p
    while left > 0 and y[left] > half:
        left -= 1
    while right < len(y) - 1 and y[right] > half:
        right += 1
    assert right - left < 40  # pulse was 400 samples


def test_range_from_delay(cfg: RadarConfig) -> None:
    """133 samples -> 997.5 m (R = c*dt/2, 7.5 m per sample)."""
    assert range_from_delay(133, cfg) == pytest.approx(997.5)
    assert range_from_delay(0, cfg) == 0.0
    assert range_from_delay(1, cfg) == pytest.approx(3e8 / (2 * cfg.fs_hz))


def test_detect_peaks_single_target(cfg: RadarConfig, rng) -> None:
    """One detection, range within one 7.5 m bin of the 1000 m truth."""
    dets = detect_peaks(_matched_for(cfg, [Target(1000.0, 40.0)], rng), cfg)
    assert len(dets) == 1
    assert dets[0].range_m == pytest.approx(1000.0, abs=7.5)


def test_detect_peaks_snr_matches_gain(cfg: RadarConfig, rng) -> None:
    """20 dB input + 26 dB processing gain (N = tau*fs = 400) -> ~46 dB."""
    dets = detect_peaks(_matched_for(cfg, [Target(1000.0, 40.0)], rng), cfg)
    assert len(dets) == 1
    assert dets[0].snr_db == pytest.approx(46.0, abs=3.0)


def test_detect_peaks_two_targets_stretch(cfg: RadarConfig, rng) -> None:
    """Two targets -> two detections, both within one range bin of truth."""
    dets = detect_peaks(
        _matched_for(cfg, [Target(1000.0, 0.0), Target(5000.0, 0.0)], rng), cfg
    )
    ranges = sorted(d.range_m for d in dets)
    assert len(ranges) == 2
    assert ranges[0] == pytest.approx(1000.0, abs=7.5)
    assert ranges[1] == pytest.approx(5000.0, abs=7.5)


def test_detect_peaks_noise_only(cfg: RadarConfig, rng) -> None:
    """No target -> no detections at a 15 dB threshold (deterministic)."""
    tx = transmit_waveform(cfg)
    noise = tx * 0 + (
        rng.normal(0, 1 / np.sqrt(2), tx.shape)
        + 1j * rng.normal(0, 1 / np.sqrt(2), tx.shape)
    )
    y = matched_filter(noise, lfm_chirp(cfg))
    assert detect_peaks(y, cfg, threshold_db=15.0) == []


def test_detect_peaks_threshold_gates_by_height(cfg: RadarConfig) -> None:
    """Synthetic spike over a flat floor: gate works purely on height.

    One compressed peak (power 1000) over a unit floor -> SNR ~28 dB. It is
    reported at a 20 dB threshold but suppressed at 30 dB, deterministically
    (no noise, flat floor -> no other peaks).
    """
    n = round(cfg.pri_s * cfg.fs_hz)
    y = np.full(n, 1.0)
    y[200 + 133] = np.sqrt(1000.0)
    assert detect_peaks(y, cfg, threshold_db=30.0) == []
    dets = detect_peaks(y, cfg, threshold_db=20.0)
    assert len(dets) == 1
    assert dets[0].range_m == pytest.approx(1000.0, abs=7.5)
