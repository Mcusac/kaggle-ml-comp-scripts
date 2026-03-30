## ARC-AGI-2 Run Tracking (MVP)

This contest package supports minimal run-folder tracking to prevent artifact overwrites and to create paper-grade provenance.

### Run folder location

On Kaggle:

- `/kaggle/working/arc_agi_2/runs/<run_id>/`

Locally:

- `output/arc_agi_2/runs/<run_id>/`

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

If omitted, a run id is generated automatically.

### Recommended workflow

1. Run train/tune/submit with a `--run-id` you can reuse if you want a combined narrative.
2. After the run completes, copy the entire run folder into your curated archive (e.g. `for_paper/YYYY-MM-DD/...`).

