---
generated: 2026-04-22
artifact: circular_deps_scan
schema: circular_deps_scan.v1
root: C:/Users/mdc0431/OneDrive - UNT System/Documents/Kaggle/code/input/kaggle-ml-comp-scripts/scripts
---

# Circular dependency scan

- Root: `C:/Users/mdc0431/OneDrive - UNT System/Documents/Kaggle/code/input/kaggle-ml-comp-scripts/scripts`
- Files with parse errors: 0
- Cycle components: 68

## Cycles

1. **1 modules**
   - Chain: `layers -> layers`
   - Nodes: `layers`
2. **1 modules**
   - Chain: `layers.layer_0_core -> layers.layer_0_core`
   - Nodes: `layers.layer_0_core`
3. **1 modules**
   - Chain: `layers.layer_0_core.level_0 -> layers.layer_0_core.level_0`
   - Nodes: `layers.layer_0_core.level_0`
4. **1 modules**
   - Chain: `layers.layer_0_core.level_0.vision -> layers.layer_0_core.level_0.vision`
   - Nodes: `layers.layer_0_core.level_0.vision`
5. **1 modules**
   - Chain: `layers.layer_0_core.level_1 -> layers.layer_0_core.level_1`
   - Nodes: `layers.layer_0_core.level_1`
6. **1 modules**
   - Chain: `layers.layer_0_core.level_1.cli -> layers.layer_0_core.level_1.cli`
   - Nodes: `layers.layer_0_core.level_1.cli`
7. **1 modules**
   - Chain: `layers.layer_0_core.level_1.cli.builders -> layers.layer_0_core.level_1.cli.builders`
   - Nodes: `layers.layer_0_core.level_1.cli.builders`
8. **1 modules**
   - Chain: `layers.layer_0_core.level_1.data -> layers.layer_0_core.level_1.data`
   - Nodes: `layers.layer_0_core.level_1.data`
9. **1 modules**
   - Chain: `layers.layer_0_core.level_1.data.domain -> layers.layer_0_core.level_1.data.domain`
   - Nodes: `layers.layer_0_core.level_1.data.domain`
10. **1 modules**
   - Chain: `layers.layer_0_core.level_1.data.domain.vision -> layers.layer_0_core.level_1.data.domain.vision`
   - Nodes: `layers.layer_0_core.level_1.data.domain.vision`
11. **1 modules**
   - Chain: `layers.layer_0_core.level_1.data.processing -> layers.layer_0_core.level_1.data.processing`
   - Nodes: `layers.layer_0_core.level_1.data.processing`
12. **1 modules**
   - Chain: `layers.layer_0_core.level_1.features -> layers.layer_0_core.level_1.features`
   - Nodes: `layers.layer_0_core.level_1.features`
13. **1 modules**
   - Chain: `layers.layer_0_core.level_1.runtime -> layers.layer_0_core.level_1.runtime`
   - Nodes: `layers.layer_0_core.level_1.runtime`
14. **1 modules**
   - Chain: `layers.layer_0_core.level_1.search -> layers.layer_0_core.level_1.search`
   - Nodes: `layers.layer_0_core.level_1.search`
15. **1 modules**
   - Chain: `layers.layer_0_core.level_1.training -> layers.layer_0_core.level_1.training`
   - Nodes: `layers.layer_0_core.level_1.training`
16. **1 modules**
   - Chain: `layers.layer_0_core.level_10 -> layers.layer_0_core.level_10`
   - Nodes: `layers.layer_0_core.level_10`
17. **1 modules**
   - Chain: `layers.layer_0_core.level_2 -> layers.layer_0_core.level_2`
   - Nodes: `layers.layer_0_core.level_2`
18. **1 modules**
   - Chain: `layers.layer_0_core.level_2.training -> layers.layer_0_core.level_2.training`
   - Nodes: `layers.layer_0_core.level_2.training`
19. **1 modules**
   - Chain: `layers.layer_0_core.level_2.vision_transforms -> layers.layer_0_core.level_2.vision_transforms`
   - Nodes: `layers.layer_0_core.level_2.vision_transforms`
