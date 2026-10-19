"""Exercise the documented registration surface without a Hermes dependency."""
import importlib
import json
from pathlib import Path
import os
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))


class FakeContext:
    def __init__(self):
        self.tools = {}
        self.skills = {}

    def register_tool(self, *, name, toolset, schema, handler):
        if name in self.tools:
            raise AssertionError("duplicate registration")
        self.tools[name] = {"toolset": toolset, "schema": schema, "handler": handler}

    def register_skill(self, name, path):
        self.skills[name] = Path(path)


class RegistrationTests(unittest.TestCase):
    def test_register_exact_tools_and_available_bundled_skills(self):
        self.assertTrue((ROOT / "__init__.py").exists(), "native registration is missing")
        plugin = importlib.import_module(ROOT.name)
        ctx = FakeContext()
        plugin.register(ctx)
        expected = {"game_dev_inspect", "game_dev_asset_audit", "game_dev_checklist"}
        self.assertEqual(set(ctx.tools), expected)
        manifest = (ROOT / "plugin.yaml").read_text(encoding="utf-8")
        for name, tool in ctx.tools.items():
            self.assertIn("  - " + name, manifest)
            self.assertEqual(tool["schema"]["name"], name)
            self.assertEqual(tool["toolset"], "game-dev")
            result = json.loads(tool["handler"]({}, task_id="compatibility"))
            self.assertIn("ok", result)
        skills = ROOT / "skills"
        expected_skills = {"game-dev-workflow", "game-dev-assets", "game-dev-verification"}
        self.assertEqual({p.parent.name for p in skills.glob("*/SKILL.md")}, expected_skills)
        self.assertEqual(set(ctx.skills), expected_skills)
        for path in ctx.skills.values():
            self.assertTrue(path.is_file())

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_registration_refuses_junction_skill_root(self):
        import _winapi
        from unittest.mock import patch
        plugin = importlib.import_module(ROOT.name)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            package = root / "package"
            package.mkdir()
            outside = root / "outside"
            (outside / "untrusted").mkdir(parents=True)
            (outside / "untrusted/SKILL.md").write_text("fixture", encoding="utf-8")
            junction = package / "skills"
            _winapi.CreateJunction(str(outside), str(junction))
            try:
                with patch.object(plugin, "__file__", str(package / "__init__.py")):
                    ctx = FakeContext()
                    plugin.register(ctx)
                self.assertEqual(ctx.skills, {})
            finally:
                junction.rmdir()


if __name__ == "__main__":
    unittest.main()
