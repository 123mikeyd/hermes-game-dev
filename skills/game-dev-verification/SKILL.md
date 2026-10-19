---
name: game-dev-verification
description: "Use when testing games and handing off builds."
version: 0.1.0
author: Mike (123mikeyd), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, playtest, release, portability]
    related_skills: [game-dev-workflow, game-dev-assets]
---

# Game Development Verification

Verify a defined revision through isolated tests, actual input, and portable builds.
Keep static findings, automated results, visual approval, and publication distinct.
This skill guides approved Hermes actions; the plugin itself does not run tests.

## When to Use

- Reproduce a gameplay bug, validate a feature, diagnose a suite, or hand off a build.
- Establish what was actually tested before describing a release as ready.
- Don't equate an inspection checklist with execution or an upload with deployment.

## Prerequisites

- Obtain the exact project, source identity, intended platforms, and acceptance contract.
- Read test/build scripts and their inherited helpers before running them.
- Discover installed engine and export-template versions without downloading anything.
- Reserve explicit scratch, logs, user-data, and output locations for this task.
- Obtain approval for builds, launches, writes, public servers, and publication.
- Use `templates/playtest.md` and `templates/release-handoff.md` beside this skill.

## How to Run

1. Inventory expected checks and preserve the baseline under a separate evidence path.
2. Run the smallest relevant isolated test before widening to the full suite.
3. Freeze a coherent revision for the final suite; do not test across ongoing edits.
4. Exercise the real input/mode path and exact extracted package independently.
5. Report every check as passed, failed, blocked, or not run, with evidence.

## Procedure

### 1. Inspect side effects and reserve ownership

- Find writes to saves, settings, screenshots, logs, import caches, and fixed paths.
- Inspect transitive helpers and production save APIs, not just runner entrypoints.
- A separate worktree does not isolate user data when the project name stays the same.
- Give each run its own user-data and output roots; verify where the engine writes.
- On Windows, isolate Godot's application-data environment per child command only.
- Do not globally change a persistent shell's environment and break unrelated tools.
- Preserve read-only fixtures; block tests whose writes cannot be safely redirected.
- Reserve a suite lock with owner, revision, start time, and owned process identifiers.
- Refuse overlapping full suites on shared source/cache/output or an active edit phase.
- Parallel runs require separate proven state, ports, caches, and output paths.
- Exit criterion: writes and process ownership are known before execution starts.

### 2. Establish a trustworthy focused test

- Enumerate assertions, expected completion marker, exit contract, and timeout budget.
- Confirm a behavior test fails for the expected reason before implementing a fix.
- Distinguish parser/preload failures and harness faults from gameplay regressions.
- Use real physics ticks for movement/contact and actual lifecycle setup for fixtures.
- In Godot, wait for required initialization before touching `_ready()`-created members.
- Never add arbitrary render waits to old tests; they can change object lifetimes.
- Require zero exit, the exact final success contract, and no unexpected fatal diagnostics.
- An early PASS line cannot override a later error, abort, timeout, or missing assertions.
- Keep any allowed diagnostic exception narrow, explained, and separately reported.
- Exit criterion: the runner fails reliably and reaches all intended assertions on success.

### 3. Expand to the final suite

- Save the full expected test inventory before running; do not infer it from successes.
- Freeze changed source or use an immutable snapshot and record its identity.
- Account for dirty files with a byte manifest; HEAD alone can omit the actual candidate.
- Persist each test result and full stdout/stderr immediately, including timeouts.
- Use bounded per-test and total budgets; derive long budgets from actual workload.
- On timeout, stop only owned processes and preserve partial evidence before retrying.
- Diagnose stalls versus contention; increasing the timeout is not a root-cause fix.
- Run scripts beyond the entry scene: a menu boot does not parse every gameplay script.
- Compare baseline/candidate failure sets, not only equal totals.
- Classify pre-existing failures, stale assertions, harness faults, and regressions separately.
- Never relabel an unresolved failure as passing to produce a green summary.
- Aggregate inventory, attempts, retries, and unique results in code, not mentally.
- Release the lock only after owned processes finish and evidence is flushed.
- Exit criterion: every inventory entry has a result tied to the frozen source.

