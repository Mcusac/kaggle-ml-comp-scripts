"""Verify export output."""

from pathlib import Path

from layers.layer_0_core.level_0 import verify_export_files

KAGGLE_EXPORT_DIR = Path('/kaggle/working/best_model')


def verify_export_output(model_type: str = 'end_to_end') -> bool:
    result = verify_export_files(KAGGLE_EXPORT_DIR, model_type)

    if result['success']:
        print("\n✅", result['message'])
        print(f"   Model path: {result['model_path']}")
        print(f"\n📥 Next: Download {KAGGLE_EXPORT_DIR}/ folder")
    else:
        print("\n⚠️", result['message'])
        print(f"   Check {KAGGLE_EXPORT_DIR} for exported files")

    return result['success']
