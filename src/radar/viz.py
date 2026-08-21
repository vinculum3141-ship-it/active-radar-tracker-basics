"""Visualization: plotting helpers (never plot by default; --plot enabled).

API spec: docs/training/04-python-discipline.md §3.
Reproducibility: save_plot wired in (see §5); the plot_* functions below
are the learner's to implement per stage.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def save_plot(fig, name: str, stage: str, cfg) -> Path:
    """Save a figure to `<cfg.out_dir>/<stage>/<name>.png`.

    Makes the directory if needed and closes the figure. Call this from the
    subcommand handlers (cli.py) whenever `--plot` is given (§5).
    """
    out_dir = Path(cfg.out_dir) / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_pulse(tx, cfg):
    """Plot the transmit pulse magnitude over time in microseconds.

    Uses the first pulse of the train. For the baseline config the pulse
    spans 20 us (400 samples at 20 MHz).
    """
    pulse = tx[0] if tx.ndim == 2 else tx
    t_us = np.arange(pulse.size) / cfg.fs_hz * 1e6
    fig, ax = plt.subplots()
    ax.plot(t_us, np.abs(pulse))
    ax.set_xlabel("time (us)")
    ax.set_ylabel("magnitude")
    ax.set_title(
        f"Transmit pulse ({cfg.pulse_type}, tau = {cfg.pulse_width_s * 1e6:.0f} us)"
    )
    ax.set_xlim(0, cfg.pulse_width_s * 1e6)
    fig.tight_layout()
    return fig


def plot_echo(rx, matched, cfg):
    """Two-panel plot: |rx| echo and |matched| filter output over time.

    The echo panel shows the 400-sample pulse buried in noise; the matched
    panel shows the compressed spike (~6 samples wide) at the same delay,
    making the range-estimation job obvious. Uses the first pulse row.
    """
    if rx.ndim == 2:
        rx = rx[0]
    if matched.ndim == 2:
        matched = matched[0]
    t_us = np.arange(len(rx)) / cfg.fs_hz * 1e6
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(9, 5))
    axes[0].plot(t_us, np.abs(rx))
    axes[0].set_ylabel("|echo|")
    axes[0].set_title("Received echo (pulse buried in noise)")
    axes[1].plot(t_us, np.abs(matched))
    axes[1].set_ylabel("|matched|")
    axes[1].set_xlabel("time (us)")
    axes[1].set_title("Matched-filter output (compressed spike at the delay)")
    fig.tight_layout()
    return fig


def plot_range_profile(matched, cfg):
    """Plot the matched-filter magnitude versus range in meters.

    The range axis is the sample index minus the correlation offset
    (len(pulse)//2), converted via R = c*t/2, so the target sits at its true
    range (997.5 m for the baseline 1000 m target).
    """
    if matched.ndim == 2:
        matched = matched[0]
    n_pulse = round(cfg.pulse_width_s * cfg.fs_hz)
    r_m = (np.arange(len(matched)) - n_pulse // 2) * 3e8 / (2 * cfg.fs_hz)
    fig, ax = plt.subplots()
    ax.plot(r_m / 1e3, np.abs(matched))
    ax.set_xlabel("range (km)")
    ax.set_ylabel("|matched|")
    ax.set_title("Range profile")
    fig.tight_layout()
    return fig


def plot_rd_map(rd_map, cfg):
    """Plot the range-Doppler map magnitude (dB) over range and velocity.

    Axes use ``doppler.range_axis`` / ``doppler.velocity_axis`` so the target's
    true range and (folded) velocity land at their analytical cells (roadmap
    stage 4). Velocity is on the y-axis, range on the x-axis; magnitude is in
    dB relative to the map peak so the blob stands out from the noise floor.
    """
    from radar.doppler import range_axis, velocity_axis

    r = range_axis(cfg) / 1e3  # km
    v = velocity_axis(cfg)
    mag_db = 20 * np.log10(np.abs(rd_map) + 1e-12)
    mag_db -= mag_db.max()

    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(
        mag_db,
        origin="lower",
        aspect="auto",
        extent=[r[0], r[-1], v[0], v[-1]],
        cmap="viridis",
        vmin=-60,
    )
    ax.set_xlabel("range (km)")
    ax.set_ylabel("velocity (m/s)")
    ax.set_title("Range-Doppler map")
    fig.colorbar(im, ax=ax, label="magnitude (dB)")
    fig.tight_layout()
    return fig


def plot_track(true, measured, track):
    raise NotImplementedError("roadmap stage 5")


def plot_beam_pattern(thetas_deg, pattern):
    raise NotImplementedError("roadmap stage 6")


def plot_array_geometry(cfg):
    raise NotImplementedError("roadmap stage 6")
