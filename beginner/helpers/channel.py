from __future__ import annotations

import numpy as np


def add_echo(signal: np.ndarray, template: np.ndarray, delay_samples: int, attenuation_linear: float = 1.0) -> np.ndarray:
    """Add a delayed, attenuated copy of ``template`` into ``signal``."""

    required_len = delay_samples + len(template)
    out = signal.copy()
    if required_len > len(out):
        out = np.pad(out, (0, required_len - len(out)))
    out[delay_samples : delay_samples + len(template)] += attenuation_linear * template
    return out


def awgn(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """Return ``signal`` with white Gaussian noise added to achieve the target SNR in dB."""

    sig_power = np.mean(np.abs(signal) ** 2)
    noise_power = sig_power / (10.0 ** (snr_db / 10.0))
    if np.iscomplexobj(signal):
        noise = np.sqrt(noise_power / 2.0) * (
            np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))
        )
    else:
        noise = np.sqrt(noise_power) * np.random.randn(len(signal))
    return signal + noise


def single_target_channel(
    transmitted: np.ndarray,
    delay_samples: int,
    attenuation_linear: float = 1.0,
    snr_db: float = 20.0,
) -> np.ndarray:
    """Return a received signal with one delayed, attenuated echo plus noise."""

    received = np.zeros(delay_samples + len(transmitted), dtype=transmitted.dtype)
    received = add_echo(received, transmitted, delay_samples, attenuation_linear)
    return awgn(received, snr_db)
