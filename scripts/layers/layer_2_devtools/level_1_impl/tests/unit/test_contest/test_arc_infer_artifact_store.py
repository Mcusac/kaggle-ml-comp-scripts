"""Tests for ARC inference artifact layout (stdlib; no layers package import chain)."""

import importlib.util
import json
from pathlib import Path


def _load_infer_store():
    here = Path(__file__).resolve()
    mod_path = (
        here.parents[5]
        / "layer_1_competition"
        / "level_1_impl"
        / "level_arc_agi_2"
        / "level_0"
        / "arc_infer_artifact_store.py"
    )
    spec = importlib.util.spec_from_file_location("arc_infer_artifact_store_iso", mod_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_infer_layout_shard_roundtrip_and_finalize(tmp_path: Path) -> None:
    m = _load_infer_store()
    root = str(tmp_path / "run1")
    infer_out, dec_dir, inter_dir = m.infer_ensure_run_layout(root)
    assert Path(infer_out).is_dir()
    assert Path(dec_dir).is_dir()
    assert Path(inter_dir).is_dir()

    basekey = m.infer_eval_basekey("taskabc", 0)
    assert basekey == "taskabc_0"
    sub = m.infer_shard_basename(basekey, 2)
    samples = [
        {"solution": [[0, 1], [2, 3]], "beam_score": 1.5, "score_aug": [0.1]},
        {"solution": [[1, 0]], "beam_score": 2.0, "score_aug": [0.2, 0.3]},
    ]
    shard_path = Path(infer_out) / sub
    m.infer_save_decoded_result_shard(str(shard_path), samples)

    loaded = m.infer_load_decoded_results_from_dir(infer_out, run_name="")
    assert basekey in loaded
    inner = loaded[basekey]
    assert len(inner) == 2
    assert f"{sub}.out0" in inner
    assert inner[f"{sub}.out0"]["beam_score"] == 1.5

    m.infer_save_intermediate_candidates(
        str(Path(inter_dir) / f"{basekey}.json"),
        {"basekey": basekey, "candidates": [{"aug_key": "aug_0"}]},
    )
    mid = json.loads((Path(inter_dir) / f"{basekey}.json").read_text(encoding="utf-8"))
    assert mid["basekey"] == basekey

    fin = m.infer_finalize_artifact_root(root, run_name="")
    assert Path(fin["decoded_store_pkl"]).is_file()
    assert Path(fin["manifest_json"]).is_file()
