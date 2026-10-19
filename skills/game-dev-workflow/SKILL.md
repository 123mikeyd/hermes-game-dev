---
name: game-dev-workflow
description: "Use when building a playable game vertical slice."
version: 0.1.0
author: Mike (123mikeyd), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game-development, godot, mvp, iteration]
    related_skills: [game-dev-assets, game-dev-verification]
---

# Game Development Workflow

Turn a bounded feature request into a playable, verified vertical slice.
Use Godot-first examples without converting an existing project to Godot.
This procedure uses normal Hermes tools; it does not install engines or assets.

## When to Use

- Start a small game, add a mechanic, or finish a playable feature.
- Investigate an existing engine project before changing its structure.
- Don't use a prototype request as permission to replace an established game.

## Prerequisites

- Resolve the user-approved project directory and permitted write scope.
- Read project instructions and inspect version-control status with `terminal`.
- Discover the existing engine, version, renderer, language, and entry scene.
- Obtain approval before downloads, dependency installs, exports, or publishing.
- Stop if the only available source is an unsaved editor session; request a save.
- No API keys are needed by this workflow or the bundled inspection tools.

## How to Run

1. Use `search_files` and `read_file` on the selected project, not the whole home.
2. If available, call `game_dev_inspect` with the explicitly selected path.
3. Treat inspection as bounded static evidence, never an engine execution result.
4. Record a short contract using `templates/acceptance.md` beside this skill.
5. Implement, test, and play the smallest end-to-end loop before expanding scope.

## Engine Discovery

- For Godot, inspect `project.godot`, the main scene, autoloads, and Input Map.
- Read renderer settings and `export_presets.cfg` if export is in scope.
- Treat export credentials and signing material as secrets; do not open them.
- Resolve the executable through approved local discovery; do not guess its path.
- Through `terminal`, run the discovered executable with `--version` and `--help`.
- Read existing test runners and build scripts before executing them.
- For Unity, inspect project/version metadata and existing package/build tooling.
- For Unreal, inspect the project descriptor and existing target/build tooling.
- For another engine, record the equivalent scene, input, build, and test entrypoints.
- Use that engine's installed version and official documentation for actual commands.
- Preserve the current architecture unless the requested change requires otherwise.

## Procedure

### 1. Define one playable loop

- Write the player action, feedback, success/failure condition, and restart path.
- Choose one representative environment and one input device for the first slice.
- State required platforms and distinguish current scope from later aspirations.
- Define measurable checks: inputs, expected state, timing bounds, and evidence.
- Separate gameplay acceptance from art approval and performance targets.
- Explicitly list excluded systems such as online play, progression, or extra levels.
- Exit criterion: another person can follow the contract without guessing controls.

### 2. Preserve the baseline

- Record the branch/revision and dirty files; never discard unrelated changes.
- Use an isolated copy or worktree when tests may alter imports, saves, or content.
- Record existing failures before attributing them to this feature.
- Keep temporary evidence outside runtime assets and public release payloads.
- Assign ownership of shared files when multiple contributors work concurrently.
- Exit criterion: the baseline and rollback source are identifiable and recoverable.

### 3. Build the smallest scene

- Use primitive or clearly labeled placeholder art until the loop works.
- Separate input intent, gameplay state, physics, presentation, and UI ownership.
- Give reset/retry an explicit path that clears transient state and owned effects.
- In Godot, use named Input Map actions rather than scattering physical key checks.
- Use physics ticks for movement/contact; do not emulate physics with large deltas.
- Keep visual offsets separate from colliders and authoritative world positions.
- Connect UI through the real start/pause/retry routes, not test-only substitutes.
- Exit criterion: start, act, receive feedback, finish, and restart work together.

### 4. Add one behavior at a time

- Write a focused check for the requested behavior before changing its implementation.
- Run it against the baseline and confirm the expected failure, not a broken harness.
- Implement the smallest change; inspect the actual files before patching APIs.
- Verify cancellation on pause, hit, death, scene change, or restart as applicable.
- Keep presentation timing separate from mechanics unless both changes are approved.
- Do not add hidden invulnerability, range, damage, or latency to improve appearance.
- Exit criterion: focused regression and relevant neighboring behaviors pass.

### 5. Exercise the real game

- Launch the owned project window and verify its title/path/process identity.
- Enter through normal menus; press, hold, release, and combine actual inputs.
- Test first use and repeated use, both directions, and each affected mode.
- Test losing focus, pause/resume, failure/retry, and returning to the menu.
- Inspect camera framing, readable feedback, collision response, and sound behavior.
- Headless success does not qualify visuals, audio, input feel, or device support.
- Exit criterion: observed results are attached to the exact changed revision.

### 6. Finish with a bounded handoff

- State what changed, how to try it, what passed, and what remains untested.
- Provide exact launch instructions using the discovered executable and project.
- Leave an interactive handoff at a safe menu or ready state, not uncontrolled play.
- Ask for approval on new visual direction before integrating polished replacements.
- Export only when requested; publication needs separate authorization.
- Exit criterion: the recipient can reproduce the slice and identify its limitations.

## Godot Command Patterns

Use these through `terminal`, replacing every placeholder with inspected values.
Set a finite tool timeout and a distinct log path for each run.
Imports and launches can execute project code and write caches; approve scope first.

```text
terminal(command='"<godot>" --headless --path "<project>" --import', timeout=300)
terminal(command='"<godot>" --headless --path "<project>" --script res://tests/test_feature.gd', timeout=120)
terminal(command='"<godot>" --headless --path "<project>" --quit-after 120', timeout=120)
terminal(command='"<godot>" --path "<project>"', background=true)
```

The bounded boot is a smoke test, not full script coverage or a playtest.
Only use the focused-test command after inspecting that actual runner.
Track an interactive process and close only the process owned by this task.

## Pitfalls

- A filename or engine marker does not prove the game is runnable.
- A passing helper test does not prove the real input dispatch reaches the helper.
- A new frame wait can change object lifetime; do not add waits just to hide failures.
- Existing art is not approval to redesign it while fixing unrelated mechanics.
- A broader rewrite increases the acceptance surface; prefer a narrow fix.
- A clean editor session does not prove a fresh import or packaged build works.

## Verification

- Account for every acceptance row as passed, failed, blocked, or not run.
- Retain logs and exact commands; distinguish observed output from expectations.
- Inspect changed-file scope and confirm unrelated work remains intact.
- Report static inspection, automated tests, and rendered playtests separately.
- Never invent passing output when the engine or required device is unavailable.
