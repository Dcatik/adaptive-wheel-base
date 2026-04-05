#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ -n "${CONDA_PREFIX:-}" ]; then
  echo "Error: conda environment is active (${CONDA_PREFIX})"
  echo "Run 'conda deactivate' first."
  exit 1
fi

unset PYTHONPATH
unset PYTHONHOME

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: $PYTHON_BIN not found"
  exit 1
fi

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install pip-tools
pip-sync requirements.txt

python - <<'PY'
import gymnasium
import mlagents_envs
import hydra
import omegaconf
import mlflow
import torch
import numpy
print("Python environment OK")
PY

pip check