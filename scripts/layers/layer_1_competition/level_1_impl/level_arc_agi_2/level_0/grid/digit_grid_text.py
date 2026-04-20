"""ARC grid to/from newline digit text (stdlib only; shared by LM formatters)."""

Grid = list[list[int]]
MAX_ARC_GRID_DIM = 30


def arc_grid_to_text_lines(grid: Grid) -> str:
    """Serialize grid rows as concatenated digits, newline-separated (no spaces)."""
    lines: list[str] = []
    for row in grid:
        lines.append("".join(str(int(cell)) for cell in row))
    return "\n".join(lines).strip()


def arc_is_valid_grid_shape(nrows: int, ncols: int) -> bool:
    return 0 < nrows <= MAX_ARC_GRID_DIM and 0 < ncols <= MAX_ARC_GRID_DIM


def arc_text_lines_to_grid(text: str, *, limit_rows: int = MAX_ARC_GRID_DIM) -> Grid | None:
    """Parse digit-only rows into a rectangular grid; return ``None`` if invalid."""
    if not str(text or "").strip():
        return None
    try:
        lines = [ln for ln in str(text).strip().split("\n") if ln.strip()]
        if not lines:
            return None
        if len(lines) > int(limit_rows):
            lines = lines[: int(limit_rows)]
        by_rows: list[list[int]] = []
        for line in lines:
            row = [int(x) for x in line if x.isdigit()]
            if not row:
                continue
            by_rows.append(row)
        if not by_rows:
            return None
        w = len(by_rows[0])
        if any(len(r) != w for r in by_rows):
            return None
        h = len(by_rows)
        if not arc_is_valid_grid_shape(h, w):
            return None
        for r in by_rows:
            for v in r:
                if v < 0 or v > 9:
                    return None
        return by_rows
    except (TypeError, ValueError):
        return None
