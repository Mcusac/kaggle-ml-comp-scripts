from pathlib import Path


def test_lines_oversized_modules_empty() -> None:
    from layers.layer_2_devtools.level_0_infra.level_0.formatting.health_report_views import (
        lines_oversized_modules,
    )

    lines = lines_oversized_modules(
        {"file_metrics": {"long_files": []}},
        report_path=Path("health_report.json"),
        max_file_lines=500,
        top=50,
        include_suggestions=True,
    )
    joined = "\n".join(lines)
    assert "OVERSIZED MODULES" in joined
    assert "Oversized modules: 0" in joined
    assert "No oversized modules detected" in joined


def test_lines_oversized_modules_with_suggestions() -> None:
    from layers.layer_2_devtools.level_0_infra.level_0.formatting.health_report_views import (
        lines_oversized_modules,
    )

    report = {
        "file_metrics": {
            "long_files": [
                {"module": "pkg.big", "lines": 900},
                {"module": "pkg.ok", "lines": 120},
            ],
            "long_functions": [
                {"module": "pkg.big", "function": "very_long", "lines": 140},
                {"module": "pkg.big", "function": "also_long", "lines": 95},
            ],
            "large_classes": [
                {"module": "pkg.big", "class": "BigClass", "methods": 12},
            ],
        }
    }
    lines = lines_oversized_modules(
        report,
        report_path=Path("health_report.json"),
        max_file_lines=500,
        top=50,
        include_suggestions=True,
    )
    joined = "\n".join(lines)
    assert "pkg.big" in joined
    assert "Suggestion:" in joined
    assert "very_long" in joined
    assert "BigClass" in joined

