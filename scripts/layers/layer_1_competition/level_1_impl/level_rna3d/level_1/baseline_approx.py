"""RNA3D baseline approximation submission pipeline.

This is a lightweight, reproducible baseline that:
- selects similar training sequences via global alignment
- adapts template coordinates onto the query via alignment mapping
- fills gaps via interpolation
- outputs 5 predicted structures per sequence (template-based + fallbacks)

It is designed to be invoked via the framework runner (`scripts/run.py`) so
notebooks stay lean and configurable.
"""

import numpy as np
import pandas as pd

from Bio import pairwise2
from Bio.Seq import Seq as BioSeq
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from layers.layer_0_core.level_0 import get_logger, ensure_dir

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import (
    build_coordinate_columns,
    group_labels_by_target,
    RNA3DPaths,
    RNA3DPostProcessor,
)
from layers.layer_1_competition.level_0_infra.level_1.paths import contest_submission_path

_logger = get_logger(__name__)


@dataclass(frozen=True)
class BaselineApproxConfig:
    """Tunable parameters for the baseline approximation predictor."""

    n_structures: int = 5
    template_top_n: int = 5
    template_pool: int = 80
    rel_len_cap: float = 0.30

    aln_match: int = 2
    aln_mismatch: int = -1
    aln_gap_open: float = -8.0
    aln_gap_ext: float = -0.2

    noise_gain: float = 0.25
    noise_floor: float = 0.02

    seed: int = 42
    max_targets: int = 0  # smoke: 0 means all


@dataclass(frozen=True)
class Template:
    target_id: str
    sequence: str
    coords: np.ndarray  # (L, 3)


def group_labels_to_coords(labels_df: pd.DataFrame) -> dict[str, np.ndarray]:
    """
    Build target_id -> coords mapping from train_labels.csv.

    Uses the first experimental conformation: x_1,y_1,z_1.
    """
    if labels_df.empty:
        return {}

    required = {"x_1", "y_1", "z_1"}
    missing = sorted(required - set(labels_df.columns))
    if missing:
        raise ValueError(f"train_labels.csv missing required columns: {missing}")

    groups = group_labels_by_target(labels_df)
    out: dict[str, np.ndarray] = {}
    for target_id, g in groups.items():
        coords = g[["x_1", "y_1", "z_1"]].to_numpy(dtype=np.float32, copy=True)
        out[target_id] = coords

    return out


def build_templates(
    train_seqs: pd.DataFrame,
    coords_by_target: dict[str, np.ndarray],
) -> List[Template]:
    """Build Template list from train sequences and coordinate mapping."""
    templates: List[Template] = []
    for row in train_seqs.itertuples(index=False):
        tid = str(row.target_id)
        seq = str(row.sequence)
        coords = coords_by_target.get(tid)
        if coords is None:
            continue
        if coords.shape[0] != len(seq):
            m = min(coords.shape[0], len(seq))
            coords = coords[:m]
            seq = seq[:m]
        if coords.shape[0] == 0:
            continue
        templates.append(Template(target_id=tid, sequence=seq, coords=coords))
    return templates


def _normalized_similarity(
    query: str,
    template: str,
    match: int,
    mismatch: int,
    gap_open: float,
    gap_ext: float,
) -> float:
    aln = pairwise2.align.globalms(
        BioSeq(query),
        BioSeq(template),
        match,
        mismatch,
        gap_open,
        gap_ext,
        one_alignment_only=True,
    )
    if not aln:
        return 0.0
    denom = float(max(1, match * min(len(query), len(template))))
    return float(aln[0].score) / denom


def _adapt_template_to_query(
    query: str,
    template: str,
    template_coords: np.ndarray,
    match: int,
    mismatch: int,
    gap_open: float,
    gap_ext: float,
) -> np.ndarray:
    """Map template coords onto query positions using global alignment."""
    aln = pairwise2.align.globalms(
        BioSeq(query),
        BioSeq(template),
        match,
        mismatch,
        gap_open,
        gap_ext,
        one_alignment_only=True,
    )
    if not aln:
        return np.zeros((len(query), 3), dtype=np.float32)

    aligned_q = aln[0].seqA
    aligned_t = aln[0].seqB

    new_coords = np.full((len(query), 3), np.nan, dtype=np.float32)
    q_i = 0
    t_i = 0

    for cq, ct in zip(aligned_q, aligned_t):
        if cq != "-" and ct != "-":
            if t_i < template_coords.shape[0]:
                new_coords[q_i] = template_coords[t_i]
            q_i += 1
            t_i += 1
        elif cq != "-":
            q_i += 1
        elif ct != "-":
            t_i += 1

    # Fill NaNs by interpolation or simple extrapolation
    n = new_coords.shape[0]
    for i in range(n):
        if np.isfinite(new_coords[i]).all():
            continue
        prev_i = i - 1
        while prev_i >= 0 and not np.isfinite(new_coords[prev_i]).all():
            prev_i -= 1
        next_i = i + 1
        while next_i < n and not np.isfinite(new_coords[next_i]).all():
            next_i += 1

        if prev_i >= 0 and next_i < n:
            w = float(i - prev_i) / float(next_i - prev_i)
            new_coords[i] = (1.0 - w) * new_coords[prev_i] + w * new_coords[next_i]
        elif prev_i >= 0:
            new_coords[i] = new_coords[prev_i] + np.array([3.0, 0.0, 0.0], dtype=np.float32)
        elif next_i < n:
            new_coords[i] = new_coords[next_i] + np.array([-3.0, 0.0, 0.0], dtype=np.float32)
        else:
            new_coords[i] = np.array([3.0 * i, 0.0, 0.0], dtype=np.float32)

    return np.nan_to_num(new_coords, copy=False)


