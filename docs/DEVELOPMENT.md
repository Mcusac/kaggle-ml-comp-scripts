# Local development (Windows)

## Create / refresh the venv

Run this from PowerShell:

```powershell
& "c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\dev\scripts\setup_project_venv.ps1"
```

## Activate

```powershell
& "c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.venv\Scripts\Activate.ps1"
```

## Run audits / validation (always from `scripts/`)

```powershell
Set-Location "c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts"
python dev/scripts/audit_precheck.py --audit-scope competition_infra --level-path "c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_1_competition\level_0_infra\level_0" --level-name level_0
python dev/scripts/validate_before_upload.py
pytest
```

## Sanity check: torch + path bootstrap

```powershell
Set-Location "c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts"
python -c "import path_bootstrap; path_bootstrap.prepend_framework_paths(); import torch; print(torch.__version__)"
```

