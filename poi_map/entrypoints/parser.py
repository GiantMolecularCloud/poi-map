import argparse
import json
from pathlib import Path
from typing import Sequence

from ..config.models import POIMapConfig


def parse_config(argv: Sequence[str] | None = None) -> POIMapConfig:
    """
    Parse the JSON config into the config model.

    :param description: CLI Description.
    :param argv: Optional sequence of arguments to the argument parser.
    :return: The config model.
    """
    parser = make_parser()
    args = parser.parse_args(argv)

    if args.config.suffix == ".json":
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        raise ValueError(f"File type {args.config.suffix} is not supported. Config file has to be JSON.")

    return POIMapConfig(**config)


def make_parser() -> argparse.ArgumentParser:
    """
    Function to create ArgumentParser.

    :return: ArgumentParser
    """
    parser = argparse.ArgumentParser(description="A quick and dirty track labeling app.")

    parser.add_argument(
        "config",
        help="Path of the config file.",
        type=Path,
    )

    return parser
