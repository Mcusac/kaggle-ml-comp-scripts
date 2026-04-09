"""Lightweight ARC component benchmark for strategy/runtime comparison."""

import json
import sys
import time
import types
import importlib.util

from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parents[4]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

try:
    import torchvision.transforms  # type: ignore
except Exception:
    tv = types.ModuleType("torchvision")
    transforms = types.ModuleType("torchvision.transforms")
    transforms.Compose = lambda x: x
    transforms.Normalize = lambda *a, **k: ("Normalize", a, k)
    transforms.Resize = lambda *a, **k: ("Resize", a, k)
    transforms.ToTensor = lambda *a, **k: ("ToTensor", a, k)
    tv.transforms = transforms
    sys.modules["torchvision"] = tv
    sys.modules["torchvision.transforms"] = transforms


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    level1 = (
        _SCRIPTS_ROOT
        / "layers"
        / "layer_1_competition"
        / "level_1_impl"
        / "level_arc_agi_2"
        / "level_1"
    )
    aug = _load_module("arc_aug_bench", level1 / "augmentations.py")
    dec = _load_module("arc_dec_bench", level1 / "decoder_dfs.py")
    score = _load_module("arc_score_bench", level1 / "candidate_scoring.py")

    input_grid = [[1, 0], [0, 1]]
    expected = [[1, 1], [1, 1]]
    support = [expected]

    t0 = time.perf_counter()
    baseline = [row[:] for row in input_grid]
    baseline_sec = float(time.perf_counter() - t0)

    t1 = time.perf_counter()
    specs = aug.generate_augmentation_specs(8, seed=42, include_identity=True)
    preds = []
    for i, spec in enumerate(specs):
        transformed_support = [aug.apply_augmentation(g, spec) for g in support]
        h = len(transformed_support[0])
        w = len(transformed_support[0][0])
        probs = []
        for r in range(h):
            row = []
            for c in range(w):
                counts = [1e-3] * 10
                for g in transformed_support:
                    counts[int(g[r][c]) % 10] += 1.0
                total = sum(counts)
                row.append([v / total for v in counts])
            probs.append(row)
        decoded = dec.decode_grid_candidates(probs, beam_width=12, max_candidates=6, max_neg_log_score=120.0)
        for cand in decoded:
            preds.append(
                score.CandidatePrediction(
                    grid=aug.invert_augmentation(cand.grid, spec),
                    model_score=float(cand.score),
                    aug_key=f"aug_{i}",
                    aug_likelihood_score=0.0,
                )
            )
    ranked = score.rank_candidate_grids(preds, consistency_weight=1.0, model_weight=1.0)
    surrogate = ranked[0].grid if ranked else baseline
    surrogate_sec = float(time.perf_counter() - t1)

    report = {
        "baseline_time_sec": baseline_sec,
        "surrogate_time_sec": surrogate_sec,
        "runtime_delta_sec": surrogate_sec - baseline_sec,
        "baseline_match_expected": baseline == expected,
        "surrogate_match_expected": surrogate == expected,
        "baseline_attempt_1": baseline,
        "surrogate_attempt_1": surrogate,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
