"""Verify export output."""

from pathlib import Path

from layers.layer_0_core.level_0 import verify_export_files


def verify_export_output(
    model_type: str = "end_to_end",
    *,
    export_dir: Path | None = None,
) -> bool:
    export_dir = Path("/kaggle/working/best_model") if export_dir is None else export_dir
    result = verify_export_files(export_dir, model_type)

    if result["success"]:
        print("\n✅", result["message"])
        print(f"   Model path: {result['model_path']}")
        print(f"\n📥 Next: Download {export_dir}/ folder")
    else:
        print("\n⚠️", result["message"])
        print(f"   Check {export_dir} for exported files")

    return result["success"]
