"""Registry for ARC-AGI-2 contest CLI commands."""

from typing import Dict

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import CommandSpec

COMMANDS: Dict[str, CommandSpec] = {}

def register(cmd: CommandSpec) -> None:
    COMMANDS[cmd.name] = cmd

def get_all():
    return COMMANDS.values()