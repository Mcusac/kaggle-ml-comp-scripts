"""Argument parsing utilities for CLI."""

from typing import Any, List, Optional, Dict


def get_arg(args: Any, key: str, default: Any = None) -> Any:
    """
    Get argument value from parsed args with optional default.

    Args:
        args: Parsed argparse.Namespace or object with attribute access.
        key: Argument name (e.g. 'model_path', 'batch_size').
        default: Default value if attribute is missing or None.

    Returns:
        Argument value or default.
    """
    val = getattr(args, key, None)
    return default if val is None else val


def parse_comma_separated(value: Optional[str]) -> Optional[List[str]]:
    """
    Parse comma-separated string into list of stripped non-empty strings.

    Returns None if input is None, preserving the distinction between
    "no argument provided" and "empty argument provided".

    Args:
        value: Comma-separated string or None.

    Returns:
        List of stripped non-empty strings, or None if input is None.
        Returns empty list if input is empty string after stripping.
    """
    if value is None:
        return None
    return [item.strip() for item in value.split(',') if item.strip()]


def comma_separated_type(value: str) -> List[str]:
    """
    Argparse type for comma-separated lists.
    
    Use with argparse to automatically parse comma-separated arguments.
    
    Args:
        value: Comma-separated string
        
    Returns:
        List of stripped non-empty strings
        
    Example:
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument('--items', type=comma_separated_type)
        >>> args = parser.parse_args(['--items', 'a,b,c'])
        >>> args.items
        ['a', 'b', 'c']
    """
    return parse_comma_separated(value) or []


def parse_key_value_pairs(
    value: Optional[str],
    pair_sep: str = ',',
    kv_sep: str = '='
) -> Optional[Dict[str, str]]:
    """
    Parse key=value pairs into dictionary.
    
    Args:
        value: String with key=value pairs
        pair_sep: Separator between pairs (default: ',')
        kv_sep: Separator between key and value (default: '=')
        
    Returns:
        Dictionary or None if input is None
        
    Example:
        >>> parse_key_value_pairs("lr=0.01,batch=32")
        {'lr': '0.01', 'batch': '32'}
    """
    if value is None:
        return None
        
    result = {}
    pairs = [p.strip() for p in value.split(pair_sep) if p.strip()]
    
    for pair in pairs:
        if kv_sep not in pair:
            raise ValueError(f"Invalid key-value pair: '{pair}' (missing '{kv_sep}')")
        
        key, val = pair.split(kv_sep, 1)
        result[key.strip()] = val.strip()
    
    return result