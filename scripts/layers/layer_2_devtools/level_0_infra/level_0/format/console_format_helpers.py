"""Console-oriented list and section formatting helpers."""

from typing import Any, Callable, List


class FormattingHelpers:
    """Static helpers for health report sections."""

    @staticmethod
    def format_list_with_truncation(
        items: List[Any],
        formatter: Callable[[Any], str],
        max_items: int = 15,
        item_name: str = "items",
    ) -> List[str]:
        lines: list[str] = []
        if items:
            lines.append(f"{item_name.capitalize()} ({len(items)} total):")
            for item in items[:max_items]:
                lines.append(f"  {formatter(item)}")
            if len(items) > max_items:
                lines.append(f"  ... and {len(items) - max_items} more")
        return lines

    @staticmethod
    def format_section_header(title: str, emoji: str = "") -> List[str]:
        header = f"{emoji} {title}" if emoji else title
        return [header, "-" * 80]

    @staticmethod
    def format_success_message(message: str) -> str:
        return f"✓ {message}"