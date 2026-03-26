"""Unit tests for infra pycache cleanup."""

from pathlib import Path

import pytest

from layers.layer_2_devtools.level_0_infra.level_0.fs.pycache_cleanup import (
    SKIP_DIRS,
    CleanResult,
    clean_pycache,
)


def test_clean_pycache_dry_run_leaves_dirs(tmp_path: Path) -> None:
    """Dry run reports counts and does not remove __pycache__ dirs."""
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "__pycache__").mkdir()
    result = clean_pycache(tmp_path, dry_run=True)
    assert result.dirs_removed == 2
    assert result.files_removed == 0
    assert (tmp_path / "__pycache__").is_dir()
    assert (tmp_path / "a" / "__pycache__").is_dir()


def test_clean_pycache_execute_removes_dirs(tmp_path: Path) -> None:
    """Execute removes __pycache__ dirs and returns counts."""
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "__pycache__").mkdir()
    result = clean_pycache(tmp_path, dry_run=False)
    assert result.dirs_removed == 2
    assert result.files_removed == 0
    assert not (tmp_path / "__pycache__").exists()
    assert not (tmp_path / "a" / "__pycache__").exists()


def test_clean_pycache_remove_pyc_files_dry_run(tmp_path: Path) -> None:
    """With remove_pyc_files, dry run counts loose .pyc files."""
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "foo.pyc").write_bytes(b"")
    result = clean_pycache(tmp_path, dry_run=True, remove_pyc_files=True)
    assert result.dirs_removed == 1
    assert result.files_removed == 1
    assert (tmp_path / "foo.pyc").is_file()


def test_clean_pycache_remove_pyc_files_execute(tmp_path: Path) -> None:
    """With remove_pyc_files, execute removes __pycache__ and loose .pyc."""
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "foo.pyc").write_bytes(b"")
    result = clean_pycache(tmp_path, dry_run=False, remove_pyc_files=True)
    assert result.dirs_removed == 1
    assert result.files_removed == 1
    assert not (tmp_path / "__pycache__").exists()
    assert not (tmp_path / "foo.pyc").exists()


def test_clean_pycache_non_directory_returns_zero(tmp_path: Path) -> None:
    """Non-directory root returns CleanResult with zero counts."""
    file_path = tmp_path / "notadir"
    file_path.touch()
    result = clean_pycache(file_path)
    assert result.dirs_removed == 0
    assert result.files_removed == 0


def test_clean_pycache_skips_git(tmp_path: Path) -> None:
    """__pycache__ inside .git is not removed (skip dir)."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "__pycache__").mkdir()
    result = clean_pycache(tmp_path, dry_run=False)
    assert result.dirs_removed == 0
    assert (tmp_path / ".git" / "__pycache__").is_dir()


def test_clean_result_attributes() -> None:
    """CleanResult has dirs_removed and files_removed."""
    r = CleanResult(dirs_removed=1, files_removed=2)
    assert r.dirs_removed == 1
    assert r.files_removed == 2


def test_skip_dirs_contains_git() -> None:
    """SKIP_DIRS includes .git."""
    assert ".git" in SKIP_DIRS
