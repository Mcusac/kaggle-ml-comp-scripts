"""
worker_core — the single shared training + inference loop.

All per-version differences are expressed through ``WorkerConfig``.
No version-specific logic lives here.
"""

import gc
import io
import os
import time
import bz2
import pickle
import numpy as np
import torch.cuda.amp as amp

from collections import defaultdict
from contextlib import redirect_stdout, redirect_stderr
from datasets import Dataset
from peft import get_peft_model_state_dict, set_peft_model_state_dict
from unsloth import FastLanguageModel, UnslothTrainingArguments

from layers.layer_0_core.level_0 import get_logger, get_torch

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    inference_turbo_dfs,   
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    QwenDataCollatorForCompletionOnlyLM, 
    ArcDataset, 
    QwenFormatter
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import calc_scores, WorkerConfig



torch = get_torch()
logger = get_logger(__name__)


def worker_core(rank: int, queue, end_time: float, config: WorkerConfig) -> None:
    """
    Main per-GPU worker loop.

    1. Applies environment variables and optional patches from *config*.
    2. Loads the model + PEFT adapter.
    3. Iterates over puzzle keys from *queue*, running TTT (train-then-test) for each.
    """

    # ------------------------------------------------------------------
    # Environment & patches
    # ------------------------------------------------------------------
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    for key, val in config.extra_env_vars.items():
        os.environ[key] = val

    if config.disable_amp_grad_scaler:
        amp.GradScaler = lambda **kwargs: torch.cuda.amp.GradScaler(enabled=False, **kwargs)

    if config.install_attention is not None:
        config.install_attention()

    rerun_mode = os.getenv("KAGGLE_IS_COMPETITION_RERUN")

    # ------------------------------------------------------------------
    # Model setup
    # ------------------------------------------------------------------
    max_seq_length = config.max_seq_length

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config.model_name,
        full_finetuning=False,
        load_in_4bit=True,
        local_files_only=True,
        use_gradient_checkpointing=False,
        max_seq_length=max_seq_length,
        **config.model_load_kwargs,
    )

    model = FastLanguageModel.get_peft_model(model, **config.peft_params)

    if config.post_peft_setup is not None:
        model = config.post_peft_setup(model)

    default_weights = get_peft_model_state_dict(model, adapter_name="default")
    default_weights = {k: v.clone().detach() for k, v in default_weights.items()}

    collator = QwenDataCollatorForCompletionOnlyLM(tokenizer=tokenizer, mlm=False)
    formatter = QwenFormatter(tokenizer=tokenizer)
    max_new_tokens = formatter.max_new_tokens()
    max_score = -np.log(0.2)

    if rerun_mode:
        test_path = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_test_challenges.json"
    else:
        test_path = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_evaluation_challenges.json"

    arc_test_set = ArcDataset.from_file(test_path)
    os.makedirs(config.dir_outputs, exist_ok=True)

    # ------------------------------------------------------------------
    # Puzzle loop
    # ------------------------------------------------------------------
    while not queue.empty():

        if time.time() > end_time:
            print(f"[Rank {rank}] stop!")
            break

        key = queue.get()
        if key is None:
            break

        start_time = time.time()
        torch.cuda.reset_peak_memory_stats()

        # Reset adapter weights to base checkpoint
        set_peft_model_state_dict(model, default_weights.copy(), adapter_name="default")
        model = FastLanguageModel.for_training(model)

        # ---- TTT: fine-tune on this puzzle's examples ----
        puzzle_ds = arc_test_set.change_keys([key])
        train_ds = puzzle_ds.augment(n=16, shfl_keys=True, seed=1)
        train_ds = train_ds.cut_to_len(formatter=formatter, name="text", max_len=max_seq_length)

        with io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
            trainer = config.trainer_class(
                model=model,
                tokenizer=tokenizer,
                data_collator=collator,
                train_dataset=Dataset.from_list(train_ds.as_list(formatter)),
                dataset_text_field="text",
                max_seq_length=max_seq_length,
                args=UnslothTrainingArguments(**config.train_args),
            )

            stats = trainer.train()

            if config.post_train_cleanup is not None:
                config.post_train_cleanup(model, trainer)

            model = trainer.accelerator.unwrap_model(model, keep_fp32_wrapper=False)
            del trainer

        model = FastLanguageModel.for_inference(model)

        gc.collect()
        torch.cuda.empty_cache()

        mem_mb = torch.cuda.max_memory_allocated() // 1024 ** 2
        print(f"[Rank {rank}] allocated {mem_mb}MB for training")
        torch.cuda.reset_peak_memory_stats()
        print(f"[Rank {rank}] training stats for puzzle {key}: {stats}")

        # ---- Inference: decode solutions ----
        puzzle_ds_multi = puzzle_ds.split_multi_replies()
        eval_ds = puzzle_ds_multi.augment(n=2, seed=2)
        eval_ds = eval_ds.cut_to_len(
            formatter=formatter, name="input", max_len=max_seq_length - max_new_tokens
        )

        test_id_to_subkeys: dict = defaultdict(list)
        for subkey in sorted(eval_ds.keys):
            test_id = subkey.split(".")[0].split("_")[1]
            test_id_to_subkeys[test_id].append(subkey)

        batches = config.build_batches(test_id_to_subkeys)

        with torch.inference_mode():
            known_scores: dict = {}

            for subkeys in batches:
                spend_time = time.time() - start_time
                if spend_time > 1200 or time.time() > end_time:
                    print(f"[Rank {rank}] timeout after {spend_time:.1f}s for puzzle {key}")
                    break

                print(f"[Rank {rank}] decoding {subkeys}")

                tokens = [
                    tokenizer.encode(eval_ds.get(sk, formatter)["input"])
                    for sk in subkeys
                ]

                dfs_result = inference_turbo_dfs(model, tokens, max_new_tokens, max_score, end_time)

                for subkey_id, scored_beams in dfs_result:
                    subkey = subkeys[subkey_id]
                    bk = subkey.split(".")[0]
                    decoded_result = []

                    for beam_score, beam_tokens in scored_beams:
                        array = formatter.convert_tokens_to_array(beam_tokens)
                        if array is None:
                            continue

                        solution = puzzle_ds_multi.invert_mod(array, subkey, inv_perm=True)
                        grid_id = (bk, tuple(map(tuple, solution)))

                        if grid_id not in known_scores:
                            print(f"[Rank {rank}] scoring {subkey} #{len(decoded_result)}")
                            aug_dataset = ArcDataset(
                                keys=[bk],
                                queries={bk: puzzle_ds_multi.queries.get(bk)},
                                replies={bk: [solution.tolist()]},
                            )
                            aug_dataset = aug_dataset.augment(seed=hash(bk) % 1024 ** 2)
                            aug_dataset = aug_dataset.cut_to_len(
                                formatter=formatter,
                                name="input",
                                max_len=max_seq_length - max_new_tokens,
                            )
                            aug_pairs = [
                                (s["input"], s["reply"])
                                for s in aug_dataset.as_list(formatter)
                            ]
                            aug_queries, aug_answers = zip(*aug_pairs)
                            scores1 = calc_scores(list(aug_queries[:4]), list(aug_answers[:4]), tokenizer, model)
                            scores2 = calc_scores(list(aug_queries[4:]), list(aug_answers[4:]), tokenizer, model)
                            known_scores[grid_id] = scores1 + scores2

                        decoded_result.append({
                            "beam_score": beam_score,
                            "score_aug": known_scores[grid_id],
                            "solution": solution,
                        })

                    if decoded_result:
                        out_path = os.path.join(config.dir_outputs, subkey)
                        with bz2.BZ2File(out_path, "w") as f:
                            pickle.dump(decoded_result, f)

                if config.post_batch_cleanup is not None:
                    config.post_batch_cleanup(tokens, dfs_result)

        mem_mb = torch.cuda.max_memory_allocated() // 1024 ** 2
        print(f"[Rank {rank}] allocated {mem_mb}MB for inference")
        spend_time = time.time() - start_time
        print(f"[Rank {rank}] finished {key} in {spend_time:.1f}s")