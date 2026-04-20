"""Phase 3: apply RUN_PHASE2 moves and rewrite import strings (run from repo root optional)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT_ARC = Path(__file__).resolve().parent
JSON_PATH = ROOT_ARC / "_phase2_scan_output.json"
PREFIX = "layers.layer_1_competition.level_1_impl.level_arc_agi_2"


def path_to_module(rel: str) -> str:
    return PREFIX + "." + rel.replace("/", ".").removesuffix(".py")


def main() -> int:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    moves = [f for f in data["files"] if f.get("needs_move")]
    moves.sort(key=lambda x: -len(x["path"]))

    print(f"Phase 3: {len(moves)} filesystem moves under {ROOT_ARC}")
    for m in sorted(moves, key=lambda x: x["path"]):
        src = ROOT_ARC / m["path"]
        dst = ROOT_ARC / m["target_path"]
        if not src.exists():
            print(f"ERR missing source: {m['path']}")
            return 1
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            print(f"ERR target exists: {m['target_path']}")
            return 1
        shutil.move(str(src), str(dst))
        print(f"OK {m['path']} -> {m['target_path']}")

    pairs: list[tuple[str, str]] = []
    for m in moves:
        old_m = path_to_module(m["path"])
        new_m = path_to_module(m["target_path"])
        pairs.append((old_m, new_m))
    pairs.sort(key=lambda x: -len(x[0]))

    scan_root = ROOT_ARC.parents[3]  # .../kaggle-ml-comp-scripts
    if not (scan_root / "scripts").is_dir():
        scan_root = ROOT_ARC.parents[4]
    script_roots = [
        scan_root / "scripts",
    ]
    if not script_roots[0].is_dir():
        print(f"ERR scripts dir not found under {scan_root}")
        return 1

    exts = {".py", ".mdc", ".md"}
    skip_names = {"_phase2_scan_output.json", "_phase3_apply.py"}
    changed: list[Path] = []

    for base in script_roots:
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix not in exts and p.name not in skip_names:
                continue
            if p.name in skip_names or "_phase2_scan" in p.name:
                continue
            if "__pycache__" in p.parts:
                continue
            text = p.read_text(encoding="utf-8")
            orig = text
            for old_m, new_m in pairs:
                if old_m in text:
                    text = text.replace(old_m, new_m)
            if text != orig:
                p.write_text(text, encoding="utf-8")
                changed.append(p)

    print(f"Rewrote imports in {len(changed)} files")
    for p in changed[:30]:
        print(f"   {p.relative_to(scan_root)}")
    if len(changed) > 30:
        print(f"   ... +{len(changed) - 30} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
