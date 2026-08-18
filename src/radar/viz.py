"""Visualization: plotting helpers (never plot by default; --plot enabled).

API spec: docs/training/04-python-discipline.md §3.
Implemented by roadmap stages as each plot is needed.
"""


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
