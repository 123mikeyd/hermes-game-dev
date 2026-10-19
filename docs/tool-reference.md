# Tool reference

These are read-only handlers. Their schemas in the installed plugin are authoritative.
Results are JSON strings with an `ok` flag; an error is not an empty successful audit.

## Shared project traversal

`game_dev_inspect` and `game_dev_asset_audit` require `project_path`: an explicit
absolute local directory, without parent traversal. Network/device path prefixes,
symlink/reparse-point roots or ancestors, and excluded root names are rejected.

| Argument | Default | Allowed range |
|---|---:|---:|
| `max_entries` | 10000 | 1–50000 |
| `max_depth` | 12 | 0–32 |

The entry budget includes examined directory entries, not just returned files.
Traversal skips hidden names, common dependency/build/cache directories,
credential-like names, links/reparse points, special files, and hard-linked files.
A directory that overflows the remaining entry budget is not partially reported.
These restrictions can omit legitimate assets; choose a narrower project directory
rather than treating the observed totals as a complete disk inventory.

Inspect `truncated`, `truncation_reasons`, `skipped`, and scope descriptions before
interpreting totals. Output is bounded; an excessive result returns an error asking
you to narrow the project or lower the asset limit. A quiet result is not certification.

## `game_dev_inspect`

Recognizes root markers for Godot, Unity, Unreal, and web projects. It reports
observed file/byte counts and extension counts. Multiple engine hints are possible.
`package.json` and `index.html` are web hints, not proof of a game framework.

For Godot, selected metadata is extracted from `project.godot` and
`export_presets.cfg`: main-scene value and preset name/platform/runnable fields.
Each metadata file has a 256 KiB read limit; metadata warnings make the result
incomplete. It does not resolve scene UIDs, execute scripts, or validate exports.
It does not read `export_credentials.cfg` or return whole configuration files.

## `game_dev_asset_audit`

Recognizes source image, model, audio, video, font, and engine-asset extensions.
It inventories metadata, not asset internals. No archives are expanded.

| Argument | Default | Allowed range |
|---|---:|---:|
| `max_assets` | 100 | 1–500 |
| `sha256` | false | boolean |
| `hash_budget_bytes` | 33554432 | 0–268435456 |
| `max_hash_file_bytes` | 16777216 | 0–67108864 |

With `sha256: true`, successful bounded reads yield SHA-256 values. Check each
`hash_status`; budgets, unreadable files, and files changing during reads can leave
hashes incomplete. Hash budget accounting includes attempted reads, not merely
successful hashes. Duplicate groups cover only successfully hashed returned assets.

`asset_count_observed` is the count found within traversal scope;
`assets_returned` can be lower due to `max_assets`. Observed byte totals are not
package download sizes or decoded memory usage. `reclaimable_bytes` is arithmetic
for identical returned bytes, **not deletion advice**: references may require both files.

## `game_dev_checklist`

- `engine`: `godot`, `unity`, `unreal`, `web`, or `generic` (default).
- `stage`: `prototype` (default), `integration`, or `release`.
- Reads no project files and requires no path.
- Returns `executed: false` with `status: not_run` for each suggested check.

Adapt each prompt to an observable contract. Run tests separately through approved
Hermes tools and retain actual evidence; the checklist never upgrades itself to PASS.
