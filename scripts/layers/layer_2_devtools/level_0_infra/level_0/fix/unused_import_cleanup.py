"""Remove unused imports from sources using a check_health-style JSON report."""

import json
import re
from pathlib import Path
from typing import Any


def load_health_report(path: Path) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        with open(path, "r", encoding="utf-16") as f:
            content = f.read()
            json_start = content.find("{")
            if json_start > 0:
                content = content[json_start:]
            return json.loads(content)


class UnusedImportRemover:
    """Remove unused imports from Python files."""

    def __init__(self, root: Path, dry_run: bool = False):
        self.root = root
        self.dry_run = dry_run
        self.stats = {
            "files_modified": 0,
            "imports_removed": 0,
            "lines_removed": 0,
        }

    def process_report(self, report_data: dict[str, Any]) -> None:
        unused_imports = report_data.get("dead_code", {}).get("unused_imports", [])

        print(f"📋 Processing {len(unused_imports)} modules with unused imports...")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}")
        print()

        for module_info in unused_imports:
            self._process_module(module_info)

        self._print_summary()

    def _process_module(self, module_info: dict[str, Any]) -> None:
        module = module_info["module"]
        unused_names = set(module_info["names"])

        file_path = self.root / module.replace(".", "/")

        if file_path.is_dir():
            file_path = file_path / "__init__.py"
        elif not file_path.exists():
            file_path = file_path.with_suffix(".py")

        if not file_path.exists() or not file_path.is_file():
            print(f"⚠️  {module}: File not found at {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
            lines = original_content.splitlines(keepends=True)

        modified_lines, removed_count = self._remove_unused_imports(lines, unused_names)

        if removed_count == 0:
            return

        modified_content = "".join(modified_lines)
        if modified_content == original_content:
            return

        print(f"{'🔍' if self.dry_run else '✅'} {module}")
        print(f"   Removed: {', '.join(sorted(unused_names)[:5])}")
        if len(unused_names) > 5:
            print(f"   ... and {len(unused_names) - 5} more")

        if not self.dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(modified_content)

        self.stats["files_modified"] += 1
        self.stats["imports_removed"] += removed_count

    def _remove_unused_imports(
        self,
        lines: list[str],
        unused_names: set[str],
    ) -> tuple[list[str], int]:
        modified_lines: list[str] = []
        removed_count = 0
        in_import_block = False

        for line in lines:
            if re.match(r"^\s*(from|import)\s+", line):
                in_import_block = True

                if line.strip().startswith("from "):
                    match = re.match(r"^(\s*from\s+[\w.]+)\s+import\s+(.+)$", line)
                    if match:
                        prefix = match.group(1)
                        imports_str = match.group(2)

                        imports = [imp.strip().split(" as ")[0].strip() for imp in imports_str.split(",")]

                        used_imports = [imp for imp in imports if imp not in unused_names]
                        removed = [imp for imp in imports if imp in unused_names]

                        if removed:
                            removed_count += len(removed)
                            if used_imports:
                                new_line = f"{prefix} import {', '.join(used_imports)}\n"
                                modified_lines.append(new_line)
                        else:
                            modified_lines.append(line)
                    else:
                        modified_lines.append(line)
                else:
                    match = re.match(r"^(\s*import\s+)([\w.]+)(?:\s+as\s+(\w+))?", line)
                    if match:
                        module_name = match.group(2)
                        alias = match.group(3) if match.group(3) else None

                        name_to_check = alias if alias else module_name.split(".")[0]
                        if name_to_check in unused_names:
                            removed_count += 1
                        else:
                            modified_lines.append(line)
                    else:
                        modified_lines.append(line)
            else:
                if in_import_block and line.strip() == "":
                    modified_lines.append(line)
                else:
                    in_import_block = False
                    modified_lines.append(line)

        return modified_lines, removed_count

    def _print_summary(self) -> None:
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Files modified: {self.stats['files_modified']}")
        print(f"Imports removed: {self.stats['imports_removed']}")
        print(f"Lines removed: {self.stats['lines_removed']}")
        if self.dry_run:
            print("\n[DRY RUN] No files were actually modified.")


def run_unused_import_cleanup(*, report: Path, root: Path, dry_run: bool) -> int:
    if not report.is_file():
        print(f"❌ Error: Report file not found: {report}")
        return 1
    data = load_health_report(report)
    UnusedImportRemover(root, dry_run=dry_run).process_report(data)
    return 0
