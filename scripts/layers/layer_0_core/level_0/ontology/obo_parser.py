"""Generic OBO file parsing for Gene Ontology and similar ontologies.

Uses obonet when available for robust parsing; falls back to manual parsing
when obonet is not installed (optional dependency).
"""

from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, Tuple


def parse_obo_file(obo_path: Path) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """
    Parse OBO file into parents and children maps.

    Handles is_a and relationship: part_of. Tries obonet if available,
    falls back to manual parsing.

    Args:
        obo_path: Path to .obo file (e.g., go-basic.obo)

    Returns:
        Tuple of (parents_map, children_map) where:
        - parents_map: term_id -> set of parent term_ids
        - children_map: term_id -> set of child term_ids

    Raises:
        FileNotFoundError: If obo_path does not exist
    """
    if not obo_path.exists():
        raise FileNotFoundError(f"OBO file not found: {obo_path}")

    try:
        import obonet
        graph = obonet.read_obo(str(obo_path))
        parents_map: Dict[str, Set[str]] = defaultdict(set)
        children_map: Dict[str, Set[str]] = defaultdict(set)
        for term_id in graph.nodes():
            for parent_id in graph.predecessors(term_id):
                parents_map[term_id].add(parent_id)
                children_map[parent_id].add(term_id)
        return dict(parents_map), dict(children_map)
    except ImportError:
        pass

    return _parse_obo_manual(obo_path)


def _parse_obo_manual(obo_path: Path) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """Manual OBO parsing fallback (no obonet dependency)."""
    parents_map: Dict[str, Set[str]] = defaultdict(set)
    children_map: Dict[str, Set[str]] = defaultdict(set)
    cur_id: str | None = None

    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                cur_id = None
            elif line.startswith("id: "):
                cur_id = line.split("id: ")[1].strip()
            elif line.startswith("is_a: "):
                parts = line.split()
                if len(parts) >= 2 and cur_id:
                    parent_id = parts[1].strip()
                    parents_map[cur_id].add(parent_id)
                    children_map[parent_id].add(cur_id)
            elif line.startswith("relationship: part_of "):
                parts = line.split()
                if len(parts) >= 3 and cur_id:
                    parent_id = parts[2].strip()
                    parents_map[cur_id].add(parent_id)
                    children_map[parent_id].add(cur_id)

    return dict(parents_map), dict(children_map)
