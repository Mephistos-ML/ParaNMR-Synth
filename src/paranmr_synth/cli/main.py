"""Command-line entrypoint for paraNMR-Synth."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from paranmr_synth.app.pipelines import run_generate
from paranmr_synth.cfg import GenerateConfig
from paranmr_synth.cli.set_logging import setup_logging

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""

    parser = argparse.ArgumentParser(
        prog="paranmr-synth",
        description="Generate paranmr-compatible susceptibility tensor series.",
    )
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument(
        "--version",
        action="store_true",
        help="show version",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show debug logs",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="show errors only",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="run generation from YAML",
        description="Generate tensor series from a YAML config file.",
    )
    run_parser.add_argument(
        "config_file",
        help="YAML config path",
    )

    return parser


def main() -> int:
    """CLI entrypoint."""

    parser = build_parser()
    args = parser.parse_args()
    setup_logging(
        verbose=getattr(args, "verbose", False),
        quiet=getattr(args, "quiet", False),
    )

    if args.version:
        from paranmr_synth.__version__ import __version__

        print(__version__)
        return 0

    if args.command == "run":
        logger.info("Loading generation config from %s", args.config_file)
        config_path = Path(args.config_file).resolve()
        config = GenerateConfig.from_file(config_path)
        spec = config.to_series_generator_spec()
        output_name = config.output_name if config.output_name is not None else config_path.stem
        written_files = run_generate(
            spec,
            output_dir=config_path.parent / output_name,
            seed=config.seed,
            series_metadata=config.to_report_metadata(),
        )
        logger.info("Generated %d tensor series file(s)", len(written_files))
        return 0

    parser.print_help()
    return 0
