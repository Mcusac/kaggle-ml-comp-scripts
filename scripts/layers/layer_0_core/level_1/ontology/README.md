# level_1/ontology

## Purpose
GO hierarchy propagation and ontology configuration resolution for protein function prediction.

## Contents
- `config_resolver.py` — `OntologyConfigResolver`: resolve ontology config from base config
- `hierarchy_propagator.py` — `HierarchyPropagator`: load OBO, traverse hierarchy, propagate predictions

## Public API
- `HierarchyPropagator(parents_map, children_map, term_to_idx)` — GO hierarchy operations
- `OntologyConfigResolver` — Get ontology config for a given ontology name

## Dependencies
- `level_0` — `parse_obo_file` (from level_0.ontology)

## Usage Example
```python
from level_1.ontology import HierarchyPropagator

propagator = HierarchyPropagator(parents_map, children_map, term_to_idx)
propagator.load_from_obo("go-basic.obo")
ancestors = propagator.get_ancestors("GO:0008150")
```
