# Circle packing n=26: tolerance audit and exact certificate

Reproducible certificates for placing 26 variable-radius circles in the unit
square while maximizing the sum of their radii.

| Contract | Recomputed score | Interpretation |
| --- | ---: | --- |
| `1e-6` | `2.63599872089287514` | Public benchmark tolerance |
| `1e-10` | `2.63598308647338795` | Stricter numerical tolerance |
| `0` | `2.635983084917607783186569485443481730396676798274474857745771129860703849334…` | Strict finite-decimal rational witness |

These scores are not interchangeable. The first two certificates consume their
stated tolerances and fail at tolerance zero. The strict certificate proves a
feasible lower bound, not global optimality and not a new Packomania record.

![Exact packing and contact graph](figures/exact_packing_contact_graph.svg)

## Verify

Python 3.12 is the reference environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement requirements.lock
./verify_all.sh
```

The command checks all 1,287 inequalities—429 per certificate—with exact
rational pass/fail decisions, runs the tests, regenerates the audit table and
SVG, and updates `SHA256SUMS`. CI repeats the same command on Linux.

The primary review path is intentionally small:

- `data/certificates/`: the three tolerance-separated witnesses;
- `scripts/verifier.py`: independent standard-library rational verifier;
- `results/verification.json`: machine-readable feasibility margins;
- `data/leaderboard_audit.json` and `results/audit_tables.md`: frozen,
  tolerance-matched public-corpus audit;
- `docs/METHODS.md`: method, exactness, provenance, limitations, and AI
  disclosure.

## Reconstruct the numerical work

Rebuild the conservative exact certificate:

```bash
python scripts/refine_exact.py --output-dir work/rebuilt_exact
```

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
`circle-packing-full-evidence-v1.1.0.zip` and its SHA-256 checksum. That archive
preserves the original model explanations and programs, historical logs, and
all 78 regenerated seeds and traces without placing 180 archival files on the
reviewer-facing branch. It contains a per-file `MANIFEST.json` and can be
rebuilt from the immutable `v1.0.0` tag:

```bash
python scripts/build.py \
  --evidence-archive dist/circle-packing-full-evidence-v1.1.0.zip
```

## Supported claims

1. Each certificate passes its explicitly named numerical contract.
2. The finite decimals in `data/certificates/exact.csv`, interpreted as exact
   rationals, satisfy all 429 geometric inequalities at tolerance zero.
3. Each primary certificate ranks first inside the frozen public corpus dated
   2026-08-06 when compared only under the same tolerance.
4. The strict witness reconstructs a full-rank 78-contact stationary
   configuration with 58 pair and 20 wall contacts.

Rankings exclude private results and public claims without a complete witness.
Read `docs/METHODS.md` before citing these claims.

## Citation and license

Citation metadata is in `CITATION.cff`. Repository-authored code is MIT
licensed. External artifacts are not relicensed; `data/provenance.json` records
their sources and redistribution status.
