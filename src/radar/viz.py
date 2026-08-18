"""Visualization: plotting helpers (never plot by default; --plot enabled).

API spec: docs/training/04-python-discipline.md §3.
Reproducibility: save_plot wired in (see §5); the plot_* functions below
are the learner's to implement per stage.
"""

from pathlib import Path

import matplotlib.pyplot as plt


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
    raise NotImplementedError("roadmap stage 1")


def plot_echo(rx, matched, cfg):
    raise NotImplementedError("roadmap stage 3")


def plot_range_profile(matched, cfg):
    raise NotImplementedError("roadmap stage 3")


def plot_rd_map(rd_map, cfg):
    raise NotImplementedError("roadmap stage 4")


def plot_track(true, measured, track):
    raise NotImplementedError("roadmap stage 5")


def plot_beam_pattern(thetas_deg, pattern):
    raise NotImplementedError("roadmap stage 6")


def plot_array_geometry(cfg):
    raise NotImplementedError("roadmap stage 6")
