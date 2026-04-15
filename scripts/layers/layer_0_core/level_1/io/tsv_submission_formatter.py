"""Generic TSV submission formatting, sorting, and limit enforcement."""

import heapq
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Callable, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


class TsvSubmissionFormatter:
    """
    Generic TSV submission formatter: parse, sort, enforce limits.

    Subclasses or callers provide parse logic via parse_line.
    Default parse expects: col0, col1, score (tab-separated).
    """

    def __init__(
        self,
        parse_line: Optional[Callable[[str], Optional[Tuple[str, str, float, str]]]] = None,
        score_min: float = 0.0,
        score_max: float = 1.0,
    ):
        """
        Args:
            parse_line: Optional custom parser. Default expects (id, term, score, line).
            score_min: Minimum valid score (inclusive)
            score_max: Maximum valid score (inclusive)
        """
        self._score_min = score_min
        self._score_max = score_max
        self._parse_line = parse_line or self._default_parse_line

    def _default_parse_line(self, line: str) -> Optional[Tuple[str, str, float, str]]:
        """Parse tab-separated: id, term, score."""
        line = line.strip()
        if not line:
            return None
        parts = line.split("\t")
        if len(parts) >= 3:
            try:
                col0, col1, score = parts[0], parts[1], float(parts[2])
                if self._score_min < score <= self._score_max:
                    return (col0, col1, score, line)
            except (ValueError, IndexError):
                pass
        return None

    def parse_submission_line(self, line: str) -> Optional[Tuple[str, str, float, str]]:
        """Parse a single submission line."""
        return self._parse_line(line)

    def try_system_sort(self, input_path: Path, output_path: Path) -> bool:
        """Try system sort (Unix only). Returns True if succeeded."""
        if sys.platform == "win32":
            return False
        try:
            temp_dir = tempfile.gettempdir()
            with open(output_path, "w", encoding="utf-8") as out:
                subprocess.run(
                    ["sort", "-t", "\t", "-k1,2", "-T", temp_dir, str(input_path)],
                    stdout=out,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                )
            logger.info(f"Sorted using system sort: {output_path}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False

    def sort_submission_external(
        self,
        input_path: str | Path,
        output_path: str | Path,
        chunk_size: int = 1_000_000,
    ) -> None:
        """Sort TSV by first two columns. Uses system sort or chunked merge."""
        input_path = Path(input_path)
        output_path = Path(output_path)
        if self.try_system_sort(input_path, output_path):
            return
        chunk_files = self._read_and_sort_chunks(input_path, chunk_size)
        self._merge_sorted_chunks(chunk_files, output_path)
        logger.info(f"External sort complete: {output_path}")

    def _read_and_sort_chunks(
        self, input_path: Path, chunk_size: int
    ) -> list[str]:
        """Read, sort in chunks, return temp file paths."""
        chunk_files = []
        chunk = []
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = self.parse_submission_line(line)
                if parsed:
                    chunk.append(parsed)
                if len(chunk) >= chunk_size:
                    chunk.sort(key=lambda x: (x[0], x[1]))
                    tf = tempfile.NamedTemporaryFile(
                        mode="w", delete=False, suffix=".tsv", encoding="utf-8"
                    )
                    for _, _, _, orig in chunk:
                        tf.write(orig + "\n")
                    tf.close()
                    chunk_files.append(tf.name)
                    chunk = []
            if chunk:
                chunk.sort(key=lambda x: (x[0], x[1]))
                tf = tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".tsv", encoding="utf-8"
                )
                for _, _, _, orig in chunk:
                    tf.write(orig + "\n")
                tf.close()
                chunk_files.append(tf.name)
        return chunk_files

    def _merge_sorted_chunks(
        self, chunk_files: list[str], output_path: Path
    ) -> None:
        """Merge sorted chunks with heap."""
        with open(output_path, "w", encoding="utf-8") as out_file:
            handles = [open(f, "r", encoding="utf-8") for f in chunk_files]
            iters = [iter(h) for h in handles]
            heap = []
            for i, it in enumerate(iters):
                try:
                    line = next(it).strip()
                    if line:
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            heap.append((parts[0], parts[1], i, line))
                except StopIteration:
                    pass
            heapq.heapify(heap)
            while heap:
                _, _, idx, line = heapq.heappop(heap)
                out_file.write(line + "\n")
                try:
                    next_line = next(iters[idx]).strip()
                    if next_line:
                        parts = next_line.split("\t")
                        if len(parts) >= 2:
                            heapq.heappush(
                                heap, (parts[0], parts[1], idx, next_line)
                            )
                except StopIteration:
                    pass
            for h in handles:
                h.close()
        for f in chunk_files:
            try:
                Path(f).unlink()
            except Exception:
                pass

    def enforce_prediction_limits(
        self,
        submission_path: str | Path,
        max_predictions_per_id: int = 1500,
        output_path: Optional[str | Path] = None,
    ) -> str:
        """
        Keep top-K predictions per first column (e.g. protein_id).

        Returns:
            Path to output file.
        """
        submission_path = Path(submission_path)
        output_path = output_path or str(submission_path.with_suffix("")) + "_limited.tsv"
        output_path = Path(output_path)
        id_predictions: dict[str, list[Tuple[float, str]]] = defaultdict(list)
        with open(submission_path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = self.parse_submission_line(line)
                if parsed:
                    id_val, term, score, _ = parsed
                    if len(id_predictions[id_val]) < max_predictions_per_id:
                        heapq.heappush(id_predictions[id_val], (score, term))
                    else:
                        min_score, _ = id_predictions[id_val][0]
                        if score > min_score:
                            heapq.heapreplace(id_predictions[id_val], (score, term))
        final_count = 0
        with open(output_path, "w", encoding="utf-8") as out:
            for id_val, preds in id_predictions.items():
                for score, term in sorted(preds, reverse=True):
                    out.write(f"{id_val}\t{term}\t{score:.6f}\n")
                    final_count += 1
        logger.info(f"Enforced limit: {final_count:,} predictions")
        return str(output_path)
