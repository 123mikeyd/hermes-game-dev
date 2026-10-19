# Example tasks

These prompts are generic starting points, **not executed demonstrations or test results**.
Replace every project placeholder with an explicitly authorized absolute local path.
Do not paste secrets or use a home directory as a convenient project root.

## 1. Small Godot vertical slice

> Inspect my selected project at <absolute-local-project-directory>. Use
> game-dev-workflow to scope one room where a player collects a key, opens an exit,
> and can restart. Preserve the existing engine/version and unrelated work. Define
> acceptance first. Do not download assets or export a build without approval.

Suggested read-only calls:

```text
game_dev_inspect({"project_path": "<absolute-local-project-directory>"})
game_dev_checklist({"engine": "godot", "stage": "prototype"})
```

Expected workflow, not an observed result: inspect the main scene and inputs, fill
the acceptance template, implement a minimal loop, run focused checks, and enter
through the real menu. Record actual findings instead of copying a sample PASS.

## 2. Character asset review

> Inventory assets in <absolute-local-project-directory> with hashes limited to
> the default budget. Use game-dev-assets to prepare a plan for one walk animation.
> Preserve the native source, rig rest transforms, original full clip, and rights
> records. Show a candidate before installing it; controller movement owns travel.

```text
game_dev_asset_audit({"project_path": "<absolute-local-project-directory>", "sha256": true, "max_assets": 50})
```

Inventory/hashes do not inspect deformation. Next steps require an installed,
approved authoring tool, fresh reimport, actual engine review, and recorded approval.
Do not delete a duplicate asset simply because its bytes match another file.

## 3. Focused regression before a full suite

> Use game-dev-verification to reproduce a pause/retry bug in my selected project.
> Read the runner and output sinks first. Run the focused check in isolation; reserve
> a coherent source revision before the final suite. Keep baseline failures and
> harness faults separate, and do not disturb my running editor or real saves.

Use the playtest template to track real Start, pause, retry, and input restoration.
Record interrupted attempts; count unique checks separately from retries.

## 4. Browser release handoff

> Prepare a release checklist for the selected web target. Do not publish or start
> a public tunnel. Identify hosting, audio/input, touch, memory, and real-device
> gates. Keep native success separate from browser coverage. Leave unavailable
> device checks marked NOT RUN.

```text
game_dev_checklist({"engine": "web", "stage": "release"})
```

Use the release-handoff template only after obtaining actual build identities and
evidence. The checklist tool does not build, upload, or verify any artifact.
