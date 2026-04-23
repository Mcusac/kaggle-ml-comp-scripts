---
name: code-fix-doer
description: Legacy name — execution spec is now code-fix-runner. Read .cursor/agents/code-fix-runner.md. Used by code-fix orchestrator. Do not invoke directly.
model: inherit
---

**Superseded:** The **`/code-fix` executor** is **`code-fix-runner`**. The **`code-fix`** orchestrator delegates the approved plan to **`code-fix-runner`**, not this document.

**Read `.cursor/agents/code-fix-runner.md`** for: strict plan following, per-tranche **verifier** / **tester**, no ad-hoc scanning, no `tempfile`, Windows shell rules, and output contract.
