"""Shared argparse fragments for ARC contest subcommands."""

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_run_context


def add_seed_and_run_context(parser: Any) -> None:
    """Random seed plus run folder metadata (matches legacy ``add_run`` recipes)."""
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    add_run_context(parser)
