---
generated: 2026-04-08
---

# infra/level_1/registry — Contest registration

**Import:** `layers.layer_1_competition.level_0_infra.level_1` or `…level_1.registry`.

## Purpose

Central registry for contest metadata: config class, data schema, paths, post-processor, and optional training loader hook.

## Contents

| Module | Description |
|--------|-------------|
| `contest_registry` | `ContestRegistry`, `register_contest`, `get_contest`, `detect_contest` |

## Public API

- **ContestRegistry** — classmethods for register/get/list
- **register_contest** / **get_contest** / **detect_contest** — module-level helpers

## Dependencies

- **`layers.layer_0_core.level_0`**: argument and logging helpers
- **`layers.layer_1_competition.level_0_infra.level_0`**: `ContestConfig`, `ContestDataSchema`, `ContestPaths`, `ContestPostProcessor`

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import register_contest, get_contest

# Contests call register_contest(...) at import/startup; tooling calls get_contest("slug").
entry = get_contest("my_contest")
paths_cls = entry["paths"]
```
