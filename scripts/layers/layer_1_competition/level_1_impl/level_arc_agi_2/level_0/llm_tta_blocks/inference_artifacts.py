from typing import Any


def add_llm_tta_artifacts(parser: Any) -> None:
    parser.add_argument("--llm-infer-artifact-dir", type=str, default=None)

    parser.add_argument("--llm-infer-artifact-run-name", type=str, default="")