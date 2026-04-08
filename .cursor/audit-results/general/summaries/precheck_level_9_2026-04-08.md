---
generated: 2026-04-08
audit_scope: general
level_name: level_9
artifact_kind: precheck
precheck_status: skipped_machine_script
---

# Precheck (machine script unavailable)

## Why skipped

ModuleNotFoundError: No module named 'torchvision'

## What this means

- This environment could not import the devtools precheck stack.
- The code-audit orchestrator can still run (inventories/audits); Phase 7 machine reconciliation is unavailable.

## How to get machine precheck locally

- Create/activate a venv where optional deps (notably `torchvision`) import cleanly, then rerun this command.
