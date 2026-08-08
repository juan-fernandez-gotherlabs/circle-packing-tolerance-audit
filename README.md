# Circle packing n=26: tolerance audit and exact certificate

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21853178.svg)](https://doi.org/10.5281/zenodo.21853178)

Reproducible certificates for placing 26 variable-radius circles in the unit
square while maximizing the sum of their radii.

| Contract | Recomputed score | Interpretation |
| --- | ---: | --- |
| `1e-6` | `2.63599872089287514` | Exact-rational linear tolerance contract |
| `1e-10` | `2.63598308647338795` | Stricter numerical tolerance |
| `0` | `2.63598308491760778…` | Strict finite-decimal rational witness |

The unabbreviated exact score is preserved in
[`results/verification.json`](results/verification.json); shortening its display
here keeps the interpretation column readable on ordinary screens.

These scores are not interchangeable. The first two certificates consume their
stated tolerances and fail at tolerance zero. The strict certificate proves a
feasible lower bound, not global optimality and not a new Packomania record.

![Exact packing and contact graph](figures/exact_packing_contact_graph.svg)

## Verify

CPython 3.12.4 on Ubuntu x86-64 is the reference environment for the
NumPy/SciPy diagnostics. Exact-rational verification uses only the Python
standard library and is platform-independent.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes --requirement requirements.lock
./verify_all.sh
```

The three primary contracts require 1,365 exact-rational decisions: 429
geometric inequalities and 26 radius-positivity conditions per certificate.
The two relaxed certificates are then rechecked at tolerance zero, adding 910
separation decisions, for 2,275 condition evaluations in total. The command
runs the tests, regenerates the audit table and SVG, and updates the repository
artifact manifest `SHA256SUMS`. CI repeats the same command on Linux.

The primary review path is intentionally small:

- `data/certificates/`: the three tolerance-separated witnesses;
- `scripts/verifier.py`: independent standard-library rational verifier;
- `results/verification.json`: machine-readable feasibility margins;
- `data/leaderboard_audit.json` and `results/audit_tables.md`: a historical,
  tolerance-matched comparison snapshot with explicit reproducibility limits;
- `docs/METHODS.md`: method, exactness, provenance, limitations, and AI
  disclosure.

## Reproduce numerical diagnostics

Derive another nearby strict certificate from the published witness:

```bash
python scripts/derive_nearby_strict.py --output-dir work/nearby_strict
```

This is deliberately not called a reconstruction: it uses the published
certificate to discover and seed the contact system and does not reproduce the
published CSV byte for byte.

Regenerate the 78 first-layer contact releases and deterministic `.npz` seeds:

```bash
python scripts/search.py --depth 1
```

The missing historical `contact_flip.py` is replaced by the self-contained
`scripts/contact_graph.py`. The clean implementation reproduced all 78 released
contacts and all 23 historical local-maximum classifications. It is a
reconstruction, not a claim of byte-identical recovery of the former sandbox.

## Full evidence archive

The `v1.1.0` release attaches
`circle-packing-full-evidence-v1.1.0.zip` and its SHA-256 checksum. The archive
preserves the original model explanations and programs, historical logs, and
all 78 regenerated seeds and traces without placing 180 archival files on the
reviewer-facing branch. It contains a per-file `MANIFEST.json` and can be
rebuilt from the pinned commit
`2359ee29d5de8747a124a5439779b8d4c553cce0`. The builder also requires the
protected `v1.0.0` tag to resolve to that commit and verifies the expected ZIP
SHA-256 `d55ec1eae5b50c0eb81b89da86fa520c9988d122cbe77465c180af1b30181f87`.
This command requires a full Git clone with tags; GitHub source archives do not
contain the `.git` objects it needs:

```bash
python scripts/build.py \
  --evidence-archive dist/circle-packing-full-evidence-v1.1.0.zip
```

## Supported claims

1. Each certificate passes its explicitly named numerical contract.
2. The finite decimals in `data/certificates/exact.csv`, interpreted as exact
   rationals, satisfy all 429 geometric inequalities at tolerance zero.
3. The strict witness reconstructs a full-rank 78-contact stationary
   configuration with 58 pair and 20 wall contacts.

The historical snapshot places each primary certificate ahead of the external
candidates stored for its matching rational tolerance, but this is not a
supported rank claim: the original acquisition program and every upstream
payload were not preserved. Our other two certificates are excluded from each
snapshot comparison. The rational `1e-6` contract is also not claimed to be
bit-for-bit equivalent to the public evaluator's binary64 implementation. Read
`docs/METHODS.md` before citing these results.

## Citation and license

Version `v1.1.0` is archived at Zenodo under
[DOI `10.5281/zenodo.21853178`](https://doi.org/10.5281/zenodo.21853178).
Citation metadata is in `CITATION.cff`. Repository-authored code is MIT
licensed. External artifacts are not relicensed; `data/provenance.json`
records their sources and redistribution status.
