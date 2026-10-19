"""Stdlib-only regression tests; fixtures never touch a real project."""
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # macOS temporary roots may be reached through /var -> /private/var.
        # The tool intentionally rejects symlink ancestors; use the real root.
        self.root = Path(self.temp.name).resolve()

    def write(self, name, data=b"fixture"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def call(self, name, **args):
        module = importlib.import_module("game_dev_tools")
        result = getattr(module, name)({"project_path": str(self.root), **args}, task_id="test")
        self.assertIsInstance(result, str)
        return json.loads(result)

    def test_inspect_godot_metadata_and_counts(self):
        self.assertTrue((ROOT / "game_dev_tools.py").exists(), "inspection implementation is missing")
        self.write("project.godot", b'[application]\nrun/main_scene="res://main.tscn"\n')
        self.write("main.tscn")
        self.write("export_presets.cfg", b'[preset.0]\nname="Desktop"\nplatform="Linux"\nrunnable=true\n[preset.0.options]\nsecret="DO_NOT_RETURN"\n')
        result = self.call("game_dev_inspect")
        self.assertTrue(result["ok"])
        self.assertEqual(result["engines"], ["godot"])
        self.assertEqual(result["file_count"], 3)
        self.assertEqual(result["godot"]["main_scene"], "res://main.tscn")
        self.assertEqual(result["godot"]["export_presets"], [{"section": "preset.0", "name": "Desktop", "platform": "Linux", "runnable": "true"}])
        self.assertNotIn("DO_NOT_RETURN", json.dumps(result))
        self.assertFalse(result["truncated"])

    def test_asset_inventory_hashes_and_duplicates(self):
        module = importlib.import_module("game_dev_tools")
        self.assertTrue(hasattr(module, "game_dev_asset_audit"), "asset audit is missing")
        self.write("z.png", b"same")
        self.write("a.png", b"same")
        self.write("b.wav", b"other")
        self.write("code.py", b"not an asset")
        plain = self.call("game_dev_asset_audit")
        self.assertEqual([x["path"] for x in plain["assets"]], ["a.png", "b.wav", "z.png"])
        self.assertEqual(plain["duplicates"], [])
        self.assertFalse(plain["hashes_requested"])
        hashed = self.call("game_dev_asset_audit", sha256=True)
        self.assertEqual(hashed["duplicates"][0]["paths"], ["a.png", "z.png"])
        self.assertEqual(hashed["duplicates"][0]["reclaimable_bytes"], 4)
        self.assertEqual(hashed["assets"][0]["sha256"], __import__("hashlib").sha256(b"same").hexdigest())
        self.assertEqual(hashed, self.call("game_dev_asset_audit", sha256=True))

    def test_checklist_is_engine_specific_and_never_claims_execution(self):
        module = importlib.import_module("game_dev_tools")
        self.assertTrue(hasattr(module, "game_dev_checklist"), "checklist is missing")
        for engine in ("godot", "unity", "unreal", "web", "generic"):
            result = json.loads(module.game_dev_checklist({"engine": engine, "stage": "release"}))
            self.assertTrue(result["ok"])
            self.assertFalse(result["executed"])
            self.assertTrue(all(item["status"] == "not_run" for item in result["checks"]))
            self.assertTrue(any(item["id"].startswith(engine + ".") for item in result["checks"]))
        self.assertFalse(json.loads(module.game_dev_checklist({"engine": "madeup"}))["ok"])

    def test_rejects_sensitive_ancestor_even_when_root_is_nested(self):
        self.write("credentials/nested/art.png")
        result = self.call("game_dev_asset_audit", project_path=str(self.root / "credentials/nested"), sha256=True)
        self.assertFalse(result["ok"])

    def test_explicit_path_and_argument_validation(self):
        module = importlib.import_module("game_dev_tools")
        for args in ({}, {"project_path": "."}, {"project_path": "../elsewhere"},
                     {"project_path": "//server/share"}, {"project_path": str(self.root / "missing")},
                     {"project_path": str(self.root / ".." / self.root.name)},
                     {"project_path": str(self.root), "max_entries": True},
                     {"project_path": str(self.root), "max_entries": 0},
                     {"project_path": str(self.root), "max_depth": 33}, None, []):
            with self.subTest(args=args):
                self.assertFalse(json.loads(module.game_dev_inspect(args))["ok"])
        self.assertFalse(self.call("game_dev_asset_audit", sha256="yes")["ok"])
        self.assertFalse(self.call("game_dev_asset_audit", max_assets=501)["ok"])

    def test_cache_and_credential_exclusions(self):
        self.write("good.png")
        for name in (".env", "auth.json", "export_credentials.cfg", "private_key.png", "secrets.png",
                     "token.wav", ".ssh/key.png", "credentials/art.png", ".git/art.png",
                     ".godot/art.png", "Library/art.png", "node_modules/art.png", "build/art.png"):
            self.write(name, b"DO_NOT_READ")
        result = self.call("game_dev_asset_audit", sha256=True)
        self.assertEqual([row["path"] for row in result["assets"]], ["good.png"])
        self.assertEqual(self.call("game_dev_inspect")["file_count"], 1)
        self.assertNotIn("DO_NOT_READ", json.dumps(result))

    def test_no_content_reads_without_hash_opt_in(self):
        from unittest.mock import patch
        self.write("art.png")
        self.write("package.json", b"not parsed or executed")
        with patch("game_dev_tools._read", side_effect=AssertionError("unexpected content read")):
            self.assertTrue(self.call("game_dev_asset_audit")["ok"])
            self.assertEqual(self.call("game_dev_inspect")["engines"], ["web"])

    def test_entry_budget_is_bounded_and_explicit(self):
        for number in range(10):
            self.write(f"{number}.png")
        result = self.call("game_dev_asset_audit", max_entries=3)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["entries_examined"], 3)
        self.assertEqual(result["assets"], [])
        self.assertIn("max_entries", result["truncation_reasons"])
        self.assertEqual(result, self.call("game_dev_asset_audit", max_entries=3))

    def test_depth_budget_and_asset_budget(self):
        self.write("a.png")
        self.write("b.png")
        self.write("nested/c.png")
        result = self.call("game_dev_asset_audit", max_depth=0, max_assets=1)
        self.assertEqual(result["asset_count_observed"], 2)
        self.assertEqual(result["assets_returned"], 1)
        self.assertEqual(result["assets"][0]["path"], "a.png")
        self.assertEqual(set(result["truncation_reasons"]), {"max_depth", "max_assets"})

    def test_hash_budgets_and_duplicate_scope(self):
        self.write("a.png", b"aaaa")
        self.write("b.png", b"aaaa")
        self.write("c.png", b"longer")
        result = self.call("game_dev_asset_audit", sha256=True, hash_budget_bytes=4, max_hash_file_bytes=5)
        self.assertEqual([r["hash_status"] for r in result["assets"]], ["hashed", "total_budget_exceeded", "file_budget_exceeded"])
        self.assertEqual(result["hash_bytes_budget_charged"], 4)
        self.assertEqual(result["duplicates"], [])
        self.assertTrue(result["truncated"])

    def test_static_symlink_escape_and_link_root_are_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside)
            (target / "outside.png").write_bytes(b"outside")
            link = self.root / "escape"
            try:
                link.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest("OS cannot create symlink: " + type(exc).__name__)
            self.assertEqual(self.call("game_dev_asset_audit", sha256=True)["assets"], [])
            self.assertFalse(self.call("game_dev_inspect", project_path=str(link))["ok"])
            (target / "nested").mkdir()
            self.assertFalse(self.call("game_dev_inspect", project_path=str(link / "nested"))["ok"])

    def test_hardlinked_files_are_skipped(self):
        target = self.write("a.png")
        try:
            os.link(target, self.root / "hard.png")
        except (OSError, NotImplementedError) as exc:
            self.skipTest("OS cannot create hardlink: " + type(exc).__name__)
        self.assertEqual(self.call("game_dev_asset_audit", sha256=True)["assets"], [])

    def test_file_symlink_is_skipped(self):
        target = self.write("target.png")
        try:
            (self.root / "soft.png").symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("OS cannot create symlink: " + type(exc).__name__)
        result = self.call("game_dev_asset_audit", sha256=True)
        self.assertEqual([row["path"] for row in result["assets"]], ["target.png"])

    def test_godot_metadata_limit_and_allowlist(self):
        self.write("project.godot", b"x" * 262145)
        result = self.call("game_dev_inspect")
        self.assertTrue(result["truncated"])
        self.assertIsNone(result["godot"]["main_scene"])
        self.assertIn("metadata_incomplete", result["truncation_reasons"])

    def test_engine_markers_and_no_code_execution(self):
        self.write("ProjectSettings/ProjectVersion.txt")
        self.write("sample.uproject")
        self.write("index.html")
        self.write("package.json", b'{"scripts":{"test":"must never execute"}}')
        self.assertEqual(self.call("game_dev_inspect")["engines"], ["unity", "unreal", "web"])

    def test_long_extensions_are_not_silently_merged(self):
        first = "." + "a" * 40 + "x"
        second = "." + "a" * 40 + "y"
        self.write("one" + first)
        self.write("two" + second)
        self.assertEqual(self.call("game_dev_inspect")["extensions"], {first: 1, second: 1})

    def test_hash_read_never_requests_more_than_budget(self):
        from unittest.mock import patch
        module = importlib.import_module("game_dev_tools")
        self.write("a.png", b"abcd")
        original_fdopen = os.fdopen
        requested = []

        class TrackedStream:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.stream.close()
            def fileno(self):
                return self.stream.fileno()
            def read(self, amount):
                requested.append(amount)
                return self.stream.read(amount)

        with patch("game_dev_tools.os.fdopen", side_effect=lambda *a, **kw: TrackedStream(original_fdopen(*a, **kw))):
            self.assertEqual(module._read(self.root, "a.png", 4), b"abcd")
        self.assertLessEqual(sum(requested), 4)

    def test_godot_long_value_truncation_is_explicit(self):
        self.write("project.godot", ('[application]\nrun/main_scene="' + 'x' * 300 + '"\n').encode())
        result = self.call("game_dev_inspect")
        self.assertTrue(result["truncated"])
        self.assertIn("metadata_value_limit", result["godot"]["metadata_warnings"])

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_windows_junction_escape(self):
        import _winapi  # stdlib Windows fixture helper; never used by plugin tools
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside).resolve()
            (target / "outside.png").write_bytes(b"outside")
            (target / "nested").mkdir()
            link = self.root / "junction"
            _winapi.CreateJunction(str(target), str(link))
            self.addCleanup(lambda: link.rmdir() if link.exists() else None)
            self.assertEqual(self.call("game_dev_asset_audit", sha256=True)["assets"], [])
            self.assertFalse(self.call("game_dev_inspect", project_path=str(link))["ok"])
            self.assertFalse(self.call("game_dev_inspect", project_path=str(link / "nested"))["ok"])
            link.rmdir()

    def test_read_errors_return_json_without_paths(self):
        from unittest.mock import patch
        with patch("game_dev_tools._root", side_effect=PermissionError("private-location")):
            result = self.call("game_dev_inspect")
        self.assertFalse(result["ok"])
        self.assertNotIn("private-location", json.dumps(result))

    def test_output_is_bounded(self):
        module = importlib.import_module("game_dev_tools")
        from unittest.mock import patch
        huge = {"oversized": "x" * (module.MAX_OUTPUT + 1)}
        with patch("game_dev_tools._walk", return_value=([], huge)):
            raw = module.game_dev_inspect({"project_path": str(self.root)})
        self.assertLessEqual(len(raw), module.MAX_OUTPUT)
        self.assertTrue(json.loads(raw)["truncated"])


if __name__ == "__main__":
    unittest.main()
