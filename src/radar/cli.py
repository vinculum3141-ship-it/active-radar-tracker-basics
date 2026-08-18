"""Command-line entry points: simulate, bench, plot, track.

API spec: docs/training/04-python-discipline.md §3.
Reproducibility: the shell below loads the config and prints the banner on
every run (§5); the subcommand handlers are the learner's to implement.
"""

import argparse
import sys

from radar.config import RadarConfig, config_summary, load_config


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="configs/*.yaml to load (default: RadarConfig defaults)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="save plots to out/<stage>/ via viz.save_plot",
    )


def simulate(cfg: RadarConfig, args: argparse.Namespace) -> None:
    raise NotImplementedError("roadmap stages 1-4 pipeline")


def bench(cfg: RadarConfig, args: argparse.Namespace) -> None:
    raise NotImplementedError("roadmap stages 1-12 benchmark")


def plot(cfg: RadarConfig, args: argparse.Namespace) -> None:
    raise NotImplementedError("roadmap stages 1-6 viz")


def track(cfg: RadarConfig, args: argparse.Namespace) -> None:
    raise NotImplementedError("roadmap stage 5 tracker")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="radar", description="Active radar tracker (fully simulated)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    handlers = {"simulate": simulate, "bench": bench, "plot": plot, "track": track}
    for name, handler in handlers.items():
        cmd = sub.add_parser(name)
        _add_common_args(cmd)
        cmd.set_defaults(handler=handler)

    args = parser.parse_args()
    cfg = load_config(args.config)
    print(config_summary(cfg))  # reproducibility: banner on every run (§5)
    try:
        args.handler(cfg, args)
    except NotImplementedError as e:
        detail = f" ({e})" if str(e) else ""
        print(
            f"radar: '{args.command}' is not implemented yet{detail} - "
            "see docs/training/05-roadmap.md",
            file=sys.stderr,
        )
        raise SystemExit(1) from e
