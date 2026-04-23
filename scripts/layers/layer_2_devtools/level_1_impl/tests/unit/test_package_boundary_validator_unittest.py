import importlib.util
import sys
import types
import unittest
from pathlib import Path


_SCRIPTS = Path(__file__).resolve().parents[5]

if "layers" not in sys.modules:
    pkg = types.ModuleType("layers")
    pkg.__path__ = [str(_SCRIPTS / "layers")]
    sys.modules["layers"] = pkg

# Bypass auto-generated __init__.py side effects by pre-seeding packages.
for name, rel in [
    ("layers.layer_2_devtools", ["layers", "layer_2_devtools"]),
    ("layers.layer_2_devtools.level_0_infra", ["layers", "layer_2_devtools", "level_0_infra"]),
    ("layers.layer_2_devtools.level_0_infra.level_0", ["layers", "layer_2_devtools", "level_0_infra", "level_0"]),
    ("layers.layer_2_devtools.level_1_impl", ["layers", "layer_2_devtools", "level_1_impl"]),
    ("layers.layer_2_devtools.level_1_impl.level_1", ["layers", "layer_2_devtools", "level_1_impl", "level_1"]),
    ("layers.layer_2_devtools.level_1_impl.level_1.composed", ["layers", "layer_2_devtools", "level_1_impl", "level_1", "composed"]),
]:
    if name not in sys.modules:
        p = types.ModuleType(name)
        p.__path__ = [str(_SCRIPTS.joinpath(*rel))]
        sys.modules[name] = p


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestPackageBoundaryClassifier(unittest.TestCase):
    def _load_classifier(self):
        # Load as package module so relative imports work.
        base = (
            _SCRIPTS
            / "layers"
            / "layer_2_devtools"
            / "level_0_infra"
            / "level_0"
            / "validation"
            / "boundaries"
        )
        _load_module_from_path(
            "layers.layer_2_devtools.level_0_infra.level_0.validation.boundaries.boundary_nodes",
            base / "boundary_nodes.py",
        )
        return _load_module_from_path(
            "layers.layer_2_devtools.level_0_infra.level_0.validation.boundaries.boundary_classifiers",
            base / "boundary_classifiers.py",
        )

    def test_classify_general_stack_levelN(self):
        mod = self._load_classifier()
        res = mod.classify_module_to_boundary("level_2.analysis.cv_analysis")
        self.assertIsNotNone(res.node)
        self.assertEqual(res.node.key, "general_level_2")

    def test_classify_general_stack_layers_namespace(self):
        mod = self._load_classifier()
        res = mod.classify_module_to_boundary("layers.layer_0_core.level_3.ensemble.create_meta_model")
        self.assertIsNotNone(res.node)
        self.assertEqual(res.node.key, "general_level_3")

    def test_classify_competition_infra(self):
        mod = self._load_classifier()
        res = mod.classify_module_to_boundary(
            "layers.layer_1_competition.level_0_infra.level_1.io.loaders"
        )
        self.assertIsNotNone(res.node)
        self.assertEqual(res.node.key, "competition_infra_level_1")

    def test_classify_contest(self):
        mod = self._load_classifier()
        res = mod.classify_module_to_boundary(
            "layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.foo.bar"
        )
        self.assertIsNotNone(res.node)
        self.assertEqual(res.node.key, "contest_level_arc_agi_2_level_2")

    def test_classify_devtools(self):
        mod = self._load_classifier()
        res = mod.classify_module_to_boundary(
            "layers.layer_2_devtools.level_0_infra.level_1.health_analyzers.import_analyzer"
        )
        self.assertIsNotNone(res.node)
        self.assertEqual(res.node.key, "devtools_infra_level_1")


class TestPackageBoundaryMarkdown(unittest.TestCase):
    def _load_ops(self):
        path = (
            _SCRIPTS
            / "layers"
            / "layer_2_devtools"
            / "level_1_impl"
            / "level_1"
            / "composed"
            / "package_boundary_validation_ops.py"
        )
        return _load_module_from_path(
            "layers.layer_2_devtools.level_1_impl.level_1.composed.package_boundary_validation_ops",
            path,
        )

    def test_markdown_is_deterministic(self):
        mod = self._load_ops()
        report = {
            "generated": "2026-01-01",
            "scripts_root": "/scripts",
            "scope_root": None,
            "files_scanned": 1,
            "nodes": [
                {"key": "general_level_1", "label": "general level_1", "sort_key": ["general", 1]},
                {"key": "general_level_0", "label": "general level_0", "sort_key": ["general", 0]},
            ],
            "node_keys": ["general_level_0", "general_level_1"],
            "edge_counts": {"general_level_1": {"general_level_0": 2}},
            "violations": {"total": 1, "upward": 1, "illegal_external": 0},
            "examples_by_pair": {
                "general_level_1::general_level_0": [
                    {
                        "source_file": "layers/layer_0_core/level_1/x.py",
                        "import_text": "import level_0",
                        "target_module": "level_0",
                    }
                ]
            },
        }
        md1 = mod.build_boundary_markdown(report)
        md2 = mod.build_boundary_markdown(report)
        self.assertEqual(md1, md2)
        self.assertIn("# Package Boundary Validation Report", md1)


if __name__ == "__main__":
    unittest.main()

