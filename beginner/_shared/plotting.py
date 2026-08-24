from __future__ import annotations

import matplotlib.pyplot as plt


def apply_notebook_style() -> None:
    """Apply a simple shared plotting style for the beginner notebooks."""

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.figsize": (10, 4),
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )


def save_figure(fig: plt.Figure, path: str) -> None:
    """Save a figure with consistent notebook-friendly defaults."""

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
