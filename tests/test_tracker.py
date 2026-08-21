"""Tests for tracker.py (roadmap stage 5)."""

import numpy as np
import pytest

from radar import receiver
from radar.config import RadarConfig
from radar.tracker import KalmanTracker, State


@pytest.fixture
def cfg() -> RadarConfig:
    """Baseline config (defaults; fixed numbers expected)."""
    return RadarConfig()


def _constant_velocity_track(dt_s, n, r0, v, sigma, seed):
    """Return (true States, noisy Detections) for a constant-velocity target."""
    rng = np.random.default_rng(seed)
    true = []
    meas = []
    for k in range(n):
        R = r0 + v * k * dt_s
        zr = R + rng.normal(0.0, sigma)
        zv = v + rng.normal(0.0, sigma)
        true.append(State(R, v))
        meas.append(receiver.Detection(range_m=zr, velocity=zv))
    return true, meas


def _run(tracker, meas):
    for m in meas:
        tracker.predict()
        tracker.update(m)
    return tracker.track


def test_api_shape() -> None:
    """predict/update return State; track is a list of States."""
    t = KalmanTracker(dt_s=0.1, q=1.0, r=25.0)
    d = receiver.Detection(range_m=1000.0, velocity=40.0)
    pred = t.predict()
    upd = t.update(d)
    assert isinstance(pred, State)
    assert isinstance(upd, State)
    assert isinstance(t.track, list)
    assert all(isinstance(s, State) for s in t.track)
    assert len(t.track) == 1


def test_range_only_accepted() -> None:
    """A range-only Detection (velocity=None) still updates without error."""
    t = KalmanTracker(dt_s=0.1, q=1.0, r=25.0)
    t.predict()
    s = t.update(receiver.Detection(range_m=1000.0, velocity=None))
    assert np.isfinite(s.range_m)


def test_steady_state_error_below_measurement_noise(cfg) -> None:
    """Steady-state RMS track error < measurement-noise std (sqrt(r))."""
    dt, n, r0, v = 0.1, 120, 1000.0, 40.0
    sigma = 5.0
    true, meas = _constant_velocity_track(dt, n, r0, v, sigma, cfg.seed)
    track = _run(KalmanTracker(dt, q=2.0, r=sigma**2), meas)

    k0 = 20  # discard the transient
    true_arr = np.array([[s.range_m, s.velocity_mps] for s in true])[k0:]
    track_arr = np.array([[s.range_m, s.velocity_mps] for s in track])[k0:]
    rms = np.sqrt(np.mean((track_arr - true_arr) ** 2, axis=0))

    assert rms[0] < sigma
    assert rms[1] < sigma


def test_track_smooths_measurements(cfg) -> None:
    """Track RMS error is below the raw measurement RMS error."""
    dt, n, r0, v = 0.1, 120, 1000.0, 40.0
    sigma = 5.0
    true, meas = _constant_velocity_track(dt, n, r0, v, sigma, cfg.seed)
    track = _run(KalmanTracker(dt, q=2.0, r=sigma**2), meas)

    k0 = 20
    true_arr = np.array([[s.range_m, s.velocity_mps] for s in true])[k0:]
    track_arr = np.array([[s.range_m, s.velocity_mps] for s in track])[k0:]
    meas_arr = np.array([[m.range_m, m.velocity] for m in meas])[k0:]

    track_rms = np.sqrt(np.mean((track_arr - true_arr) ** 2, axis=0))
    meas_rms = np.sqrt(np.mean((meas_arr - true_arr) ** 2, axis=0))
    assert track_rms[0] < meas_rms[0]
    assert track_rms[1] < meas_rms[1]


def test_converges_on_constant_velocity(cfg) -> None:
    """Tracked velocity converges to the true constant velocity."""
    dt, n, r0, v = 0.1, 120, 1000.0, 40.0
    sigma = 5.0
    _, meas = _constant_velocity_track(dt, n, r0, v, sigma, cfg.seed)
    track = _run(KalmanTracker(dt, q=2.0, r=sigma**2), meas)
    steady_vel = np.mean([s.velocity_mps for s in track[20:]])
    assert steady_vel == pytest.approx(v, abs=1.0)
