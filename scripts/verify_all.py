#!/usr/bin/env python3
"""Run the deterministic artifact build and exact checks."""

from __future__ import annotations

import json

from build import generate_all
from prove_local_optimum import OUTPUT as LOCAL_OPTIMUM_OUTPUT
from prove_local_optimum import proof as prove_local_optimum
from verifier import verify_repository


def main() -> int:
    verification = verify_repository(write=True)
    local_optimum = prove_local_optimum()
    LOCAL_OPTIMUM_OUTPUT.write_text(
        json.dumps(local_optimum, indent=2) + "\n", encoding="utf-8"
    )
    outputs = generate_all()
    outputs.insert(0, LOCAL_OPTIMUM_OUTPUT)
    print(
        json.dumps(
            {
                "status": verification["status"],
                "local_optimum": local_optimum["status"],
                "generated": [str(path) for path in outputs],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
