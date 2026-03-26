"""
Base command builder for constructing subprocess command lists.
"""

from typing import List, Optional, Any


class BaseCommandBuilder:
    """
    Base class for building CLI subprocess commands.

    Provides helper utilities for safely adding arguments.
    """

    def __init__(self, base_executable: Optional[List[str]] = None):
        # Default: python run.py
        self._cmd: List[str] = base_executable or ["python", "run.py"]

    # ----------------------------
    # Core build interface
    # ----------------------------

    def build(self) -> List[str]:
        """
        Return a copy of the constructed command list.
        """
        return list(self._cmd)

    # ----------------------------
    # Argument helpers
    # ----------------------------

    def add_positional(self, value: Any) -> None:
        if value is None:
            return
        self._cmd.append(str(value))

    def add_flag(self, flag: str, condition: bool) -> None:
        """
        Add boolean flag if condition is True.
        Example: --verbose
        """
        if condition:
            self._cmd.append(flag)

    def add_option(self, flag: str, value: Optional[Any]) -> None:
        """
        Add flag + value pair if value is not None.
        Example: --fold 3
        """
        if value is None:
            return
        self._cmd.extend([flag, str(value)])

    def add_list_option(self, flag: str, values: Optional[List[Any]]) -> None:
        """
        Add repeated flag entries.
        Example: --model a --model b
        """
        if not values:
            return

        for v in values:
            self._cmd.extend([flag, str(v)])
