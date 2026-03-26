from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("scripts/layers/layer_0_core")
LEVEL_DIRS = [ROOT / f"level_{i}" for i in range(1, 11)]

# Only match at start of line to reduce accidental replacements.
PATTERNS = [
    # from level_0 import ...
    (re.compile(r"^from\s+level_0\s+import\s+", re.M),
     "from layers.layer_0_core.level_0 import "),

    # from level_1 import ...
    (re.compile(r"^from\s+level_1\s+import\s+", re.M),
     "from layers.layer_0_core.level_1 import "),
]

def iter_py_files() -> list[Path]:
    files = []
    for d in LEVEL_DIRS:
        if not d.exists():
            continue
        for p in d.rglob("*.py"):
            if p.name == "__init__.py":
                continue
            files.append(p)
    return files

def transform(text: str) -> str:
    out = text
    for pat, repl in PATTERNS:
        out = pat.sub(repl, out)
    return out

def main() -> None:
    files = iter_py_files()
    changed = 0

    for p in files:
        orig = p.read_text(encoding="utf-8")
        new = transform(orig)
        if new != orig:
            p.write_text(new, encoding="utf-8")
            changed += 1
            print(f"✅ updated: {p}")

    print(f"Done. Files changed: {changed}")

if __name__ == "__main__":
    main()