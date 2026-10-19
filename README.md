# Game Dev for Hermes

A standalone native Hermes plugin named **`game-dev`**: read-only project inspection tools plus practical skills for building, reviewing, and verifying games.

Godot-first development guidance, engine-aware checklists, and general asset/release discipline. The plugin uses **Python's standard library only**; it does not bundle or download an engine, editor, asset pack, or model.

## Install

In a Hermes terminal:

```text
hermes plugins install 123mikeyd/hermes-game-dev
hermes plugins list
```

Review the install scanner and consent prompts. If the plugin is disabled, enable it explicitly:

```text
hermes plugins enable game-dev
```

Start a new Hermes session if the current session does not expose the new tools or skills. Use `skills_list` to discover the registered qualified skill names, then `skill_view` to load one. This is a standalone community plugin; this README makes no claim of catalog acceptance or endorsement.

## Tools

| Tool | What it does | What it does not prove |
|---|---|---|
| `game_dev_inspect` | Bounded project inventory, engine-marker hints, and selected Godot main-scene/export-preset metadata | That the engine is installed, every dependency exists, or the game runs |
| `game_dev_asset_audit` | Bounded asset-extension inventory with sizes; optional budgeted SHA-256 and exact-byte duplicate groups | Asset quality, rig correctness, rights clearance, or safe deletion |
| `game_dev_checklist` | Unexecuted acceptance prompts for a selected engine and development stage | That any check has run or passed |

Inspection and audit require an **explicit absolute local `project_path`**. The directory can be outside the plugin installation; this is intentional access to the user's selected project. Use the smallest relevant directory, not a home directory or drive root.

Example tool arguments (replace the placeholder; it is not a literal usable path):

```json
{"project_path": "<absolute-local-project-directory>", "max_entries": 10000, "max_depth": 12}
```

For a checklist, no project path or filesystem read is required:

```json
{"engine": "godot", "stage": "prototype"}
```

Supported checklist engines: `godot`, `unity`, `unreal`, `web`, `generic`. Stages: `prototype`, `integration`, `release`. All generated check statuses begin as `not_run`.

See `docs/tool-reference.md` for bounds and interpretation, and `examples/README.md` for generic task prompts. Examples contain no fabricated test results.

## Three bundled skills

- **`game-dev-workflow`** — inspect the actual engine/project, define a vertical slice, implement one behavior, and prove the playable loop.
- **`game-dev-assets`** — preserve editable sources, obtain reference approval, inspect rig/rest transforms and root motion, verify export/import, and record rights/provenance.
- **`game-dev-verification`** — isolate focused tests and full suites, test real input/modes, retain evidence, and verify portable releases and browser limitations.

Each skill is a complete procedure with prerequisites, checkable steps, pitfalls, and verification—not a pointer to private skills. Templates ship beside their owning skills:

```text
skills/game-dev-workflow/templates/acceptance.md
skills/game-dev-assets/templates/asset-provenance.md
skills/game-dev-verification/templates/playtest.md
skills/game-dev-verification/templates/release-handoff.md
```

## Security and side effects

**Plugin tool handlers:** read-only; no network requests, credential-store reads, subprocesses, background jobs, engine execution, or project writes. They do not install packages, download assets, modify projects, launch editors, publish builds, or bypass approvals. Installing the plugin itself is a separate Hermes-managed operation that downloads/writes plugin files.

The tools skip hidden entries, common build/cache/dependency directories, known credential-like names, links/reparse points, hard-linked files, and special files. Root paths containing symlinks or reparse points are rejected. Budgets and truncation are reported; excluded or unexamined files are not certified safe. Name-based exclusions cannot detect a secret disguised as ordinary project data. Optional hashing reads bytes of selected assets within explicit limits.

Returned filenames, sizes, hashes, and selected metadata enter the Hermes conversation and may be processed by the configured model provider. Review the selected directory accordingly. These checks are **not an OS sandbox** against a hostile process changing the filesystem concurrently.

**Skills:** instructions for an agent using normal Hermes tools. Following a skill can involve approved source edits, builds, editor launches, tests, or publishing. Those are separate actions with their own scope and approvals; the plugin's read-only implementation does not make those actions read-only. No local active installation is required to read these files.

More detail: `docs/security-and-limitations.md`.

## Limits

- No full engine-editor integration, live scene bridge, or automatic gameplay testing.
- No engine installation, downloaded assets, automatic retargeting, or renderer access.
- Root marker detection is heuristic, especially for web projects; nested projects may need their own path.
- Asset auditing recognizes extensions; it does not parse models, archives, materials, or license documents.
- Hash equality identifies bytes, not interchangeable runtime references or safe cleanup.
- A checklist is a plan, not evidence. Headless tests do not establish visual quality or real-device playability.
- Godot command patterns must be checked against the installed version; other engines retain their own workflows.

## Credits and license

Created by **Mike (123mikeyd)** with **Hermes Agent**. MIT licensed; see `LICENSE`.

The toolkit's license does not relicense third-party games, assets, engines, or dependencies. Keep their original notices and redistribution restrictions.
