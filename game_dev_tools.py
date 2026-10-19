"""Read-only, bounded project observations. No engine or project code is run.

Filesystem safety is best effort against static links, not an OS sandbox against
concurrent hostile filesystem mutation. Only explicitly supplied absolute local
project paths are accepted. File contents are never returned wholesale.
"""
from collections import Counter
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import re
import stat

MAX_OUTPUT = 64000
EXCLUDED_DIRS = frozenset({
    "node_modules", "vendor", "build", "builds", "dist", "target", "out",
    "bin", "obj", "library", "temp", "logs", "intermediate", "saved",
    "deriveddatacache", "binaries", "__pycache__", "venv", "env",
    "coverage", "exports", "cache", "caches", "credentials", "secrets",
})
SECRET_PARTS = ("credential", "secret", "password", "token", "private_key", "private-key")
SECRET_NAMES = frozenset({"auth.json", "auth", "id_rsa", "id_ed25519", "id_dsa",
                          "export_credentials.cfg", "keychain", "keystore"})
SECRET_EXTS = frozenset({".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"})


def _excluded(name):
    low = name.casefold()
    return (low.startswith(".") or low in EXCLUDED_DIRS or low in SECRET_NAMES
            or any(word in low for word in SECRET_PARTS)
            or Path(low).suffix in SECRET_EXTS)


