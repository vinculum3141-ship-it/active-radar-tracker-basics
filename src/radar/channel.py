"""Channel model: propagation delay, attenuation, noise, targets.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 2.
"""

from dataclasses import dataclass

import numpy as np

from radar.config import RadarConfig

C_MPS = 3e8


def _wavelength_m(cfg: RadarConfig) -> float:
    """Carrier wavelength lambda = c / f_c."""
    return C_MPS / cfg.fc_hz


def _doppler_hz(velocity_mps: float, cfg: RadarConfig) -> float:
    """Doppler shift f_d = 2*v/lambda (01-physics.md §4)."""
    return 2.0 * velocity_mps / _wavelength_m(cfg)


@dataclass
class Target:
    """A target the radar is trying to see.

    ``range_m`` sets the round-trip delay; ``velocity_mps`` is carried for
    the Doppler stage (4) — stage 2 uses range only. ``snr_db`` is the
    echo-to-noise ratio at the receiver.
    """

    range_m: float
    velocity_mps: float
    angle_deg: float | None = None
    snr_db: float = 20.0


def _samples_per_pulse(cfg: RadarConfig) -> int:
    """Fast-time samples in one PRI (T * fs)."""
    return round(cfg.pri_s * cfg.fs_hz)


def _echo(pulse: np.ndarray, target: Target, cfg: RadarConfig) -> np.ndarray:
    """Noiseless echo of one pulse from one target (delayed, attenuated).

    Places a scaled copy of the transmit pulse at the round-trip delay
    ``round(2R/c * fs)`` inside a full PRI-length window. The scale factor is
    the amplitude that yields ``target.snr_db`` against unit-power noise
    (01-physics.md §1 measurement loop; the 1/R^4 range equation is an
    intuition tool, not needed here).
    """
    n_delay = round(2 * target.range_m / C_MPS * cfg.fs_hz)
    amplitude = 10 ** (target.snr_db / 20.0)
    rx = np.zeros(_samples_per_pulse(cfg), dtype=complex)
    n = min(pulse.size, rx.size - n_delay)
    if n > 0:
        rx[n_delay : n_delay + n] = amplitude * pulse[:n]
    return rx


def _complex_noise(shape, rng: np.random.Generator) -> np.ndarray:
    """Unit-power complex Gaussian noise (variance 1 in each quadrature)."""
    return rng.normal(0.0, 1.0 / np.sqrt(2.0), shape) + 1j * rng.normal(
        0.0, 1.0 / np.sqrt(2.0), shape
    )


def propagate(pulse: np.ndarray, target: Target, cfg: RadarConfig, rng) -> np.ndarray:
    """Return the received signal for one pulse and one target.

    The delayed, attenuated echo of ``pulse`` plus complex Gaussian noise,
    scaled so the echo SNR matches ``target.snr_db``.
    """
    return _echo(pulse, target, cfg) + _complex_noise(_samples_per_pulse(cfg), rng)


def simulate_channel(
    tx: np.ndarray,
    targets: list[Target],
    cfg: RadarConfig,
    rng,
    *,
    apply_doppler: bool = False,
) -> np.ndarray:
    """Return the received signal for a list of targets over a CPI.

    Sums each target's noiseless echo into every PRI row, then adds one noise
    draw per row — so multi-target SNR is not inflated by summing noise per
    target (01-physics.md §1 measurement loop).

    ``apply_doppler`` is **opt-in** and defaults to ``False`` so the default
    contract is exactly the Stage 1–3 channel (delay + attenuation + noise, no
    slow-time phase) — earlier stages are untouched. Set it ``True`` (roadmap
    stage 4) to impart the per-pulse Doppler phase from each target's radial
    velocity.

    Parameters
    ----------
    tx : np.ndarray
        Transmit pulse train ``[n_pulses, samples_per_pulse]``
        (signal_gen.transmit_waveform).
    targets : list[Target]
        One or more targets to simulate.
    cfg : RadarConfig
        Radar configuration.
    rng : np.random.Generator
        Seeded generator (04-python-discipline.md §2).
    apply_doppler : bool, keyword-only
        If ``True``, rotate each PRI's echo by ``2*pi*f_d*T*n`` (``f_d =
        2v/lambda``) — the slow-time phase that yields Doppler (01-physics.md
        §4). If ``False`` (default) the channel is range-only.

    Returns
    -------
    np.ndarray
        Received signal ``[n_pulses, samples_per_pulse]`` (data contract
        ``rx_slow``).
    """
    rx = np.zeros_like(tx)  # [n_pulses, samples_per_pulse]
    for target in targets:
        fd = _doppler_hz(target.velocity_mps, cfg) if apply_doppler else 0.0
        for n in range(cfg.n_pulses):
            # Slow-time phase rotation (only when requested): the target's
            # radial velocity advances the echo phase by 2*pi*f_d per PRI.
            # Fast-time (within-pulse) motion is negligible, so only
            # pulse-to-pulse phase changes (01-physics.md §4). The factor is
            # unit-modulus, so magnitude/delay/power — and therefore Stage 2/3
            # checks — are unaffected when enabled.
            phase = (
                np.exp(1j * 2.0 * np.pi * fd * cfg.pri_s * n) if apply_doppler else 1.0
            )
            rx[n] += phase * _echo(tx[n], target, cfg)
    rx += _complex_noise(rx.shape, rng)
    return rx
