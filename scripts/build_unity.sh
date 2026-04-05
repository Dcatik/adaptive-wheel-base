#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_PATH="$ROOT_DIR/unity"
LOG_DIR="$ROOT_DIR/artifacts/unity_build_logs"

mkdir -p "$LOG_DIR"

BUILD_KIND="${1:-headless}"
BUILD_KIND="${1:-headless}"
GIT_SHA="$(git -C "$ROOT_DIR" rev-parse HEAD)"

case "$BUILD_KIND" in
  headless)
    EXECUTE_METHOD="BuildScripts.BuildLinuxHeadless"
    LOG_FILE="$LOG_DIR/build_linux_headless.log"
    export UNITY_BUILD_SCENE_ID="sample_scene_v1"
    ;;
  visual)
    EXECUTE_METHOD="BuildScripts.BuildLinuxVisual"
    LOG_FILE="$LOG_DIR/build_linux_visual.log"
    export UNITY_BUILD_SCENE_ID="sample_scene_v1"
    ;;
  *)
    echo "ERROR: unknown build kind: $BUILD_KIND"
    echo "Usage: bash scripts/build_unity.sh [headless|visual]"
    exit 1
    ;;
esac

export UNITY_BUILD_GIT_SHA="$GIT_SHA"

if [ -z "${UNITY_BIN:-}" ]; then
  echo "ERROR: UNITY_BIN is not set."
  echo 'Example: UNITY_BIN="/path/to/Unity" bash scripts/build_unity.sh headless'
  exit 1
fi

if [ ! -x "$UNITY_BIN" ]; then
  echo "ERROR: UNITY_BIN is not executable: $UNITY_BIN"
  exit 1
fi

"$UNITY_BIN" \
  -batchmode \
  -quit \
  -nographics \
  -accept-apiupdate \
  -projectPath "$PROJECT_PATH" \
  -executeMethod "$EXECUTE_METHOD" \
  -logFile "$LOG_FILE"