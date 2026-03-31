## ARC-AGI-2 Run Tracking (MVP)

This contest package supports minimal run-folder tracking to prevent artifact overwrites and to create paper-grade provenance.

### Train / tune / submit behavior

- **Train (`--models`)** — Registered neural models (e.g. `grid_cnn_v0`) run PyTorch training and write `model.pt` + `train_config.json` under `output/models/arc_agi_2/<model>/`. Names without a trainer use **training-challenge heuristic scoring** and store the best `copy_input` / `blank_grid` choice per model in `train_metadataJSON` (`train_scores`).
- **Tune** — Picks a heuristic using the **evaluation** split when solution JSON is present (unchanged).
- **Submit (`--strategy`)** — `single` uses one heuristic or neural `attempt_1` + heuristic second attempt when a checkpoint is available. `ensemble` ranks heuristics on the training corpus for two attempts. `stacking` / `stacking_ensemble` are **not implemented** and fail with a clear error.
- **Neural inference** — Submit loads `per_model.<primary>.artifacts.checkpoint` from `train_metadata.json` when present (override with `--neural-checkpoint` / `--neural-train-config`). **Limitation (v0):** the grid CNN is trained on same-shape input/output pairs only; inference trims predictions to the test **input** size (incorrect when the true output size differs).

### Artifacts under `output/models/arc_agi_2/`

- Global `train_metadata.json` listing `per_model` entries (heuristic params and/or neural paths).
- Per-model directory for neural runs: `model.pt`, `train_config.json`.

### Run folder location

On Kaggle:

- `/kaggle/working/arc_agi_2/runs/<run_id>/`

Locally:

- `output/arc_agi_2/runs/<run_id>/`

(`init_run_context(..., paths=...)` can override the output base via `ContestRunPathsProtocol`.)

### Run folder contents

- `run_metadata.json` (canonical manifest; written/updated automatically)
- `commands.txt` (copy/paste reproducibility)
- `artifacts/`
  - `train_metadata.json` (if train executed)
  - `best_config.json` (if tune executed)
  - `submission.json` (if submit executed)
- `logs/` (reserved; you may still capture logs via notebook execution tooling)

### CLI usage

All ARC commands accept optional:

- `--run-id <id>` to control the run folder name
- `--run-dir <path>` to write into an explicit folder

Submit additionally: `--models`, `--train-mode` (ensemble ranking), `--neural-checkpoint`, `--neural-train-config`, `--tuned-config`.

If omitted, a run id is generated automatically.

### Recommended workflow

1. Run train/tune/submit with a `--run-id` you can reuse if you want a combined narrative.
2. After the run completes, copy the entire run folder into your curated archive (e.g. `for_paper/YYYY-MM-DD/...`).
