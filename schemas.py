"""JSON schemas for bounded, read-only tools. No Hermes imports needed."""
PROJECT = {
    "project_path": {"type": "string", "description": "Explicit absolute local project directory requested by the user. No implicit working directory, network paths, symlinks, or parent traversal."},
    "max_entries": {"type": "integer", "minimum": 1, "maximum": 50000, "default": 10000, "description": "Maximum directory entries examined; includes excluded entries. An overflowing directory is skipped entirely for deterministic results."},
    "max_depth": {"type": "integer", "minimum": 0, "maximum": 32, "default": 12, "description": "Maximum directory descent; zero inspects root files only."},
}
INSPECT = {
    "name": "game_dev_inspect",
    "description": "Read-only bounded summary of an explicitly requested local game project: engine root markers (Godot/Unity/Unreal/web), observed file sizes and extension counts, and allowlisted Godot main-scene/export-preset metadata. Skips hidden files, credentials, links, and build/cache folders. Never executes an engine or reads arbitrary source content. Results are observations, not verified playtests.",
    "parameters": {"type": "object", "properties": PROJECT, "required": ["project_path"], "additionalProperties": False},
}
ASSET_AUDIT = {
    "name": "game_dev_asset_audit",
    "description": "Read-only deterministic source-asset inventory for an explicitly requested local project. Lists allowlisted asset extensions, relative paths and byte sizes; optional bounded SHA256 detects byte-identical duplicates only among successfully hashed returned assets. Never deletes, writes, executes, connects to a network, parses assets, or expands archives. Explicitly reports truncation and skipped hashes. Credential/cache/hidden paths and links are excluded; this is not a hostile-filesystem sandbox.",
    "parameters": {
        "type": "object", "required": ["project_path"], "additionalProperties": False,
        "properties": {
            **PROJECT,
            "max_assets": {"type": "integer", "minimum": 1, "maximum": 500, "default": 100, "description": "Maximum returned assets; hashing applies only to returned rows."},
            "sha256": {"type": "boolean", "default": False, "description": "Opt in to reading asset bytes for SHA256 and duplicate groups."},
            "hash_budget_bytes": {"type": "integer", "minimum": 0, "maximum": 268435456, "default": 33554432, "description": "Total asset-read budget per call, including failed read attempts."},
            "max_hash_file_bytes": {"type": "integer", "minimum": 0, "maximum": 67108864, "default": 16777216, "description": "Per-asset read cap; larger files are inventoried but not hashed."},
        },
    },
}
CHECKLIST = {
    "name": "game_dev_checklist",
    "description": "Return a deterministic engine-specific acceptance/playtest checklist with required evidence and not_run status. Reads no project files and executes nothing. Use the bundled game-dev-workflow skill for project-specific planning instead of treating this checklist as execution evidence.",
    "parameters": {
        "type": "object", "additionalProperties": False,
        "properties": {
            "engine": {"type": "string", "enum": ["godot", "unity", "unreal", "web", "generic"], "default": "generic"},
            "stage": {"type": "string", "enum": ["prototype", "integration", "release"], "default": "prototype"},
        },
    },
}
