"""Transmit waveform generation: rectangular pulse, LFM chirp, pulse train.

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stage 1.
"""


def rectangular_pulse(cfg):
    """Return one rectangular pulse (fast-time samples)."""
    raise NotImplementedError("roadmap stage 1")


def lfm_chirp(cfg):
    """Return one complex analytic LFM chirp (fast-time samples)."""
    raise NotImplementedError("roadmap stage 1")


def pulse_train(cfg):
    """Return the pulse train as [n_pulses, samples_per_pulse]."""
    raise NotImplementedError("roadmap stage 1")


def transmit_waveform(cfg):
    """Return the full transmit waveform."""
    raise NotImplementedError("roadmap stage 1")