def _apply_backbone_constraints(coords: np.ndarray, target_dist: float = 6.0) -> np.ndarray:
    """Light constraint to keep consecutive distances roughly consistent."""
    if coords.shape[0] < 2:
        return coords

    out = coords.astype(np.float32, copy=True)
    min_d = 5.5
    max_d = 6.5
    strength = 0.12

    for i in range(out.shape[0] - 1):
        dvec = out[i + 1] - out[i]
        dist = float(np.linalg.norm(dvec) + 1e-8)
        if dist < min_d or dist > max_d:
            direction = dvec / dist
            out[i + 1] = out[i + 1] + direction * float((target_dist - dist) * strength)

    return out


def _fallback_structure(seq_len: int, rng: np.random.Generator) -> np.ndarray:
    """Simple fallback: noisy straight-chain walk."""
    if seq_len <= 0:
        return np.zeros((0, 3), dtype=np.float32)
    coords = np.zeros((seq_len, 3), dtype=np.float32)
    step = 4.0
    for i in range(1, seq_len):
        jitter = rng.normal(0.0, 0.15, size=(3,)).astype(np.float32)
        coords[i] = coords[i - 1] + np.array([step, 0.0, 0.0], dtype=np.float32) + jitter
    return coords


class BaselineApproxPredictor:
    """Predictor that adapts training templates onto test sequences."""

    def __init__(self, templates: Sequence[Template], config: BaselineApproxConfig):
        self._templates = list(templates)
        self._cfg = config
        self._rng = np.random.default_rng(int(config.seed))

    def predict(self, sequence: str) -> List[np.ndarray]:
        """Return a list of predicted structures, each (L,3)."""
        seq = str(sequence)
        n = len(seq)

        if not self._templates:
            return [_fallback_structure(n, self._rng) for _ in range(self._cfg.n_structures)]

        pool_size = min(self._cfg.template_pool, len(self._templates))
        pool_idx = self._rng.choice(len(self._templates), size=pool_size, replace=False)

        scored: List[Tuple[float, Template]] = []
        for idx in pool_idx:
            t = self._templates[int(idx)]
            if not t.sequence:
                continue
            if abs(len(t.sequence) - n) / float(max(len(t.sequence), n, 1)) > self._cfg.rel_len_cap:
                continue
            sim = _normalized_similarity(
                query=seq,
                template=t.sequence,
                match=self._cfg.aln_match,
                mismatch=self._cfg.aln_mismatch,
                gap_open=self._cfg.aln_gap_open,
                gap_ext=self._cfg.aln_gap_ext,
            )
            scored.append((sim, t))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[: max(1, self._cfg.template_top_n)]

        preds: List[np.ndarray] = []
        for sim, t in top:
            adapted = _adapt_template_to_query(
                query=seq,
                template=t.sequence,
                template_coords=t.coords,
                match=self._cfg.aln_match,
                mismatch=self._cfg.aln_mismatch,
                gap_open=self._cfg.aln_gap_open,
                gap_ext=self._cfg.aln_gap_ext,
            )
            refined = _apply_backbone_constraints(adapted)
            noise_scale = max(self._cfg.noise_floor, (0.5 - float(sim)) * self._cfg.noise_gain)
            refined = refined + self._rng.normal(0.0, noise_scale, size=refined.shape).astype(np.float32)
            preds.append(refined.astype(np.float32, copy=False))

            if len(preds) >= self._cfg.n_structures:
                break

        while len(preds) < self._cfg.n_structures:
            preds.append(_fallback_structure(n, self._rng))

        return preds


