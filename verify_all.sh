#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

REPOSITORY_TOPLEVEL="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ "$REPOSITORY_TOPLEVEL" != "$REPO_DIR" ]]; then
  echo "ERROR: ./verify_all.sh requires a full Git clone with tags; source archives lack the history needed for the manifest and evidence checks." >&2
  echo "Standalone exact checks: python3 scripts/verifier.py and python3 -S scripts/prove_local_optimum.py" >&2
  exit 2
fi

python3 -c 'import platform, sys; ok=platform.python_implementation()=="CPython" and sys.version_info[:2]==(3,12); raise SystemExit(0 if ok else f"ERROR: release verification requires CPython 3.12, found {platform.python_implementation()} {sys.version.split()[0]}")'

export PYTHONDONTWRITEBYTECODE=1
python3 scripts/verify_all.py
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
echo "ALL CHECKS: PASS"
