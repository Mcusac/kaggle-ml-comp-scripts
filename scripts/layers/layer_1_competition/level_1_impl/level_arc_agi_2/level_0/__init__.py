"""ARC-AGI-2 level_0 primitives.

Conceptual subpackages (organised by purpose, not by dependency level):
- ``arc_paths/``   — challenge filenames, eval paths, Kaggle paths, :class:`ARC26Paths`
- ``cli/``           — command-list arg appenders (common + LLM)
- ``config/``        — contest config, schema, post-processor
- ``datasets/``      — same-shape datasets and loader helpers
- ``decoding/``      — LLM turbo DFS, grid/token decoders, eval parse helpers
- ``grid/``          — tensor encoding, digit text, equality, hash keys
- ``infer/``         — inference artifact store layout
- ``llm_tta/``       — LLM-TTA DFS config and grid utilities
- ``llm_tta_blocks/`` — argparse blocks for LLM-TTA
- ``lm/``            — LM runtime, attention patchers, trainers, solver constants
- ``ndarray_ops/``   — small NumPy helpers
- ``notebook_commands/`` — notebook-style shell command builders
- ``ranking/``       — heuristics, scoring, augmentations, tuning IO, submit limits
- ``runner/``        — multiprocess runner entrypoints
- ``subparser_blocks/`` — argparse subparser building blocks
- ``validation/``    — JSON / submission validation
"""

from . import llm_tta_blocks, notebook_commands, subparser_blocks
from .llm_tta_blocks import (
    add_llm_tta_adaptation,
    add_llm_tta_args,
    add_llm_tta_augmentation,
    add_llm_tta_artifacts,
    add_llm_tta_core,
    add_llm_tta_decoding,
    add_llm_tta_inference,
    add_llm_tta_runtime,
)
from .notebook_commands import (
    build_submit_command,
    build_train_and_submit_command,
    build_train_command,
    build_tune_and_submit_command,
    build_tune_command,
    build_validate_data_command,
)
from .subparser_blocks import (
    STRATEGY_CHOICES,
    add_common,
    add_ensemble,
    add_max_targets,
    add_model,
    add_output,
    add_run_context,
    add_search_type,
    add_stacking,
    add_strategy,
)

