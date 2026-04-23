"""Audit precheck composed workflows."""

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.preparation.precheck_payload_ops import (
    PrecheckMeta,
    build_precheck_json,
    build_precheck_markdown,
)
from layers.layer_2_devtools.level_1_impl.level_0.scan.contest_scan_ops import (
    scan_contest_level_directory,
    scan_contest_root_directory,
)
from layers.layer_2_devtools.level_1_impl.level_0.scan.general_scan_ops import (
    build_general_json_payload,
    build_general_markdown,
    iter_level_py_files,
    scan_general_stack_file,
)
from layers.layer_2_devtools.level_1_impl.level_0.scan.infra_scan_ops import (
    scan_infra_level_directory,
)
from layers.layer_2_devtools.level_1_impl.level_0.scan.special_scan_ops import (
    scan_special_tree_directory,
)
from layers.layer_2_devtools.level_0_infra.level_0.constants.import_patterns import LEVEL_DIR_RE
from layers.layer_2_devtools.level_0_infra.level_0 import (
    build_audit_markdown,
    build_inventory_markdown,
)
from layers.layer_2_devtools.level_0_infra.level_0 import (
    bootstrap_markdown,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.audit_paths import (
    mirror_files_to_run_snapshot,
    precheck_summary_json_path,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.layer_core_paths import find_layer_0_core_ancestor
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import find_workspace_root
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import resolve_workspace_root


@dataclass(frozen=True)
class PrecheckRunResult:
    reports: list
    markdown: str
    payload: dict[str, Any]
    workspace: Path
    output_base: Path


def run_general_full_precheck(
    *,
    layer_0_core: Path,
    generated: date,
    level_name: str,
    workspace_root: Path | None = None,
) -> PrecheckRunResult:
    """Run full general-stack precheck across level_0..level_10."""
    core = layer_0_core.resolve()
    workspace = workspace_root.resolve() if workspace_root else find_workspace_root(core)
    files = iter_level_py_files(core)
    reports = [scan_general_stack_file(path, core) for path in files]
    markdown = build_general_markdown(reports, generated, core, workspace)
    payload = build_general_json_payload(reports, generated, core, workspace)
    payload["artifact"] = "precheck_general_stack"
    payload["level"] = level_name
    payload["artifact_kind"] = "precheck"
    payload["precheck_status"] = "ok"
    out_base = _build_output_base(workspace, "general", level_name, generated)
    return PrecheckRunResult(reports, markdown, payload, workspace, out_base)


def run_target_precheck(
    *,
    audit_scope: str,
    level_path: Path,
    level_name: str,
    generated: date,
    workspace_root: Path | None = None,
    precheck_kind: str = "auto",
) -> PrecheckRunResult:
    """Run one target precheck by scope and return markdown+payload."""
    path = level_path.resolve()
    workspace = workspace_root.resolve() if workspace_root else find_workspace_root(path)
    root = path if path.is_dir() else path.parent

    if audit_scope == "general":
        layer_core = find_layer_0_core_ancestor(path)
        if layer_core is None:
            raise ValueError("general scope: level_path must be under layer_0_core")
        files = sorted(root.rglob("*.py")) if root.is_dir() else []
        reports = [scan_general_stack_file(file_path, layer_core) for file_path in files]
        meta = PrecheckMeta(generated, "general", level_name, "precheck", root.resolve())
        kinds = [
            "LAYER0_CORE_MIXED_IMPORT_STYLE",
            "WRONG_LEVEL",
            "UPWARD",
            "DEEP_PATH",
            "RELATIVE_IN_LOGIC",
            "PARSE_ERROR",
        ]
        markdown = build_precheck_markdown(
            reports, meta, workspace, "Precheck: general level package", kinds
        )
        payload = build_precheck_json(reports, meta, workspace)
    elif audit_scope == "competition_infra":
        if not root.is_dir():
            raise ValueError("competition_infra: level_path must be a directory")
        reports = scan_infra_level_directory(root)
        meta = PrecheckMeta(generated, "competition_infra", level_name, "precheck", root.resolve())
        kinds = [
            "INFRA_TIER_UPWARD",
            "INFRA_BARREL_DEEP",
            "INFRA_GENERAL_LEVEL",
            "DEEP_PATH",
            "RELATIVE_IN_LOGIC",
            "PARSE_ERROR",
        ]
        markdown = build_precheck_markdown(
            reports, meta, workspace, "Precheck: competition infra level package", kinds
        )
        payload = build_precheck_json(reports, meta, workspace)
    else:
        resolved_kind = precheck_kind if precheck_kind != "auto" else resolve_contests_precheck_kind(
            root, level_name
        )
        reports, markdown = _run_contests_special_mode(
            root=root,
            level_path=path,
            level_name=level_name,
            generated=generated,
            workspace=workspace,
            mode=resolved_kind,
        )
        meta = PrecheckMeta(generated, "contests_special", level_name, "precheck", root.resolve())
        payload = build_precheck_json(reports, meta, workspace)
        payload["precheck_kind"] = resolved_kind

    out_base = _build_output_base(workspace, audit_scope, level_name, generated)
    return PrecheckRunResult(reports, markdown, payload, workspace, out_base)


def resolve_contests_precheck_kind(root: Path, level_name: str) -> str:
    """Infer contests precheck mode from target path and level key."""
    if level_name == "layer_Z_unsorted" or root.name == "layer_Z_unsorted":
        return "special_tree"
    if LEVEL_DIR_RE.fullmatch(root.name):
        return "contest_tier"
    if root.parent.name == "contests":
        return "contest_root"
    raise ValueError(
        "contests_special: could not infer precheck mode from --level-path; "
        "pass --precheck-kind contest_tier|contest_root|special_tree."
    )


def _run_contests_special_mode(
    *,
    root: Path,
    level_path: Path,
    level_name: str,
    generated: date,
    workspace: Path,
    mode: str,
) -> tuple[list, str]:
    if mode == "contest_tier":
        if not LEVEL_DIR_RE.fullmatch(root.name):
            raise ValueError("contests_special tier mode requires .../contests/<slug>/level_K")
        contest_root = root.parent
        if contest_root.name == "contests":
            raise ValueError(
                "contests_special: missing contest package between contests/ and level_K"
            )
        slug = contest_root.name
        reports = scan_contest_level_directory(contest_root, root, slug)
        meta = PrecheckMeta(generated, "contests_special", level_name, "precheck", root.resolve())
        kinds = [
            "CONTEST_UPWARD",
            "CONTEST_DEEP_PATH",
            "CONTEST_OTHER_PACKAGE",
            "RELATIVE_IN_LOGIC",
            "PARSE_ERROR",
        ]
        markdown = build_precheck_markdown(
            reports, meta, workspace, f"Precheck: contest {slug} level package", kinds
        )
        return reports, markdown
    if mode == "contest_root":
        if root.parent.name != "contests":
            raise ValueError("contest_root mode requires .../contests/<slug>/")
        slug = root.name
        reports = scan_contest_root_directory(root, slug)
        meta = PrecheckMeta(generated, "contests_special", level_name, "precheck", root.resolve())
        kinds = ["CONTEST_OTHER_PACKAGE", "RELATIVE_IN_LOGIC", "PARSE_ERROR"]
        markdown = build_precheck_markdown(
            reports,
            meta,
            workspace,
            f"Precheck: contest {slug} package root (top-level *.py)",
            kinds,
        )
        return reports, markdown
    if mode == "special_tree":
        reports = scan_special_tree_directory(root)
        meta = PrecheckMeta(generated, "contests_special", level_name, "precheck", root.resolve())
        kinds = ["RELATIVE_IN_LOGIC", "PARSE_ERROR"]
        markdown = build_precheck_markdown(
            reports, meta, workspace, f"Precheck: special tree ({root.name})", kinds
        )
        return reports, markdown
    raise ValueError(f"Unsupported contests precheck mode: {mode}")


def _build_output_base(workspace: Path, scope: str, level_name: str, generated: date) -> Path:
    return (
        workspace
        / ".cursor"
        / "audit-results"
        / scope
        / "summaries"
        / f"precheck_{level_name}_{generated.isoformat()}"
    )


def dumps_precheck_payload(payload: dict[str, Any]) -> str:
    """Serialize precheck payload as deterministic JSON text."""
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def run_comprehensive_audit_emit(
    *,
    manifest: Path,
    workspace_override: Path | None,
    generated: date,
    run_id: str,
    pass_number: int,
    skip_precheck: bool,
    scripts_root: Path,
) -> int:
    """Manifest loop: optional precheck, bootstrap fragment, inventory + audit markdown writes."""
    workspace = resolve_workspace_root(
        scripts_root.resolve(),
        workspace_override.resolve() if workspace_override else None,
    )

    data = json.loads(manifest.read_text(encoding="utf-8"))
    targets: list[dict[str, Any]] = data.get("targets") or []

    print(f"🚀 comprehensive_audit_emit: {len(targets)} targets, workspace={workspace}")

    for i, t in enumerate(targets):
        scope = t["audit_scope"]
        level_name = t["level_name"]
        level_path = Path(t["level_path"])
        lp_rel = t.get("level_path_relative") or str(level_path)
        violations: list[Any] = []

        print(f"  [{i+1}/{len(targets)}] precheck+emit {scope}/{level_name}")

        if not skip_precheck:
            pk = t.get("precheck_kind")
            precheck_kind = (
                str(pk) if pk and pk not in ("general_level", "infra") else "auto"
            )
            try:
                precheck_result = run_target_precheck(
                    audit_scope=scope,
                    level_path=level_path,
                    level_name=level_name,
                    generated=generated,
                    workspace_root=workspace,
                    precheck_kind=precheck_kind,
                )
                output_base = _build_output_base(workspace, scope, level_name, generated)
                output_base.parent.mkdir(parents=True, exist_ok=True)
                Path(str(output_base) + ".md").write_text(
                    precheck_result.markdown, encoding="utf-8"
                )
                Path(str(output_base) + ".json").write_text(
                    dumps_precheck_payload(precheck_result.payload), encoding="utf-8"
                )
                raw_violations = precheck_result.payload.get("violations", [])
                if isinstance(raw_violations, list):
                    violations = raw_violations
            except (OSError, TypeError, ValueError) as exc:
                print(f"    ⚠️ precheck: {exc} (continuing)")

        try:
            boot = bootstrap_markdown(level_path.resolve(), workspace)
        except (OSError, ValueError) as exc:
            boot = f"_bootstrap failed: {exc}"

        inv = build_inventory_markdown(
            level_name=level_name,
            audit_scope=scope,
            generated=generated,
            pass_number=pass_number,
            run_id=run_id,
            bootstrap_md=boot,
        )
        inv_dir = workspace / ".cursor/audit-results" / scope / "inventories"
        inv_dir.mkdir(parents=True, exist_ok=True)
        inv_path = inv_dir / f"INVENTORY_{level_name}.md"
        inv_path.write_text(inv, encoding="utf-8")

        if not violations:
            pj = precheck_summary_json_path(workspace, scope, level_name, generated)
            if pj.is_file():
                try:
                    violations = json.loads(pj.read_text(encoding="utf-8")).get(
                        "violations", []
                    )
                except json.JSONDecodeError:
                    violations = []
        precheck_rel = (
            f".cursor/audit-results/{scope}/summaries/"
            f"precheck_{level_name}_{generated.isoformat()}.md"
        )

        audit = build_audit_markdown(
            level_name=level_name,
            level_number=int(t.get("level_number", 0)),
            level_path=lp_rel,
            audit_scope=scope,
            generated=generated,
            pass_number=pass_number,
            run_id=run_id,
            precheck_rel=precheck_rel,
            violations=violations,
        )
        aud_dir = workspace / ".cursor/audit-results" / scope / "audits"
        aud_dir.mkdir(parents=True, exist_ok=True)
        aud_path = aud_dir / f"{level_name}_audit.md"
        aud_path.write_text(audit, encoding="utf-8")

        snap_sources: list[Path] = [inv_path, aud_path]
        if not skip_precheck:
            snap_base = _build_output_base(workspace, scope, level_name, generated)
            snap_md = Path(str(snap_base) + ".md")
            snap_json = Path(str(snap_base) + ".json")
            if snap_md.is_file():
                snap_sources.append(snap_md)
            if snap_json.is_file():
                snap_sources.append(snap_json)
        mirror_files_to_run_snapshot(
            workspace=workspace,
            audit_scope=scope,
            level_name=level_name,
            generated=generated,
            sources=snap_sources,
        )

    print("✅ comprehensive_audit_emit done")
    return 0