### 4. Verify actual input and mode transitions

- Identify the exact process/window under test; do not drive the user's unrelated window.
- Enter through the real menu and Start callback, not only configuration helpers.
- Test press, hold, release, repeat, direction changes, and conflicting inputs as relevant.
- Exercise keyboard/controller/touch separately when each is a supported target.
- Cover pause/resume, focus changes, failure/retry, results/rematch, and menu return.
- Check cleanup of owned effects, timers, control locks, and transient states.
- Reproduce collision/contact with realistic positions and real physics, not just direct calls.
- Inspect visible feedback and timing at gameplay scale, not only close-up asset views.
- Preserve a safe ready state for interactive handoff and stop unattended active play.
- Exit criterion: the requested mechanic works through its real dispatch and lifecycle.

### 5. Verify an export, not just the source

- Build only when requested, using the identified engine and matching export templates.
- Stage a clean source snapshot; preserve import settings and required dependencies.
- Do not ship local import caches as a substitute for a reproducible import.
- Write output to a new directory and preserve failed import/export logs.
- Reject nonzero exits and unexpected fatal diagnostics even when an artifact exists.
- Record source identity, engine version, preset, target, and package hashes.
- Fresh-extract the archive and verify every expected member and relative dependency.
- Launch the extracted executable normally from the fresh directory.
- Keep editor-engine PCK probes distinct from actual release-template execution.
- Test levels/modes that load different assets, not just a successful title screen.
- Exit criterion: the exact deliverable works without the development directory.

### 6. Check browser and device boundaries

- Treat native success as separate from a browser export's runtime support.
- Check target-engine web restrictions for the exact renderer, language, and version.
- Check secure-context, cross-origin isolation, worker, and hosting requirements as applicable.
- Inspect asset HTTP responses, WebAssembly MIME type, console errors, and load failures.
- Test audio activation, pointer focus, touch controls, resize/orientation, and storage behavior.
- Measure actual load size, memory pressure, and frame timing on the intended device.
- Desktop emulation is not evidence of a real phone playtest.
- Public tunnels need explicit authorization, scoped content, tracked processes, and teardown.
- Exit criterion: browser/device claims name the actual tested environment and limitations.

### 7. Prepare a privacy-safe release handoff

- Review the exact package allowlist, notices, dependencies, and asset rights.
- Scan source and binary/export payloads for credentials and personal absolute paths.
- Inspect metadata, comments, image stamps, and embedded provenance beyond token scans.
- Preserve legally required attribution and runtime data while removing private notes.
- If publishing source, review reachable unpublished history as well as the final tree.
- Bind source, package, tag, and deployed bytes through recorded revision/hash identities.
- A changed source identity requires an updated build record and applicable re-verification.
- Publication requires authorization; this procedure does not grant it.
- After authorized publication, read back the exact remote target and download/hash assets.
- Distinguish source pushed, checks passed, package uploaded, and live gameplay verified.
- Exit criterion: recipients get controls, tested scope, known issues, and exact artifacts.

## Pitfalls

- A printed PASS or successful driver exit is not sufficient game evidence.
- Shared import caches, saves, and fixed evidence filenames can corrupt parallel runs.
- Identical test totals can hide entirely different failing tests.
- A file hash proves identity, not playability, licensing, or visual quality.
- A working editor launch can conceal missing export dependencies or remaps.
- Retrying after edits is a new candidate run, not completion of the prior frozen suite.

## Verification

- Reconcile all acceptance rows and list untested platforms/devices explicitly.
- Keep raw logs, screenshots, commands, timing, and source/package identities together.
- Confirm no task-owned server or game process remains unintentionally running.
- State limitations plainly; never synthesize logs or claim unavailable-device coverage.
