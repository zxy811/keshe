#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export MPLCONFIGDIR="$PWD/results/mplconfig"
mkdir -p "$MPLCONFIGDIR"
.venv/bin/python tests/validate.py
echo 'Use .venv/bin/python tools/viewer.py to open the PC simulator.'