20. **1 modules**
   - Chain: `layers.layer_0_core.level_3 -> layers.layer_0_core.level_3`
   - Nodes: `layers.layer_0_core.level_3`
21. **1 modules**
   - Chain: `layers.layer_0_core.level_4 -> layers.layer_0_core.level_4`
   - Nodes: `layers.layer_0_core.level_4`
22. **1 modules**
   - Chain: `layers.layer_0_core.level_5 -> layers.layer_0_core.level_5`
   - Nodes: `layers.layer_0_core.level_5`
23. **1 modules**
   - Chain: `layers.layer_0_core.level_5.data_structure -> layers.layer_0_core.level_5.data_structure`
   - Nodes: `layers.layer_0_core.level_5.data_structure`
24. **1 modules**
   - Chain: `layers.layer_0_core.level_6 -> layers.layer_0_core.level_6`
   - Nodes: `layers.layer_0_core.level_6`
25. **1 modules**
   - Chain: `layers.layer_0_core.level_7 -> layers.layer_0_core.level_7`
   - Nodes: `layers.layer_0_core.level_7`
26. **1 modules**
   - Chain: `layers.layer_0_core.level_8 -> layers.layer_0_core.level_8`
   - Nodes: `layers.layer_0_core.level_8`
27. **1 modules**
   - Chain: `layers.layer_0_core.level_9 -> layers.layer_0_core.level_9`
   - Nodes: `layers.layer_0_core.level_9`
28. **1 modules**
   - Chain: `layers.layer_1_competition -> layers.layer_1_competition`
   - Nodes: `layers.layer_1_competition`
29. **1 modules**
   - Chain: `layers.layer_1_competition.level_0_infra -> layers.layer_1_competition.level_0_infra`
   - Nodes: `layers.layer_1_competition.level_0_infra`
30. **1 modules**
   - Chain: `layers.layer_1_competition.level_0_infra.level_0 -> layers.layer_1_competition.level_0_infra.level_0`
   - Nodes: `layers.layer_1_competition.level_0_infra.level_0`
31. **1 modules**
   - Chain: `layers.layer_1_competition.level_0_infra.level_1 -> layers.layer_1_competition.level_0_infra.level_1`
   - Nodes: `layers.layer_1_competition.level_0_infra.level_1`
32. **1 modules**
   - Chain: `layers.layer_1_competition.level_0_infra.level_2 -> layers.layer_1_competition.level_0_infra.level_2`
   - Nodes: `layers.layer_1_competition.level_0_infra.level_2`
33. **1 modules**
   - Chain: `layers.layer_1_competition.level_0_infra.level_3 -> layers.layer_1_competition.level_0_infra.level_3`
   - Nodes: `layers.layer_1_competition.level_0_infra.level_3`
34. **1 modules**
   - Chain: `layers.layer_1_competition.level_0_infra.level_4 -> layers.layer_1_competition.level_0_infra.level_4`
   - Nodes: `layers.layer_1_competition.level_0_infra.level_4`
35. **1 modules**
   - Chain: `layers.layer_1_competition.level_0_infra.level_5 -> layers.layer_1_competition.level_0_infra.level_5`
   - Nodes: `layers.layer_1_competition.level_0_infra.level_5`
36. **1 modules**
   - Chain: `layers.layer_1_competition.level_0_infra.level_6 -> layers.layer_1_competition.level_0_infra.level_6`
   - Nodes: `layers.layer_1_competition.level_0_infra.level_6`
37. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl -> layers.layer_1_competition.level_1_impl`
   - Nodes: `layers.layer_1_competition.level_1_impl`
38. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2`
39. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0`
40. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1`
41. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.cli -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.cli`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.cli`
42. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2`
43. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3`
44. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4`
45. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6`
46. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7`
47. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_8 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_8`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_8`
48. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_cafa -> layers.layer_1_competition.level_1_impl.level_cafa`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_cafa`
49. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_csiro -> layers.layer_1_competition.level_1_impl.level_csiro`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_csiro`
50. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_rna3d -> layers.layer_1_competition.level_1_impl.level_rna3d`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_rna3d`
51. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_rna3d.level_2 -> layers.layer_1_competition.level_1_impl.level_rna3d.level_2`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_rna3d.level_2`
52. **1 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_rna3d.level_3 -> layers.layer_1_competition.level_1_impl.level_rna3d.level_3`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_rna3d.level_3`
53. **1 modules**
   - Chain: `layers.layer_2_devtools -> layers.layer_2_devtools`
   - Nodes: `layers.layer_2_devtools`
54. **1 modules**
   - Chain: `layers.layer_2_devtools.level_0_infra -> layers.layer_2_devtools.level_0_infra`
   - Nodes: `layers.layer_2_devtools.level_0_infra`
55. **1 modules**
   - Chain: `layers.layer_2_devtools.level_0_infra.level_0 -> layers.layer_2_devtools.level_0_infra.level_0`
   - Nodes: `layers.layer_2_devtools.level_0_infra.level_0`
56. **1 modules**
   - Chain: `layers.layer_2_devtools.level_0_infra.level_0.parse -> layers.layer_2_devtools.level_0_infra.level_0.parse`
   - Nodes: `layers.layer_2_devtools.level_0_infra.level_0.parse`
57. **1 modules**
   - Chain: `layers.layer_2_devtools.level_0_infra.level_0.validation -> layers.layer_2_devtools.level_0_infra.level_0.validation`
   - Nodes: `layers.layer_2_devtools.level_0_infra.level_0.validation`
58. **1 modules**
   - Chain: `layers.layer_2_devtools.level_0_infra.level_1 -> layers.layer_2_devtools.level_0_infra.level_1`
   - Nodes: `layers.layer_2_devtools.level_0_infra.level_1`
59. **1 modules**
   - Chain: `layers.layer_2_devtools.level_1_impl -> layers.layer_2_devtools.level_1_impl`
   - Nodes: `layers.layer_2_devtools.level_1_impl`
60. **1 modules**
   - Chain: `layers.layer_2_devtools.level_1_impl.level_0 -> layers.layer_2_devtools.level_1_impl.level_0`
   - Nodes: `layers.layer_2_devtools.level_1_impl.level_0`
61. **1 modules**
   - Chain: `layers.layer_2_devtools.level_1_impl.level_1 -> layers.layer_2_devtools.level_1_impl.level_1`
   - Nodes: `layers.layer_2_devtools.level_1_impl.level_1`
62. **1 modules**
   - Chain: `layers.layer_2_devtools.level_1_impl.level_2 -> layers.layer_2_devtools.level_1_impl.level_2`
   - Nodes: `layers.layer_2_devtools.level_1_impl.level_2`
63. **1 modules**
   - Chain: `layers.layer_2_devtools.level_1_impl.tests.integration -> layers.layer_2_devtools.level_1_impl.tests.integration`
   - Nodes: `layers.layer_2_devtools.level_1_impl.tests.integration`
64. **1 modules**
   - Chain: `layers.layer_2_devtools.level_1_impl.tests.unit -> layers.layer_2_devtools.level_1_impl.tests.unit`
   - Nodes: `layers.layer_2_devtools.level_1_impl.tests.unit`
65. **3 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.lm -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.lm.backend_config -> layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4, layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.lm, layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.lm.backend_config`
66. **4 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_csiro.level_5 -> layers.layer_1_competition.level_1_impl.level_csiro.level_5.handlers_training -> layers.layer_1_competition.level_1_impl.level_csiro.level_6 -> layers.layer_1_competition.level_1_impl.level_csiro.level_6.train_and_export_pipeline -> layers.layer_1_competition.level_1_impl.level_csiro.level_5`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_csiro.level_5, layers.layer_1_competition.level_1_impl.level_csiro.level_5.handlers_training, layers.layer_1_competition.level_1_impl.level_csiro.level_6, layers.layer_1_competition.level_1_impl.level_csiro.level_6.train_and_export_pipeline`
67. **4 modules**
   - Chain: `layers.layer_1_competition.level_1_impl.level_rna3d.level_2 -> layers.layer_1_competition.level_1_impl.level_rna3d.level_2.orchestration -> layers.layer_1_competition.level_1_impl.level_rna3d.level_2.orchestration.train_and_submit -> layers.layer_1_competition.level_1_impl.level_rna3d.level_3.training.pipeline -> layers.layer_1_competition.level_1_impl.level_rna3d.level_2`
   - Nodes: `layers.layer_1_competition.level_1_impl.level_rna3d.level_2, layers.layer_1_competition.level_1_impl.level_rna3d.level_2.orchestration, layers.layer_1_competition.level_1_impl.level_rna3d.level_2.orchestration.train_and_submit, layers.layer_1_competition.level_1_impl.level_rna3d.level_3.training.pipeline`
