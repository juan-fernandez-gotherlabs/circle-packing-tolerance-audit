#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

export PYTHONDONTWRITEBYTECODE=1
python3 scripts/verify_all.py
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
echo "ALL CHECKS: PASS"
