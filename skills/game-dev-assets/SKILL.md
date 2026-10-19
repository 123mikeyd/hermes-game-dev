---
name: game-dev-assets
description: "Use when preparing editable assets for a game."
version: 0.1.0
author: Mike (123mikeyd), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [assets, blender, animation, provenance]
    related_skills: [game-dev-workflow, game-dev-verification]
---

# Game Development Assets

Prepare reviewable, editable assets and verify their actual engine import.
Preserve approved appearance and native sources instead of treating exports as masters.
This procedure does not download art, execute Blender, or alter files by itself.

## When to Use

- Create, revise, retarget, export, or integrate models, textures, audio, or animation.
- Diagnose an import mismatch while preserving a known-good source.
- Don't treat asset availability as proof of redistribution rights or visual approval.

## Prerequisites

- Identify the exact authorized source, target engine, and destination files.
- Inspect installed authoring/exporter versions before choosing operator arguments.
- Read project instructions and obtain approval for destructive or external actions.
- Preserve unsaved editor work; never overwrite it from another process.
- Select a new candidate output and a separate evidence location.
- If available, use `game_dev_asset_audit` for bounded static inventory hints only.
- Use `search_files`, `read_file`, and approved `terminal` probes for deeper inspection.

## How to Run

1. Fill `templates/asset-provenance.md` beside this skill for each proposed asset.
2. Establish the source identity and approval target before generating derivatives.
3. Inspect a protected copy, make one controlled change, and reopen the saved output.
4. Reimport the export into a fresh authoring scene and the actual engine.
5. Promote only the approved candidate whose bytes match the reviewed evidence.

## Procedure

### 1. Establish rights and source identity

- Record creator, source location, acquisition date, license, and required notices.
- Distinguish permission to use in a game from permission to redistribute source art.
- Keep a local license copy or acquisition record; do not infer rights from “free.”
- Mark unresolved rights as blocked for publication, not implicitly MIT.
- Record generated-asset tools and applicable terms without exposing credentials.
- Record the exact asset version/hash and dependencies, not only a mutable filename.
- Keep private purchase records and internal notes out of public runtime packages.
- Exit criterion: ownership, allowed use, attribution, and unresolved limits are explicit.

### 2. Define the review target

- Identify which silhouette, pose, palette, motion, or sound is approved.
- Label new candidates as proposals; one approved frame does not approve a whole clip.
- Match reference camera, lighting, scale, and frame before comparing candidates.
- Inspect front/side/back views and the intended gameplay camera distance.
- Ask before changing identity, timing, proportions, or gameplay meaning.
- Stop when the asset is the wrong subject even if its skeleton is compatible.
- Exit criterion: the reviewer knows exactly what would be installed.

### 3. Protect editable sources

- Retain native scene files, Actions, layers, source textures, and audio sessions.
- Duplicate mesh datablocks independently for backups; linked copies are not backups.
- Keep imported motion carriers in an explicit review collection until transfer passes.
- Save a new version rather than replacing the currently open source file.
- Preserve original UVs, materials, weights, shape keys, and rig rest data by default.
- Record intended edits and compare unchanged regions against the protected source.
- Exit criterion: the change is reversible without reconstructing the original.

### 4. Inspect the transform and rig contract

- Inventory mesh/armature objects, parent chains, modifiers, bone names, and hierarchy.
- Record object transforms, units, rest matrices, parent inverses, and rotation modes.
- Bone-name equality alone does not establish rest-pose or bind compatibility.
- Compare evaluated vertices and anatomical joint heads, not only display bone tails.
- Preserve the parent inverse when duplicating a skinned mesh onto a copied rig.
- Never apply transforms, normalize weights, or change rest bones as a blind repair.
- Check deform influence coverage, seams, limb clearance, and extreme poses.
- Separate topology artifacts from motion-correlated collapse or cross-limb weighting.
- Exit criterion: the source deforms correctly and the intended transform basis is known.

### 5. Specify motion ownership

- Decide whether the engine controller or the clip owns translation and rotation.
- Use a separate unanimated placement parent for staging an animated root.
- Do not zero guessed local hip channels; local axes can differ from world axes.
- Preserve approved vertical motion when removing horizontal travel for in-place use.
- Record source frame range, effective key spacing, sample rate, and duration in seconds.
- Rebase time without silently changing speed or dropping the last authored sample.
- Distinguish source frames, engine seconds, playback rate, and gameplay event time.
- Check first/contact/last poses and intermediate samples, including loop seams.
- For paired clips, measure both actors in the same world/floor coordinate system.
- Exit criterion: travel, pose timing, and controller handoff have one explicit owner.

### 6. Export a portable derivative

- Select only the intended assets; exclude cameras, helpers, review carriers, and backups.
- Inspect the installed exporter API; do not assume arguments from another version.
- Choose interchange format for the target's supported rig/material/animation contract.
- Preserve required skin influences and morphs; inspect target limitations explicitly.
- Export actual texture files when references require them, even if images are packed.
- Use relative dependencies and include required material/texture sidecars.
- Check material paths, dimensions, units, orientation, and animation selection.
- Keep static-mesh exports clearly distinct from rigged or animated deliveries.
- Exit criterion: export dependencies are enumerated and present without local-path reliance.

### 7. Prove the round trip

- Open a fresh scene and reimport the derivative rather than inspecting the source again.
- Verify mesh/rig counts, bindings, materials, loaded images, and plausible dimensions.
- Compare evaluated landmarks or vertices at authored sample times with stated tolerances.
- Import into the actual engine using recorded import settings and sampling rates.
- If authoring reimport matches but the engine differs, investigate rebake/optimization/cache.
- Reimport only owned assets; do not clear a shared cache while another editor uses it.
- Check source versus engine poses, floor clearance, contact timing, and loop transitions.
- Review real rendered output; finite transforms and populated curves do not prove quality.
- Exit criterion: both structural and visible checks apply to the exported candidate.

### 8. Integrate the accepted candidate

- Promote exact approved bytes and settings rather than redesigning during integration.
- Keep collision, input, damage, and camera behavior unchanged unless authorized.
- Test interruption, blending, repeated use, and reset in the real gameplay lifecycle.
- Recheck unrelated clips and dependencies after modifying a shared animation library.
- Provide editable sources separately when their redistribution is permitted.
- Exit criterion: the installed asset matches review and preserves neighboring behavior.

## Pitfalls

- Packed images prove portability only after loading; they do not prove appearance.
- Export success does not prove skinning, root motion, materials, or rights are correct.
- A target empty at the right place does not prove the evaluated hand or foot reaches it.
- Sparse animation keys require interpolation-aware sampling, including quaternions.
- A texture authored for one UV layout is not interchangeable with another mesh's atlas.
- A hidden backup can still leak into an export; inspect the exported inventory.
- Failed candidates remain failed even when a later screenshot hides the defect.

## Verification

- Attach source/export identities, settings, sample times, and measured tolerances.
- Record structural checks separately from human visual approval.
- Reopen the saved editable source and the final derivative before handoff.
- State any missing target-engine, device, performance, or redistribution verification.
- Never claim a static inventory audit rendered or validated the asset in an engine.
