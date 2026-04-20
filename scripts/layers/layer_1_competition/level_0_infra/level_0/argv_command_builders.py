"""Contest-agnostic argv token appenders shared by contest command builders.

These primitives centralise the notebook-cell and ``python run.py`` argv
shapes that contest packages build. Each helper mutates ``cmd`` in place and
appends argv tokens in a fixed, byte-stable order so both shapes can share
them without altering their output ordering.
"""

from typing import List, Optional


def resolve_models(
    models: Optional[List[str]],
    default: Optional[List[str]] = None,
) -> List[str]:
    """Return ``models`` when non-empty, else ``default`` or ``["baseline_approx"]``."""
    return models or (default if default is not None else ["baseline_approx"])


def append_models(cmd: List[str], models: List[str]) -> None:
    """Append ``--models a,b,c``."""
    cmd.extend(["--models", ",".join(models)])


def resolve_and_append_models(
    cmd: List[str],
    models: Optional[List[str]],
    default: Optional[List[str]] = None,
) -> None:
    """Append the resolved models list."""
    append_models(cmd, resolve_models(models, default))


def append_strategy(cmd: List[str], strategy: str) -> None:
    """Append ``--strategy S``."""
    cmd.extend(["--strategy", str(strategy)])


def append_train_mode(cmd: List[str], train_mode: str) -> None:
    """Append ``--train-mode M``."""
    cmd.extend(["--train-mode", str(train_mode)])


def append_tune_args(cmd: List[str], model: str, search_type: str) -> None:
    """Append ``--model M --search-type T`` (paired, like the notebook builder)."""
    cmd.extend(["--model", str(model), "--search-type", str(search_type)])


def append_max_targets(cmd: List[str], max_targets: int) -> None:
    """Append ``--max-targets N`` when ``N > 0``."""
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])


def append_output_csv(cmd: List[str], output_csv: Optional[str]) -> None:
    """Append ``--output-csv P`` when set."""
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])


def append_ensemble_weights(
    cmd: List[str],
    ensemble_weights: Optional[List[float]],
) -> None:
    """Append ``--ensemble-weights w1,w2,...`` when set."""
    if ensemble_weights:
        cmd.extend(
            [
                "--ensemble-weights",
                ",".join(str(v) for v in ensemble_weights),
            ]
        )


def append_no_validation_stacking(
    cmd: List[str],
    use_validation_for_stacking: bool,
) -> None:
    """Append ``--no-validation-stacking`` when validation-based stacking is disabled."""
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")


def append_tuned_config(cmd: List[str], tuned_config_path: Optional[str]) -> None:
    """Append ``--tuned-config P`` when set."""
    if tuned_config_path:
        cmd.extend(["--tuned-config", str(tuned_config_path)])


def append_run_args(
    cmd: List[str],
    run_id: Optional[str],
    run_dir: Optional[str],
    log_file: Optional[str],
) -> None:
    """Append ``--run-id``, ``--run-dir``, ``--log-file`` when set (in that order)."""
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])


__all__ = [
    "resolve_models",
    "append_models",
    "resolve_and_append_models",
    "append_strategy",
    "append_train_mode",
    "append_tune_args",
    "append_max_targets",
    "append_output_csv",
    "append_ensemble_weights",
    "append_no_validation_stacking",
    "append_tuned_config",
    "append_run_args",
]
