"""Universal CLI arguments (config only)."""

import argparse


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments universal to every command regardless of domain."""
    parser.add_argument('--config', type=str, help='Path to config YAML file')
