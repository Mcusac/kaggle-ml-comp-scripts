"""CAFA-specific path resolution and embedding path layout."""

from pathlib import Path
from typing import Optional

from layers.layer_0_core.level_0 import (
    get_logger,
    is_kaggle_input,
    normalize_embedding_type,
    resolve_embedding_base_path,
)

EMBEDDING_TYPE_ALIASES = {"esm2": "esm2_650m"}

logger = get_logger(__name__)


def get_embedding_paths() -> tuple[dict, Path]:
    """
    Get CAFA embedding paths based on environment (Kaggle vs local).

    Returns:
        Tuple of (embedding_paths dict, cafa6_embeddings_dir Path).
    """
    is_kaggle = is_kaggle_input("/kaggle/input")

    if is_kaggle:
        cafa6_embeddings_dir = Path("/kaggle/input/cafa-6-embeddings")
        embeddings_dir = Path("/kaggle/input")
    else:
        current_dir = Path.cwd()
        if current_dir.name == "working" and (current_dir.parent / "input").exists():
            project_root = current_dir.parent.parent
        else:
            project_root = current_dir

        cafa6_embeddings_dir = project_root / "kaggle" / "input" / "cafa-6-embeddings"
        embeddings_dir = project_root / "kaggle" / "input"

    embedding_paths = {
        "esm2_15b": cafa6_embeddings_dir / "esm2_15B",
        "esm2_3b": cafa6_embeddings_dir / "esm2_3B",
        "esm2_650m": cafa6_embeddings_dir / "esm2_650M",
        "esm1b_650m": cafa6_embeddings_dir / "esm1b_650M",
        "ankh_large": cafa6_embeddings_dir / "ankh_large",
        "ankh3_large": cafa6_embeddings_dir / "ankh3_large",
        "protbert": cafa6_embeddings_dir / "protBERT",
        "prot_t5_xl": cafa6_embeddings_dir / "protT5_xl",
        "esm2": embeddings_dir / "CAFA 5 EMS-2 Embeddings Numpy"
        if not is_kaggle
        else Path("/kaggle/input/cafa-5-ems-2-embeddings-numpy"),
        "t5": embeddings_dir / "CAFA5 supplementary calcs for ML"
        if not is_kaggle
        else Path("/kaggle/input/cafa5-supp-pre-calcs-for-ml"),
    }

    return embedding_paths, cafa6_embeddings_dir


def resolve_base_path(embedding_type: str, base_path: Optional[Path]) -> Path:
    """Resolve base path for embeddings."""
    embedding_paths, _ = get_embedding_paths()
    return resolve_embedding_base_path(embedding_type, base_path, embedding_paths)


def resolve_embedding_paths(
    embedding_type: str,
    datatype: str,
    base_path: Path,
    cafa6_embeddings_dir: Path,
) -> tuple[Path, Path, list]:
    """
    Resolve embedding file paths for different embedding structures.

    Returns:
        Tuple of (ids_path, embeddings_path, checked_paths_list).
    """
    new_structure_embeddings = [
        "esm2_15b",
        "esm2_3b",
        "esm2_650m",
        "esm1b_650m",
        "ankh_large",
        "ankh3_large",
        "protbert",
        "prot_t5_xl",
    ]

    if embedding_type in new_structure_embeddings:
        return _resolve_new_structure_paths(
            datatype, base_path, cafa6_embeddings_dir
        )
    raise ValueError(
        f"Unsupported embedding_type '{embedding_type}' for path resolution. "
        f"Supported: {new_structure_embeddings}"
    )


def normalize_embedding_type_cafa(embedding_type: str) -> str:
    """Normalize embedding type for CAFA (convert legacy names)."""
    return normalize_embedding_type(embedding_type, aliases=EMBEDDING_TYPE_ALIASES)


def _resolve_new_structure_paths(
    datatype: str,
    base_path: Path,
    cafa6_embeddings_dir: Path,
) -> tuple[Path, Path, list]:
    """Resolve paths for new consolidated embedding structure."""
    checked_paths = []

    new_ids_path, new_embeddings_path = _get_new_structure_paths(
        datatype, base_path, cafa6_embeddings_dir
    )
    checked_paths.append(("new_structure", new_ids_path, new_embeddings_path))
    if new_embeddings_path.exists() and new_ids_path.exists():
        return new_ids_path, new_embeddings_path, checked_paths

    sequences_ids_path, sequences_embeddings_path = _get_sequences_emb_paths(
        datatype, base_path
    )
    checked_paths.append(
        ("train_sequences_emb", sequences_ids_path, sequences_embeddings_path)
    )
    if sequences_embeddings_path.exists() and sequences_ids_path.exists():
        return sequences_ids_path, sequences_embeddings_path, checked_paths

    return _resolve_legacy_structure_paths(datatype, base_path)


def _resolve_legacy_structure_paths(
    datatype: str, base_path: Path
) -> tuple[Path, Path, list]:
    """Resolve paths for legacy structure."""
    legacy_ids_path, legacy_embeddings_path = _get_legacy_paths(
        datatype, base_path
    )
    checked_paths = [("legacy", legacy_ids_path, legacy_embeddings_path)]
    return legacy_ids_path, legacy_embeddings_path, checked_paths


def _get_legacy_paths(datatype: str, base_path: Path) -> tuple[Path, Path]:
    """Get paths for legacy structure."""
    ids_path = base_path / f"{datatype}_ids.npy"
    embeddings_path = base_path / f"{datatype}_embeddings.npy"
    return ids_path, embeddings_path


def _get_new_structure_paths(
    datatype: str, base_path: Path, cafa6_embeddings_dir: Path
) -> tuple[Path, Path]:
    """Get paths for new structure with shared ID files."""
    if datatype == "train":
        ids_path = cafa6_embeddings_dir / "train_sequences_ids.npy"
        embeddings_path = base_path / "train.npy"
    else:
        ids_path = cafa6_embeddings_dir / "testsuperset_ids.npy"
        embeddings_path = base_path / "test.npy"
    return ids_path, embeddings_path


def _get_sequences_emb_paths(datatype: str, base_path: Path) -> tuple[Path, Path]:
    """Get paths for train_sequences_emb pattern."""
    if datatype == "train":
        ids_path = base_path / "train_sequences_ids.npy"
        embeddings_path = base_path / "train_sequences_emb.npy"
    else:
        ids_path = base_path / "testsuperset_ids.npy"
        embeddings_path = base_path / "testsuperset_emb.npy"
    return ids_path, embeddings_path