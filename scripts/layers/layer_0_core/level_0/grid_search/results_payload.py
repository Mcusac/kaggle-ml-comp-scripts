"""Normalize decoded JSON (or similar) into a list of result dicts. No I/O; depends on stdlib only."""

from typing import Any, Dict, List


def extract_results_list(data: Any) -> List[Dict]:
    """If data is a list, return it; if a dict, return data['results'] or []."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("results", [])
    return []
