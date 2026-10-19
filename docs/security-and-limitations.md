# Security boundary and limitations

## What the plugin does

The three registered handlers are stdlib Python. Inspection/audit traverse an
explicitly supplied local project directory; checklist generation uses fixed text.
Project reads can be outside the plugin directory. This is the intended capability,
not an implicit permission to inspect unrelated folders.

Handlers do not write files, run shell commands, start subprocesses/background
workers, make network calls, read credential stores, install engines/assets,
execute project code, or invoke editor APIs. No credential configuration is needed.
Hermes installation is separate and can download/write the plugin itself.

Inspection reads selected Godot configuration metadata. Asset hashing, when enabled,
reads selected asset bytes under budgets. Results include relative filenames and
selected project metadata, so they may still disclose private project information to
the conversation and its configured provider. Select roots deliberately.

## What exclusions mean

Hidden names, common generated/dependency directories, credential-like filenames,
symlinks, reparse points, special files, and hard-linked files are excluded or rejected.
These checks are best-effort safeguards, not a sandbox or a complete secret detector.
A secret stored in an ordinary asset or configuration file may still be read.
Do not point these tools at credential collections or hostile changing filesystems.
Concurrent filesystem mutation can defeat assumptions outside ordinary static use.

Entry, depth, asset-count, file-read, hash, and output budgets constrain work.
Truncation means incomplete coverage. Exclusions are not evidence that excluded
content is harmless, and observed totals do not describe all files on disk.

## Skills are not plugin execution

Bundled skills instruct an agent using normal Hermes tools. Builds, edits,
playtests, downloads, launches, network publication, and temporary servers are
separate actions, governed by user scope and Hermes approvals. A read-only plugin
is not a grant to execute a game's scripts or import hooks without review.

Before any engine run, inspect side effects, isolate saves and output, identify
owned processes, and agree on completion criteria. A headless import can execute
project code and alter caches. Do not bypass approval or silently widen scope.

## Evidence limitations

- No full editor integration or live scene inspection.
- No automatic asset licensing, geometry, rig, audio, visual, or gameplay validation.
- No download, unpacking, decoding, or interpretation of asset internals.
- No guarantee of complete nested-project detection or dependency discovery.
- No proof of compatibility from file extensions or byte hashes.
- No proof of real-device usability from desktop emulation or headless tests.
- No release readiness from a checklist whose checks have not actually run.

Keep original license notices. The MIT license covers this toolkit, not user assets.
Report security concerns without attaching credentials or private project payloads.
