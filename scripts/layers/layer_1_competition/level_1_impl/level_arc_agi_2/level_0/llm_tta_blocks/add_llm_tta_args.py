"""Add LLM TTA arguments to parser."""

from typing import Any


def add_llm_tta_args(parser: Any) -> None:
    parser.add_argument(
        "--llm-execution-mode",
        choices=("surrogate", "lm_backend"),
        default="surrogate",
        help="llm_tta_dfs execution mode.",
    )
    parser.add_argument("--llm-num-augmentations", type=int, default=8, help="Number of ARC TTA augmentations.")
    parser.add_argument("--llm-beam-width", type=int, default=12, help="Beam width for constrained decoder.")
    parser.add_argument("--llm-max-candidates", type=int, default=6, help="Max candidate grids per augmentation.")
    parser.add_argument("--llm-max-neg-log-score", type=float, default=120.0, help="Prune beams above this -log score.")
    parser.add_argument("--llm-seed", type=int, default=0, help="Deterministic seed for augmentation sampling.")
    parser.add_argument(
        "--llm-consistency-weight",
        type=float,
        default=1.0,
        help="Weight for augmentation agreement in candidate ranking.",
    )
    parser.add_argument(
        "--llm-model-weight",
        type=float,
        default=1.0,
        help="Weight for model score term in candidate ranking.",
    )
    parser.add_argument(
        "--llm-enable-neural-backend",
        action="store_true",
        help="Enable neural backend path in llm_tta_dfs when available.",
    )
    parser.add_argument("--llm-model-path", type=str, default=None, help="Optional base LLM model path.")
    parser.add_argument("--llm-lora-path", type=str, default=None, help="Optional LoRA adapter path.")
    parser.add_argument("--llm-max-runtime-sec", type=float, default=0.0, help="Optional max runtime budget.")
    parser.add_argument("--llm-task-runtime-sec", type=float, default=0.0, help="Optional per-task budget.")
    parser.add_argument("--llm-decode-runtime-sec", type=float, default=0.0, help="Optional per-decode budget.")
    parser.add_argument("--llm-adapt-steps", type=int, default=0, help="Optional adaptation steps.")
    parser.add_argument("--llm-adapt-batch-size", type=int, default=1, help="Adaptation batch size.")
    parser.add_argument(
        "--llm-adapt-gradient-accumulation-steps",
        type=int,
        default=1,
        help="Adaptation gradient accumulation steps.",
    )
    parser.add_argument("--llm-adapt-disabled", action="store_true", help="Disable task adaptation.")
    parser.add_argument(
        "--llm-per-task-adaptation",
        action="store_true",
        help="Fine-tune LoRA on task support before decode (lm_backend; use with --llm-adapt-steps >= 1).",
    )
    parser.add_argument(
        "--llm-augmentation-likelihood-weight",
        type=float,
        default=1.0,
        help="Weight for augmentation-likelihood score term.",
    )
    parser.add_argument(
        "--llm-runtime-attention-mode",
        choices=("auto", "eager", "sdpa"),
        default="auto",
        help="Runtime attention mode hint for LM backend.",
    )
    parser.add_argument(
        "--llm-runtime-disable-compile",
        action="store_true",
        help="Disable compile-related paths in runtime profile.",
    )
    parser.add_argument(
        "--llm-runtime-allocator-expandable-segments",
        action="store_true",
        default=True,
        help="Enable expandable segments allocator profile.",
    )
    parser.add_argument(
        "--llm-runtime-allocator-max-split-size-mb",
        type=int,
        default=0,
        help="Optional allocator max split size.",
    )
    parser.add_argument(
        "--llm-prefer-cnn-attempt1",
        action="store_true",
        help="When CNN checkpoint is available, prefer CNN for attempt_1 over llm_tta path.",
    )
    parser.add_argument(
        "--llm-candidate-ranker",
        choices=("default", "kgmon", "probmul"),
        default="default",
        help="Candidate merge ranker for llm_tta_dfs (default=weighted package ranker).",
    )
    parser.add_argument(
        "--llm-infer-artifact-dir",
        type=str,
        default=None,
        help=(
            "Optional root directory for inference artifacts: inference_outputs/ (bz2 shards), "
            "decoded_results/ (snapshot after submit), intermediate_candidates/ (JSON). "
            "Use inference_outputs for benchmark_rankers --decoded-dir."
        ),
    )
    parser.add_argument(
        "--llm-infer-artifact-run-name",
        type=str,
        default="",
        help="Suffix merged into loaded guess keys (reference notebook run_name; often empty).",
    )