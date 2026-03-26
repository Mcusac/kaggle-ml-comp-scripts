# Ontology

OBO file parsing for Gene Ontology and similar ontologies.

## Purpose

Parse OBO format files into parent/child term maps. Uses obonet when available; falls back to manual parsing when obonet is not installed.

## Contents

- `obo_parser.py` – `parse_obo_file`

## Public API

- `parse_obo_file` – Parse OBO file into (parents_map, children_map)

## Dependencies

stdlib only. Optional: obonet (preferred when available).

## Usage Example

```python
from level_0 import parse_obo_file
from pathlib import Path

parents, children = parse_obo_file(Path("go-basic.obo"))
```