def run_baseline_approx_predictions(
    data_root: str,
    config: BaselineApproxConfig,
    sequences_df: pd.DataFrame,
    max_targets: int = 0,
) -> Dict[str, np.ndarray]:
    """Generate predictions for sequences using baseline_approx.

    Shared logic used by submission, tuning, and make_submission pipelines.

    Args:
        data_root: Directory containing train_sequences.csv and train_labels.csv.
        config: BaselineApproxConfig.
        sequences_df: DataFrame with target_id and sequence columns.
        max_targets: If >0, only process first N targets.

    Returns:
        Dict mapping target_id -> prediction array (L, n_structures, 3).
    """
    root = Path(data_root)
    train_sequences_path = root / "train_sequences.csv"
    train_labels_path = root / "train_labels.csv"

    train_seqs = pd.read_csv(train_sequences_path, usecols=["target_id", "sequence"])
    train_labels = pd.read_csv(train_labels_path)

    coords_by_target = group_labels_to_coords(train_labels)
    templates = build_templates(train_seqs, coords_by_target)
    predictor = BaselineApproxPredictor(templates=templates, config=config)

    if max_targets and max_targets > 0:
        sequences_df = sequences_df.head(int(max_targets))

    predictions: Dict[str, np.ndarray] = {}
    for row in sequences_df.itertuples(index=False):
        target_id = str(row.target_id)
        seq = str(row.sequence)
        preds = predictor.predict(seq)
        pred_array = np.stack(preds, axis=1).astype(np.float32)
        predictions[target_id] = pred_array

    return predictions


def format_predictions_to_submission_csv(
    predictions: Dict[str, np.ndarray],
    sequences_df: pd.DataFrame,
    n_structures: int,
    output_csv: Optional[str] = None,
) -> Path:
    """Format prediction dict into submission CSV."""
    coord_cols = build_coordinate_columns(n_structures=n_structures)
    rows: List[dict] = []

    for row in sequences_df.itertuples(index=False):
        target_id = str(row.target_id)
        seq = str(row.sequence)

        if target_id not in predictions:
            pred_array = np.zeros((len(seq), n_structures, 3), dtype=np.float32)
        else:
            pred_array = predictions[target_id]

        for i, resname in enumerate(seq):
            rec: dict = {"ID": f"{target_id}_{i+1}", "resname": resname, "resid": i + 1}
            for k in range(1, n_structures + 1):
                if i < pred_array.shape[0] and (k - 1) < pred_array.shape[1]:
                    rec[f"x_{k}"] = float(pred_array[i, k - 1, 0])
                    rec[f"y_{k}"] = float(pred_array[i, k - 1, 1])
                    rec[f"z_{k}"] = float(pred_array[i, k - 1, 2])
                else:
                    rec[f"x_{k}"] = 0.0
                    rec[f"y_{k}"] = 0.0
                    rec[f"z_{k}"] = 0.0
            rows.append(rec)

    df = pd.DataFrame(rows)
    df = df[["ID", "resname", "resid", *coord_cols]]

    post = RNA3DPostProcessor()
    df[coord_cols] = post.apply(df[coord_cols].to_numpy(dtype=np.float32)).astype(np.float32)

    if output_csv:
        out_path = Path(output_csv)
    else:
        out_path = contest_submission_path(RNA3DPaths(), "submission.csv")
    ensure_dir(out_path.parent)
    df.to_csv(out_path, index=False)

    return out_path


def make_submission(
    data_root: str,
    config: BaselineApproxConfig,
    output_csv: Optional[str] = None,
) -> Path:
    """
    Generate RNA3D submission.csv using the baseline approximation pipeline.

    Args:
        data_root: Directory containing competition data CSVs.
        config: BaselineApproxConfig.
        output_csv: Optional explicit output path.

    Returns:
        Path to written submission CSV.
    """
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    train_sequences_path = root / "train_sequences.csv"
    train_labels_path = root / "train_labels.csv"
    test_sequences_path = root / "test_sequences.csv"
    for p in (train_sequences_path, train_labels_path, test_sequences_path):
        if not p.exists():
            raise FileNotFoundError(f"Missing required input file: {p}")

    test_seqs = pd.read_csv(test_sequences_path, usecols=["target_id", "sequence"])

    _logger.info("RNA3D submission generation started")
    predictions = run_baseline_approx_predictions(
        data_root=data_root,
        config=config,
        sequences_df=test_seqs,
        max_targets=config.max_targets or 0,
    )
    _logger.info("   Test targets: %d", len(predictions))

    n_structures = int(config.n_structures)
    if predictions:
        first_pred = next(iter(predictions.values()))
        n_structures = first_pred.shape[1]

    out_path = format_predictions_to_submission_csv(
        predictions=predictions,
        sequences_df=test_seqs,
        n_structures=n_structures,
        output_csv=output_csv,
    )
    _logger.info("Wrote submission: %s", out_path)
    return out_path