from .arc_paths import ARC26Paths
from .arc_paths.eval_paths import arc_find_first_existing_file
from .arc_paths.kaggle_arc_challenge_paths import (
    arc_kaggle_challenges_json_path,
    arc_kaggle_default_challenge_bundle_root,
    arc_kaggle_evaluation_solutions_json_path,
)
from .cli.append_common_args import CONTEST, append_common_args
from .cli.command_llm import append_llm_args
from .config import ARC26Config, ARC26DataSchema, ARC26PostProcessor
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.datasets.dataset_same_shape import (
    ArcSameShapeGridDataset,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.datasets.dataset_same_shape_pairs import (
    collect_same_shape_train_pairs,
)
from .decoding.decoder_dfs import (
    GridCandidate,
    decode_grid_candidates,
)
from .decoding.llm_decoding import (
    REFERENCE_ASSISTANT_TOKEN_ID,
    REFERENCE_EOS_ID,
    REFERENCE_USER_TOKEN_ID,
    inference_turbo_dfs,
    turbo_dfs,
)
from .decoding.infer_batch_offsets import infer_notebook_style_decode_batches
from .decoding.token_decoder import (
    TokenDecodeCandidate,
    decode_tokens_to_grids,
)
from .grid.digit_grid_text import (
    MAX_ARC_GRID_DIM,
    arc_grid_to_text_lines,
    arc_is_valid_grid_shape,
    arc_text_lines_to_grid,
)
from .grid.grid_tensor_encoding import (
    CANVAS_SIZE,
    NUM_CHANNELS,
    grid_to_one_hot_tensor,
    logits_to_grid,
)
from .grid.grids_equal import arc_grids_equal
from .infer.infer_artifact_store import (
    DecodedStore,
    GuessDict,
    infer_ensure_run_layout,
    infer_eval_basekey,
    infer_finalize_artifact_root,
    infer_load_decoded_results_from_dir,
    infer_save_decoded_result_shard,
    infer_save_intermediate_candidates,
    infer_shard_basename,
)
from .llm_tta.llm_tta_config import LlmTtaDfsConfig, validate_llm_tta_dfs_config
from .llm_tta.llm_tta_grid_utils import (
    build_cell_probs_from_support_grids,
    coerce_arc_grid,
    collect_llm_tta_support_grids,
    empty_arc_grid_like,
    llm_tta_augment_seed,
    llm_tta_grid_hw,
)
from .lm.lm_adaptation import ArcLmAdaptationConfig, run_task_adaptation
from .lm.lm_attention_patcher_repeat_interleave import install_repeat_interleave_attention
from .lm.lm_attention_patcher_sdpa import install_sdpa_attention
from .lm.lm_runtime import (
    ArcLmBudget,
    ArcLmRuntimeProfile,
    apply_runtime_profile,
    build_budget,
)
from .lm.solver_core import COMMON_PEFT_PARAMS, COMMON_TRAIN_ARGS
from .ndarray_ops.numpy_color_permute import permute_mod
from .ndarray_ops.numpy_shuffled import shuffled
from .ndarray_ops.numpy_solution_validation import is_valid_solution
from .ranking.augmentations import (
    AugmentationSpec,
    IDENTITY_AUGMENTATION,
    apply_augmentation,
    generate_augmentation_specs,
    invert_augmentation,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ranking.candidate_scoring import (
    CandidatePrediction,
    RankedCandidate,
    rank_candidate_grids,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ranking.ensemble_reference_rankers import (
    ENSEMBLE_REFERENCE_RANKERS,
    Grid,
    ensemble_score_full_probmul_3,
    ensemble_score_kgmon,
    ensemble_score_sum,
    reference_hashable_solution,
)
from .ranking.heuristics import (
    DEFAULT_SUBMIT_HEURISTIC,
    HEURISTIC_QUICK_ORDER,
    HEURISTIC_THOROUGH_ORDER,
    heuristic_order_for_train_mode,
    predict_attempts_for_heuristic,
    predict_attempts_from_chosen_params,
)
from .ranking.stack_policy import (
    stack_explain_stacking_requirements,
    stack_raise_if_unsupported_strategy,
)
from .ranking.submit_limits import read_submit_max_tasks_env
from .ranking.tuning_io import load_chosen_params_from_tuned_config
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.runner.runner_entry import (
    run_entry,
)
from .runner.runner_worker_factory import make_local_worker
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.validation.validate_data import (
    require_data_root,
    validate_arc_inputs,
)

__all__ = (
    list(llm_tta_blocks.__all__)
    + list(notebook_commands.__all__)
    + list(subparser_blocks.__all__)
    + [
        "ARC26Config",
        "ARC26DataSchema",
        "ARC26Paths",
        "ARC26PostProcessor",
        "ArcLmAdaptationConfig",
        "ArcLmBudget",
        "ArcLmRuntimeProfile",
        "ArcSameShapeGridDataset",
        "AugmentationSpec",
        "CANVAS_SIZE",
        "COMMON_PEFT_PARAMS",
        "COMMON_TRAIN_ARGS",
        "CONTEST",
        "CandidatePrediction",
        "DEFAULT_SUBMIT_HEURISTIC",
        "DecodedStore",
        "ENSEMBLE_REFERENCE_RANKERS",
        "Grid",
        "GridCandidate",
        "GuessDict",
        "HEURISTIC_QUICK_ORDER",
        "HEURISTIC_THOROUGH_ORDER",
        "IDENTITY_AUGMENTATION",
        "LlmTtaDfsConfig",
        "MAX_ARC_GRID_DIM",
        "NUM_CHANNELS",
        "REFERENCE_ASSISTANT_TOKEN_ID",
        "REFERENCE_EOS_ID",
        "REFERENCE_USER_TOKEN_ID",
        "RankedCandidate",
        "TokenDecodeCandidate",
        "UnslothFixedTrainer",
        "UnslothV2FixedTrainer",
        "append_common_args",
        "append_llm_args",
        "apply_augmentation",
        "apply_runtime_profile",
        "arc_find_first_existing_file",
        "arc_grid_to_text_lines",
        "arc_grids_equal",
        "arc_is_valid_grid_shape",
        "arc_kaggle_challenges_json_path",
        "arc_kaggle_default_challenge_bundle_root",
        "arc_kaggle_evaluation_solutions_json_path",
        "arc_text_lines_to_grid",
        "build_budget",
        "build_cell_probs_from_support_grids",
        "coerce_arc_grid",
        "collect_llm_tta_support_grids",
        "collect_same_shape_train_pairs",
        "decode_grid_candidates",
        "decode_tokens_to_grids",
        "empty_arc_grid_like",
        "ensemble_score_full_probmul_3",
        "ensemble_score_kgmon",
        "ensemble_score_sum",
        "generate_augmentation_specs",
        "grid_to_one_hot_tensor",
        "heuristic_order_for_train_mode",
        "infer_ensure_run_layout",
        "infer_eval_basekey",
        "infer_finalize_artifact_root",
        "infer_load_decoded_results_from_dir",
        "infer_notebook_style_decode_batches",
        "infer_save_decoded_result_shard",
        "infer_save_intermediate_candidates",
        "infer_shard_basename",
        "inference_turbo_dfs",
        "install_repeat_interleave_attention",
        "install_sdpa_attention",
        "invert_augmentation",
        "is_valid_solution",
        "llm_tta_augment_seed",
        "llm_tta_grid_hw",
        "load_chosen_params_from_tuned_config",
        "logits_to_grid",
        "make_local_worker",
        "permute_mod",
        "predict_attempts_for_heuristic",
        "predict_attempts_from_chosen_params",
        "rank_candidate_grids",
        "read_submit_max_tasks_env",
        "reference_hashable_solution",
        "run_entry",
        "run_task_adaptation",
        "shuffled",
        "stack_explain_stacking_requirements",
        "stack_raise_if_unsupported_strategy",
        "turbo_dfs",
        "require_data_root",
        "validate_arc_inputs",
        "validate_llm_tta_dfs_config",
    ]
)


def __getattr__(name: str):
    if name == "UnslothFixedTrainer":
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.lm.trainer_v1_fixed import (
            UnslothFixedTrainer,
        )

        return UnslothFixedTrainer
    if name == "UnslothV2FixedTrainer":
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.lm.trainer_v2_fixed import (
            UnslothV2FixedTrainer,
        )

        return UnslothV2FixedTrainer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
