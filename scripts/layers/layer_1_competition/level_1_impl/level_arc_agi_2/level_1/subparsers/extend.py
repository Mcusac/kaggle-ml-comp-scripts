from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import get_all

def extend_subparsers(subparsers):
    for cmd in get_all():
        p = subparsers.add_parser(cmd.name, help=cmd.help)
        cmd.builder(p)