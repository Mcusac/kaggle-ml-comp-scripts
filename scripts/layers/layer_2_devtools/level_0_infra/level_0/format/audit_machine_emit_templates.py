"""Markdown templates for machine audit emit (inventory + audit stubs)."""

from __future__ import annotations

from datetime import date
from typing import Any, cast


def build_inventory_markdown(
    *,
    level_name: str,
    audit_scope: str,
    generated: date,
    pass_number: int,
    run_id: str,
    bootstrap_md: str,
) -> str:
    return f"""---
generated: {generated.isoformat()}
run_id: {run_id}
scope: {audit_scope}
level: {level_name}
pass: {pass_number}
audit_profile: full
audit_preset: comprehensive
---

## INVENTORY: {level_name}

#### 1. Package & File Tree

See **Machine-generated (verify)** package tree below.

---

#### 2. Per-File Details

AST imports, `__all__` (static), and line counts are under **Machine-generated (verify)**.
_Planner machine pass: expand class/method signatures in a follow-up human planner if needed._

---

#### 3. Cross-package references (summary)

_To be refined by human planner against architecture rules._

---

#### 4. README / docs presence

_See tree for `README.md` files._

---

#### 5. Flags / keywords

_None auto-tagged this pass._

---

#### 6. Static scan summary

Precheck JSON path: `.cursor/audit-results/{audit_scope}/summaries/precheck_{level_name}_{generated.isoformat()}.json`

---

{bootstrap_md}
"""


def build_audit_markdown(
    *,
    level_name: str,
    level_number: int,
    level_path: str,
    audit_scope: str,
    generated: date,
    pass_number: int,
    run_id: str,
    precheck_rel: str,
    violations: list[Any],
) -> str:
    vlines = []
    for v in violations:
        row = v if isinstance(v, dict) else {}
        row = cast(dict[str, Any], row)
        vlines.append(
            f"- **{row.get('kind', '?')}** `{row.get('file', '')}` L{row.get('line', '?')}: {row.get('detail', '')}"
        )
    vblock = "\n".join(vlines) if vlines else "- _(none reported by precheck)_"

    phase7_skip = ""
    if audit_scope == "general" and level_number == 0:
        phase7_skip = "\n**Note:** Phase 7 cross-level rules skipped for general `level_0` per auditor spec.\n"

    return f"""---
generated: {generated.isoformat()}
pass_number: {pass_number}
run_id: {run_id}
audit_scope: {audit_scope}
level_name: {level_name}
level_path: {level_path}
run_mode: default
audit_profile: full
audit_preset: comprehensive
---

# Audit: {level_name} ({audit_scope})

**Inventory:** `.cursor/audit-results/{audit_scope}/inventories/INVENTORY_{level_name}.md`  
**Precheck:** `{precheck_rel}`

## PHASE 1 — Functions & Classes

Machine regenerate pass ({generated.isoformat()}): structural review deferred to targeted human pass when precheck is clean; see Phase 7 for tool findings.

## PHASE 2 — Files

Per inventory tree / bootstrap fragment.

## PHASE 3 — Packages & Sub-packages

Per inventory / `__init__.py` surfaces (verify against `init-exports.mdc` in a follow-up if needed).

## PHASE 4 — Legacy & Compatibility Purge

No automatic purge this pass.

## PHASE 5 — Full Level Review

DRY / circular imports: not rescanned beyond precheck scope this pass.

## PHASE 6 — README & Documentation

Spot-check recommended for drift vs exports.

## PHASE 7 — Cross-Level Audit

{phase7_skip}
**Precheck reconciliation (violations):**

{vblock}

## PHASE 8 — Caller updates

_List files that import changed public APIs after any code fix pass. This emit run lists callers only when companion edits were applied in-repo during the same session._

**CALLERS TOUCHED (Phase 8):** _(see consolidated rollup if orchestrator applied fixes)_

---

=== AUDIT RESULT: {level_name} ===
audit_profile: full
audit_preset: comprehensive
run_mode: recommendations-only
machine_emit: true

PUBLIC API (post-audit / intended):
  _See root and subpackage `__all__` / barrel exports; confirm against inventory._

CONSOLIDATED CHANGE LOG:
  Machine emit: inventory + audit markdown regenerated; precheck re-run.
  Code edits: only if orchestrator/auditor applied fixes in the same run (not by this script alone).

CALLERS TOUCHED (Phase 8): _(none unless stated above)_

VIOLATIONS (precheck):
  {len(violations)} record(s)

=== END AUDIT RESULT: {level_name} ===
"""
