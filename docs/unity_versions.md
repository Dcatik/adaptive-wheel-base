# Unity Versions

## Unity Editor

Source of truth:
- `unity/ProjectSettings/ProjectVersion.txt`

Current Unity Editor version:
- `6000.4.0f1`
- revision: `8cf496087c8f`

## Locked package files

Source of truth:
- `unity/Packages/manifest.json`
- `unity/Packages/packages-lock.json`

## Current top-level Unity packages

Current packages from `manifest.json`:
- `com.unity.ai.navigation` = `2.0.11`
- `com.unity.collab-proxy` = `2.11.4`
- `com.unity.ide.rider` = `3.0.39`
- `com.unity.ide.visualstudio` = `2.0.27`
- `com.unity.inputsystem` = `1.19.0`
- `com.unity.multiplayer.center` = `1.0.1`
- `com.unity.render-pipelines.universal` = `17.4.0`
- `com.unity.test-framework` = `1.6.0`
- `com.unity.timeline` = `1.8.11`
- `com.unity.ugui` = `2.0.0`
- `com.unity.visualscripting` = `1.9.10`

## Current status

At this stage:
- Unity Editor version is fixed.
- Unity package graph is fixed.
- MuJoCo Unity plug-in is not added yet.
- ML-Agents package is not added yet.

## Policy

1. The Unity Editor version is fixed through `ProjectVersion.txt`.
2. Unity packages are fixed through `manifest.json`.
3. The resolved dependency graph is fixed through `packages-lock.json`.
4. Any Unity or package upgrade must be committed together with these files.
5. Manual package upgrades without a Git commit are not allowed.
