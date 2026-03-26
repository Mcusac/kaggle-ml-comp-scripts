"""Submission file format validation for TSV prediction files."""

import re
from pathlib import Path
from typing import List, Optional, Tuple


def is_valid_score(score: float) -> bool:
    """
    Check if score is in valid range for predictions.

    Args:
        score: Score to validate.

    Returns:
        True if score is in range (0, 1.0].
    """
    return 0 < score <= 1.0


def validate_go_term_format(term: str) -> Tuple[bool, Optional[str]]:
    """
    Validate GO term format (GO:XXXXXXX).

    Args:
        term: GO term string to validate.

    Returns:
        (is_valid, error_message). error_message is None when valid.
    """
    if not term.startswith("GO:"):
        return False, f"Invalid GO term format: {term} (must start with 'GO:')"

    if not re.match(r"^GO:\d{7}$", term):
        return False, f"Invalid GO term format: {term} (expected GO:XXXXXXX)"

    return True, None


def validate_submission_format(
    filepath: str,
    sample_size: int = 1000,
) -> Tuple[bool, List[str]]:
    """
    Validate submission file format.
    Memory-efficient: only reads sample lines, does not load entire file.

    Args:
        filepath: Path to submission file.
        sample_size: Number of lines to validate (default 1000).

    Returns:
        (is_valid, issues). issues is empty when valid.
    """
    issues: List[str] = []
    filepath = Path(filepath)

    if not filepath.exists():
        issues.append(f"File not found: {filepath}")
        return False, issues

    try:
        line_count = 0
        valid_predictions = 0

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                line_count += 1

                if line_count > sample_size:
                    break

                parts = line.split("\t")
                if len(parts) != 3:
                    issues.append(
                        f"Invalid format at line {line_num}: expected 3 tab-separated "
                        f"columns, got {len(parts)}"
                    )
                    return False, issues

                protein_id, term, score_str = parts

                is_valid_term, term_error = validate_go_term_format(term)
                if not is_valid_term:
                    issues.append(f"Invalid GO term at line {line_num}: {term_error}")
                    return False, issues

                try:
                    score = float(score_str)
                    if not is_valid_score(score):
                        issues.append(
                            f"Score out of range at line {line_num}: {score} "
                            "(expected 0 < score <= 1.0)"
                        )
                        return False, issues
                    valid_predictions += 1
                except ValueError:
                    issues.append(f"Invalid score format at line {line_num}: {score_str}")
                    return False, issues

        if line_count == 0:
            issues.append("File contains no predictions")
            return False, issues

        if valid_predictions == 0:
            issues.append("File contains no valid predictions")
            return False, issues

    except Exception as e:
        issues.append(f"Failed to read file: {e}")
        return False, issues

    return True, []
