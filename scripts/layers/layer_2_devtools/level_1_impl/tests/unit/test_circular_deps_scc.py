from layers.layer_2_devtools.level_0_infra.level_0.graph.scc import find_cycles
from layers.layer_2_devtools.level_0_infra.level_0.graph.scc import (
    find_strongly_connected_components,
)


def test_scc_finds_single_cycle_component() -> None:
    g = {
        "a": ["b"],
        "b": ["c"],
        "c": ["a"],
    }
    sccs = find_strongly_connected_components(g)
    assert ["a", "b", "c"] in sccs
    cycles = find_cycles(g)
    assert cycles == [["a", "b", "c"]]


def test_scc_returns_dag_components_and_no_cycles() -> None:
    g = {
        "a": ["b", "c"],
        "b": ["c"],
        "c": [],
    }
    sccs = find_strongly_connected_components(g)
    assert sccs == [["a"], ["b"], ["c"]]
    assert find_cycles(g) == []


def test_self_loop_is_cycle() -> None:
    g = {"a": ["a"]}
    assert find_strongly_connected_components(g) == [["a"]]
    assert find_cycles(g) == [["a"]]

