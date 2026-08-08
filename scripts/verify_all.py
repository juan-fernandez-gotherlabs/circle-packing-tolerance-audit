#!/usr/bin/env python3
"""Run the deterministic artifact build and exact checks."""

from __future__ import annotations

import json

from build import generate_all
from verifier import verify_repository


def main() -> int:
    verification = verify_repository(write=True)
    outputs = generate_all()
    print(json.dumps({"status": verification["status"], "generated": [str(path) for path in outputs]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
