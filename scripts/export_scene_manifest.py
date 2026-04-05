#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="sim/manifests/sample_scene_v1.yaml",
        help="Path to scene manifest YAML",
    )
    parser.add_argument(
        "--physics-profile",
        default="sim/physics_profiles/sample_scene_v1.yaml",
        help="Path to physics profile YAML",
    )
    parser.add_argument(
        "--out",
        default="artifacts/scene_manifest_export/sample_scene_v1.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()
    manifest_path = repo_root / args.manifest
    physics_path = repo_root / args.physics_profile
    out_path = repo_root / args.out

    if not manifest_path.is_file():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    if not physics_path.is_file():
        print(f"ERROR: physics profile not found: {physics_path}", file=sys.stderr)
        return 1

    manifest_text = manifest_path.read_text(encoding="utf-8")
    physics_text = physics_path.read_text(encoding="utf-8")

    export_payload = {
        "manifest_path": args.manifest,
        "physics_profile_path": args.physics_profile,
        "manifest_file_hash": sha256_file(manifest_path),
        "physics_profile_hash": sha256_file(physics_path),
        "scene_manifest_hash": sha256_bytes(
            (
                f"manifest_path={args.manifest}\n"
                f"physics_profile_path={args.physics_profile}\n"
                f"manifest_text=\n{manifest_text}\n"
                f"physics_text=\n{physics_text}\n"
            ).encode("utf-8")
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(export_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(export_payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
