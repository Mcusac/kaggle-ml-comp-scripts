"""Embedding type normalization via alias resolution."""

from typing import Dict, Optional


def normalize_embedding_type(
    embedding_type: str, aliases: Optional[Dict[str, str]] = None
) -> str:
    """
    Normalize embedding type using optional alias mapping.

    Args:
        embedding_type: Raw embedding type
        aliases: Optional dict of alias -> canonical (e.g. {'esm2': 'esm2_650m'})
    """
    if aliases and embedding_type in aliases:
        return aliases[embedding_type]
    return embedding_type