def _link(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _check_chain(path):
    for part in (path, *path.parents):
        if _link(part.lstat()):
            raise ValueError("Symlinks and reparse points are not accepted")


def _root(args):
    raw = args.get("project_path")
    if not isinstance(raw, str) or not raw.strip() or len(raw) > 4096:
        raise ValueError("project_path must be an explicit absolute local directory")
    if raw.startswith(("\\\\", "//")):
        raise ValueError("Network and device paths are not accepted")
    path = Path(raw)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("project_path must be absolute without parent traversal")
    # An explicit nested root must not bypass credential-directory exclusion.
    for part in path.parts[1:]:
        low = part.casefold()
        if (low.startswith(".") or low in SECRET_NAMES
                or any(word in low for word in SECRET_PARTS)):
            raise ValueError("Credential-like or hidden project path components are excluded")
    _check_chain(path)
    if not path.is_dir() or _excluded(path.name):
        raise ValueError("project_path must be an accessible, non-excluded directory")
    return path.resolve(strict=True)


def _integer(args, key, default, minimum, maximum):
    value = args.get(key, default)
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{key} must be an integer from {minimum} to {maximum}")
    return value


def _endpoint(fn):
    @wraps(fn)
    def handler(args, **kwargs):
        try:
            if not isinstance(args, dict):
                raise ValueError("Arguments must be an object")
            result = fn(args)
            encoded = json.dumps({"ok": True, **result}, ensure_ascii=True, sort_keys=True)
            if len(encoded) > MAX_OUTPUT:
                return json.dumps({"ok": False, "error": "Output limit exceeded; narrow the project or lower max_assets", "truncated": True})
            return encoded
        except ValueError as exc:
            return json.dumps({"ok": False, "error": str(exc)[:300]})
        except Exception as exc:
            # OS exception messages can contain arbitrary absolute paths; omit them.
            return json.dumps({"ok": False, "error": "Unable to complete read-only inspection", "error_type": type(exc).__name__})
    return handler


def _walk(root, args):
    limit = _integer(args, "max_entries", 10000, 1, 50000)
    depth_limit = _integer(args, "max_depth", 12, 0, 32)
    state = {"entries_examined": 0, "skipped": {}, "truncated": False, "truncation_reasons": []}
    skipped = Counter()
    files = []
    pending = [(root, 0)]

    def truncate(reason):
        state["truncated"] = True
        if reason not in state["truncation_reasons"]:
            state["truncation_reasons"].append(reason)

    while pending:
        directory, depth = pending.pop()
        remaining = limit - state["entries_examined"]
        if remaining <= 0:
            truncate("max_entries")
            break
        try:
            _check_chain(directory)
            # Do not materialize an unbounded directory, nor return an OS-order
            # dependent subset: skip the entire overflowing directory instead.
            with os.scandir(directory) as iterator:
                entries = []
                for entry in iterator:
                    if len(entries) == remaining:
                        truncate("max_entries")
                        entries = None
                        break
                    entries.append(entry)
            if entries is None:
                state["entries_examined"] = limit
                break
            state["entries_examined"] += len(entries)
            for entry in sorted(entries, key=lambda item: item.name):
                if _excluded(entry.name):
                    skipped["excluded_name"] += 1
                    continue
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                if len(relative) > 1024:
                    skipped["long_path"] += 1
                    truncate("path_length")
                    continue
                try:
                    # Windows DirEntry.stat may report st_nlink=0/st_ino=0.
                    # lstat requests real identity and hardlink information.
                    info = path.lstat()
                    if _link(info):
                        skipped["link_or_reparse"] += 1
                    elif stat.S_ISDIR(info.st_mode):
                        if depth >= depth_limit:
                            truncate("max_depth")
                        else:
                            pending.append((path, depth + 1))
                    elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                        files.append((relative, info.st_size))
                    else:
                        skipped["special_or_hardlink"] += 1
                except OSError:
                    skipped["unreadable"] += 1
                    truncate("unreadable_entry")
        except (OSError, ValueError):
            skipped["unreadable_directory"] += 1
            truncate("unreadable_directory")
    state["skipped"] = dict(sorted(skipped.items()))
    return sorted(files), state


def _read(root, relative, limit):
    path = root / relative
    path.relative_to(root)
    if any(_excluded(part) for part in Path(relative).parts):
        raise ValueError("Excluded file")
    _check_chain(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > limit:
        raise ValueError("File is not a single-link regular file within the read budget")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        current = os.fstat(stream.fileno())
        if (current.st_dev, current.st_ino, current.st_size) != (before.st_dev, before.st_ino, before.st_size):
            raise ValueError("File changed before reading")
        if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1:
            raise ValueError("Unsafe file type")
        _check_chain(path)
        data = stream.read(limit)
        after = os.fstat(stream.fileno())
        if len(data) != current.st_size or (after.st_size, after.st_mtime_ns) != (current.st_size, current.st_mtime_ns):
            raise ValueError("File changed during reading or exceeded budget")
    return data


def _godot(root, names):
    result = {"main_scene": None, "export_presets": [], "metadata_warnings": []}
    for filename in ("project.godot", "export_presets.cfg"):
        if filename not in names:
            continue
        try:
            text = _read(root, filename, 262144).decode("utf-8-sig", errors="replace")
            section = ""
            presets = {}
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    section = line[1:-1]
                elif "=" in line and not line.startswith((";", "#")):
                    key, value = (item.strip() for item in line.split("=", 1))
                    value = value.strip('"')
                    selected = ((filename == "project.godot" and section == "application" and key == "run/main_scene")
                                or (filename == "export_presets.cfg" and re.fullmatch(r"preset\.\d+", section)
                                    and key in {"name", "platform", "runnable"}))
                    if selected and len(value) > 256:
                        if "metadata_value_limit" not in result["metadata_warnings"]:
                            result["metadata_warnings"].append("metadata_value_limit")
                        value = value[:256]
                    if filename == "project.godot" and section == "application" and key == "run/main_scene":
                        result["main_scene"] = value
                    elif filename == "export_presets.cfg" and re.fullmatch(r"preset\.\d+", section) and key in {"name", "platform", "runnable"}:
                        if section not in presets and len(presets) >= 32:
                            if "preset_limit" not in result["metadata_warnings"]:
                                result["metadata_warnings"].append("preset_limit")
                            continue
                        presets.setdefault(section, {"section": section})[key] = value
            result["export_presets"] += list(presets.values())
        except (OSError, ValueError):
            result["metadata_warnings"].append(filename + ": unreadable, changed, linked, or above 256 KiB")
    return result


ASSET_TYPES = {
    "image": (".png", ".jpg", ".jpeg", ".webp", ".svg", ".tga", ".bmp", ".exr", ".hdr", ".psd", ".aseprite"),
    "model": (".blend", ".fbx", ".gltf", ".glb", ".obj", ".dae", ".usd", ".usdz"),
    "audio": (".wav", ".ogg", ".mp3", ".flac", ".aiff", ".m4a"),
    "video": (".mp4", ".webm", ".mov"),
    "font": (".ttf", ".otf", ".woff", ".woff2"),
    "engine_asset": (".tscn", ".tres", ".scn", ".res", ".unity", ".prefab", ".asset", ".mat", ".anim", ".uasset", ".umap"),
}
ASSET_EXTENSIONS = {extension: kind for kind, extensions in ASSET_TYPES.items() for extension in extensions}


@_endpoint
def game_dev_asset_audit(args):
    """Inventory source assets; optional hashes compare bytes, not visual identity."""
    root = _root(args)
    maximum = _integer(args, "max_assets", 100, 1, 500)
    budget = _integer(args, "hash_budget_bytes", 33554432, 0, 268435456)
    file_budget = _integer(args, "max_hash_file_bytes", 16777216, 0, 67108864)
    hashing = args.get("sha256", False)
    if type(hashing) is not bool:
        raise ValueError("sha256 must be boolean")
    files, state = _walk(root, args)
    matches = [(name, size) for name, size in files if Path(name).suffix.lower() in ASSET_EXTENSIONS]
    rows = []
    hashes = {}
    bytes_read = 0
    for name, size in matches[:maximum]:
        row = {"path": name, "bytes": size, "kind": ASSET_EXTENSIONS[Path(name).suffix.lower()]}
        if hashing:
            if size > file_budget:
                row["hash_status"] = "file_budget_exceeded"
            elif size > budget - bytes_read:
                row["hash_status"] = "total_budget_exceeded"
            else:
                # Charge the full allowed attempt, including a failed read, so
                # changing/unreadable files cannot evade the total I/O budget.
                allowed = min(file_budget, budget - bytes_read, size)
                bytes_read += allowed
                try:
                    digest = hashlib.sha256(_read(root, name, allowed)).hexdigest()
                    row.update(sha256=digest, hash_status="hashed")
                    hashes.setdefault((digest, size), []).append(name)
                except (OSError, ValueError):
                    row["hash_status"] = "unreadable_or_changed"
        rows.append(row)
    if len(matches) > maximum:
        state["truncated"] = True
        state["truncation_reasons"].append("max_assets")
    incomplete_hashes = hashing and any(row.get("hash_status") != "hashed" for row in rows)
    if incomplete_hashes:
        state["truncated"] = True
        state["truncation_reasons"].append("hashes_incomplete")
    duplicates = [{"sha256": digest, "bytes_each": size, "paths": paths,
                   "reclaimable_bytes": size * (len(paths) - 1)}
                  for (digest, size), paths in sorted(hashes.items()) if len(paths) > 1]
    return {**state, "assets": rows, "asset_count_observed": len(matches), "assets_returned": len(rows),
            "asset_bytes_observed": sum(size for _, size in matches), "hashes_requested": hashing,
            "hash_bytes_budget_charged": bytes_read, "duplicates": duplicates,
            "duplicate_scope": "successfully hashed returned assets only; identical bytes, not safe-to-delete advice",
            "inventory_scope": "allowlisted source extensions; no archives expanded or asset formats parsed"}


ENGINE_CHECKS = {
    "godot": [
        ("startup", "Run the configured main scene and verify input actions and missing-resource errors.", "Startup log and a main-scene interaction recording."),
        ("imports", "Open the project in the intended Godot version and verify imported assets, collision layers, and scene references.", "Engine version, import log, and collision test results."),
        ("export", "Export using the intended preset and launch that artifact outside the editor.", "Preset, export log, artifact hash, and standalone launch evidence."),
    ],
    "unity": [
        ("startup", "Enter Play Mode from the intended first scene; verify input bindings and console errors.", "Editor version, startup scene, and Play Mode log."),
        ("imports", "Verify GUID references, missing scripts, animation transitions, and collision layers after import.", "Import warnings and focused reference/physics test results."),
        ("export", "Build the intended scene list and target, then launch the player outside the editor.", "Build configuration, build log, artifact hash, and player log."),
    ],
    "unreal": [
        ("startup", "Launch the intended default map and game mode; verify possession, input, and logs.", "Engine version, map, game mode, and play-session log."),
        ("imports", "Verify asset references, collision channels, animation transitions, and Blueprint compile results.", "Reference review and focused collision/animation evidence."),
        ("export", "Cook/package the intended maps and target; launch the packaged game separately.", "Packaging configuration, log, artifact hash, and standalone run evidence."),
    ],
    "web": [
        ("startup", "Open the served game in the target browser; verify console errors and missing requests.", "Browser version, URL, console log, and network failure list."),
        ("imports", "Verify resource URLs, filename case, input focus, resizing, and user-gesture audio startup.", "Input/resize/audio observations and missing-resource results."),
        ("export", "Test the deployed build on a clean browser profile and the intended mobile device when applicable.", "Build identifier, browser/device matrix, load times, and interaction recording."),
    ],
    "generic": [
        ("startup", "Launch the intended entry point and exercise one complete core loop.", "Runtime version, launch log, and core-loop recording."),
        ("imports", "Review source asset references, controls, collision rules, and animation transitions.", "Reference and focused interaction test results."),
        ("export", "Launch the distributable on a clean target environment without development tools.", "Build procedure, artifact hash, and clean-environment evidence."),
    ],
}
COMMON_CHECKS = [
    ("scope", "Write one observable acceptance criterion and explicit non-goals for this change.", "Approved scope and pass/fail criterion."),
    ("core_loop", "Play start, success, failure, restart, pause, and return-to-menu paths that exist in this game.", "Steps, expected/actual behavior, and reproduction details for failures."),
    ("readability", "Check camera framing, readable UI, audiovisual cues, and control discoverability at target resolution.", "Screenshots or video at the intended resolution and input device."),
    ("performance", "Measure frame time and memory during representative worst-case gameplay against an explicit budget.", "Hardware, scenario, duration, measured values, and budget comparison."),
]


@_endpoint
def game_dev_checklist(args):
    """Return acceptance prompts, never fabricated verification results."""
    engine = args.get("engine", "generic")
    stage = args.get("stage", "prototype")
    if not isinstance(engine, str) or engine not in ENGINE_CHECKS:
        raise ValueError("engine must be godot, unity, unreal, web, or generic")
    if not isinstance(stage, str) or stage not in {"prototype", "integration", "release"}:
        raise ValueError("stage must be prototype, integration, or release")
    selected = [("common." + key, action, evidence) for key, action, evidence in COMMON_CHECKS]
    selected += [(engine + "." + key, action, evidence) for key, action, evidence in ENGINE_CHECKS[engine]
                 if key != "export" or stage == "release"]
    if stage in {"integration", "release"}:
        selected.append(("common.regression", "Repeat the previously passing interactions affected by this change.", "Baseline, changed files, regression cases, and actual outcomes."))
    if stage == "release":
        selected.append(("common.delivery", "Check asset licenses, redistribution scope, save compatibility, and rollback/recovery instructions.", "License inventory, delivered file list, and recovery procedure."))
    return {"engine": engine, "stage": stage, "executed": False,
            "checks": [{"id": key, "action": action, "evidence_required": evidence, "status": "not_run"}
                       for key, action, evidence in selected],
            "note": "Suggested acceptance checklist only. Adapt to the project; no files read, commands run, or tests verified."}


@_endpoint
def game_dev_inspect(args):
    """Summarize a supplied project without importing or executing it."""
    root = _root(args)
    files, state = _walk(root, args)
    names = {name for name, _ in files}
    engines = []
    if "project.godot" in names:
        engines.append("godot")
    if "ProjectSettings/ProjectVersion.txt" in names:
        engines.append("unity")
    if any("/" not in name and name.endswith(".uproject") for name in names):
        engines.append("unreal")
    if "package.json" in names or "index.html" in names:
        engines.append("web")
    counts = Counter(Path(name).suffix.lower() or "(none)" for name, _ in files)
    result = {**state, "engines": engines, "engine_detection": "root markers; web markers are heuristic",
              "file_count": len(files), "total_bytes": sum(size for _, size in files),
              "extensions": dict(counts.most_common(64)), "counts_scope": "observed non-excluded files only"}
    if len(counts) > 64:
        result["truncated"] = True
        result["truncation_reasons"].append("extension_limit")
    if "godot" in engines:
        result["godot"] = _godot(root, names)
        if result["godot"]["metadata_warnings"]:
            result["truncated"] = True
            result["truncation_reasons"].append("metadata_incomplete")
    return result
