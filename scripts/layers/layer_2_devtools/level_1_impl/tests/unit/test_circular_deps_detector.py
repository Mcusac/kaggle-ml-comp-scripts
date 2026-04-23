from layers.layer_2_devtools.level_1_impl.level_2.circular_deps import _cycle_chain_for_component


def test_cycle_chain_prefers_a_real_cycle_path() -> None:
    graph = {
        "a": ["b"],
        "b": ["c"],
        "c": ["a"],
    }
    chain = _cycle_chain_for_component(component=["a", "b", "c"], graph=graph)
    assert chain[0] == chain[-1]
    assert chain[0] in {"a", "b", "c"}
    assert set(chain[:-1]) == {"a", "b", "c"}


def test_cycle_chain_self_loop() -> None:
    graph = {"a": ["a"]}
    assert _cycle_chain_for_component(component=["a"], graph=graph) == ["a", "a"]

