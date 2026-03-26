from pathlib import Path
from typing import Iterable, Optional, Set, Union


class BasePackageDumper:
    """Base class providing shared file dumping utilities."""

    def __init__(
        self,
        file_extensions: Optional[Iterable[str]] = None,
        output_dir: Union[str, Path] = "package_dumps",
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.file_extensions: Optional[Set[str]] = (
            set(file_extensions) if file_extensions else None
        )

    def _write_file(self, file_path: Path, out) -> None:
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return

        out.write(f"\n{'=' * 80}\n")
        out.write(f"FILE: {file_path.name}\n")
        out.write(f"{'=' * 80}\n\n")
        out.write(content)
        out.write("\n")

    def _process_directory(self, directory: Path, out_file: Path) -> None:
        with out_file.open("w", encoding="utf-8") as out:
            for file in sorted(directory.iterdir(), key=lambda f: f.name):
                if file.is_file() and (
                    self.file_extensions is None
                    or file.suffix in self.file_extensions
                ):
                    self._write_file(file, out)

        print(f"Wrote: {out_file}")

    def dump(self) -> None:
        raise NotImplementedError


class PackageDumper(BasePackageDumper):
    """Dump directories to text files (recursive or explicit, single or multi)."""

    def __init__(
        self,
        traversal: str,
        save_mode: str,
        directories: Optional[Iterable[Union[str, Path]]] = None,
        root_dir: Optional[Union[str, Path]] = None,
        output_file: Optional[Union[str, Path]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.traversal = traversal
        self.save_mode = save_mode

        if traversal == "explicit":
            if not directories:
                raise ValueError("Explicit mode requires directories.")
            self.directories = [Path(d) for d in directories]

        elif traversal == "recursive":
            if not root_dir:
                raise ValueError("Recursive mode requires root_dir.")

            self.root_dir = Path(root_dir)

            if not self.root_dir.is_dir():
                raise ValueError(f"Not a directory: {self.root_dir}")

        else:
            raise ValueError(f"Unknown traversal mode: {traversal}")

        if save_mode == "single_file":
            if not output_file:
                raise ValueError("single_file mode requires output_file")

            self.single_file_path = Path(output_file)
            self.single_file_path.parent.mkdir(parents=True, exist_ok=True)

    def dump(self) -> None:
        if self.save_mode == "multi_file":
            if self.traversal == "explicit":
                for directory in self.directories:
                    self._dump_multi_file(directory)

            else:
                self._dump_recursive_multi(self.root_dir)

        else:
            with self.single_file_path.open("w", encoding="utf-8") as out:
                if self.traversal == "explicit":
                    for directory in self.directories:
                        self._dump_single_file(directory, out)

                else:
                    self._dump_recursive_single(self.root_dir, out)

    def _dump_multi_file(self, directory: Path) -> None:
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        out_file = self.output_dir / f"{directory.name}.txt"

        self._process_directory(directory, out_file)

    def _dump_recursive_multi(self, directory: Path) -> None:
        py_files = [
            f
            for f in directory.iterdir()
            if f.is_file()
            and (
                self.file_extensions is None
                or f.suffix in self.file_extensions
            )
        ]

        if py_files:
            name = (
                directory.name
                if directory == self.root_dir
                else directory.relative_to(self.root_dir)
                .as_posix()
                .replace("/", "_")
            )

            out_file = self.output_dir / f"{name}.txt"

            self._process_directory(directory, out_file)

        for sub_dir in sorted(
            [d for d in directory.iterdir() if d.is_dir()],
            key=lambda d: d.name,
        ):
            self._dump_recursive_multi(sub_dir)

    def _dump_single_file(self, directory: Path, out) -> None:
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        out.write(f"\n{'#' * 80}\nPACKAGE: {directory.name}\n{'#' * 80}\n")

        py_files = sorted(
            [
                f
                for f in directory.iterdir()
                if f.is_file()
                and (
                    self.file_extensions is None
                    or f.suffix in self.file_extensions
                )
            ],
            key=lambda f: f.name,
        )

        for file in py_files:
            self._write_file(file, out)

    def _dump_recursive_single(self, directory: Path, out) -> None:
        pkg_name = (
            directory.name
            if directory == self.root_dir
            else directory.relative_to(self.root_dir).as_posix()
        )

        py_files = sorted(
            [
                f
                for f in directory.iterdir()
                if f.is_file()
                and (
                    self.file_extensions is None
                    or f.suffix in self.file_extensions
                )
            ],
            key=lambda f: f.name,
        )

        if py_files:
            out.write(f"\n{'#' * 80}\nPACKAGE: {pkg_name}\n{'#' * 80}\n")

            for file in py_files:
                self._write_file(file, out)

        for sub_dir in sorted(
            [d for d in directory.iterdir() if d.is_dir()],
            key=lambda d: d.name,
        ):
            self._dump_recursive_single(sub_dir, out)
