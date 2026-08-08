#!/usr/bin/env python3
"""Run the deterministic artifact build and exact checks."""

from __future__ import annotations

import json

from audit_historical_logs import generate as audit_historical_logs
from generate_manifest import generate as generate_manifest
from generate_provenance import generate as generate_provenance
from generate_table import generate as generate_table
from generate_visualization import generate as generate_visualization
from verifier import verify_repository


def main() -> int:
    verification = verify_repository(write=True)
    outputs = [
        audit_historical_logs(),
        generate_provenance(),
        generate_table(),
        generate_visualization(),
    ]
    outputs.append(generate_manifest())
    print(json.dumps({"status": verification["status"], "generated": [str(path) for path in outputs]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