68. **35 modules**
   - Chain: `layers.layer_1_competition.level_0_infra.level_0 -> layers.layer_1_competition.level_0_infra.level_0.pipeline_logging -> layers.layer_1_competition.level_0_infra.level_1 -> layers.layer_1_competition.level_0_infra.level_1.commands -> layers.layer_1_competition.level_0_infra.level_1.commands.cross_validate -> layers.layer_1_competition.level_0_infra.level_0`
   - Nodes: `layers.layer_1_competition.level_0_infra.level_0, layers.layer_1_competition.level_0_infra.level_0.pipeline_logging, layers.layer_1_competition.level_0_infra.level_1, layers.layer_1_competition.level_0_infra.level_1.commands, layers.layer_1_competition.level_0_infra.level_1.commands.cross_validate, layers.layer_1_competition.level_0_infra.level_1.commands.export_model, layers.layer_1_competition.level_0_infra.level_1.commands.grid_search, layers.layer_1_competition.level_0_infra.level_1.commands.test, layers.layer_1_competition.level_0_infra.level_1.commands.train, layers.layer_1_competition.level_0_infra.level_1.commands.train_test, layers.layer_1_competition.level_0_infra.level_1.contest, layers.layer_1_competition.level_0_infra.level_1.contest.cli, layers.layer_1_competition.level_0_infra.level_1.contest.context, layers.layer_1_competition.level_0_infra.level_1.contest.data_loading, layers.layer_1_competition.level_0_infra.level_1.export, layers.layer_1_competition.level_0_infra.level_1.export.export_model_pipeline, layers.layer_1_competition.level_0_infra.level_1.export.feature_filename, layers.layer_1_competition.level_0_infra.level_1.export.metadata_builders, layers.layer_1_competition.level_0_infra.level_1.export.source_handlers, layers.layer_1_competition.level_0_infra.level_1.features, layers.layer_1_competition.level_0_infra.level_1.features.feature_extractor_factory, layers.layer_1_competition.level_0_infra.level_1.paths, layers.layer_1_competition.level_0_infra.level_1.paths.env_paths, layers.layer_1_competition.level_0_infra.level_1.paths.models, layers.layer_1_competition.level_0_infra.level_1.paths.output_roots, layers.layer_1_competition.level_0_infra.level_1.paths.path_utils, layers.layer_1_competition.level_0_infra.level_1.paths.runs, layers.layer_1_competition.level_0_infra.level_1.paths.submissions, layers.layer_1_competition.level_0_infra.level_1.ranking, layers.layer_1_competition.level_0_infra.level_1.ranking.candidate_guess_dicts, layers.layer_1_competition.level_0_infra.level_1.ranking.candidate_ranking, layers.layer_1_competition.level_0_infra.level_1.registry, layers.layer_1_competition.level_0_infra.level_1.registry.contest_registry, layers.layer_1_competition.level_0_infra.level_1.run_lifecycle, layers.layer_1_competition.level_0_infra.level_1.run_lifecycle.submit_metadata`

