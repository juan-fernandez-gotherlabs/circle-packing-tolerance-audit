# Circle packing n=26: tolerance audit and exact certificate

> **Release candidate for v1.2.0.** Its version-specific DOI is reserved as
> [10.5281/zenodo.21864592](https://doi.org/10.5281/zenodo.21864592). The previous
> public release, v1.1.0, remains preserved at
> [10.5281/zenodo.21853178](https://doi.org/10.5281/zenodo.21853178); it predates
> the interval certificate, reproducible public acquisition, and preprint added
> here. The final v1.2.0 tag and Zenodo publication will use the exact commit
> that passes the post-DOI release audit.

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

## Preprint

The accompanying preprint states the tolerance contracts, public-corpus audit,
and rational interval proof as a single mathematical argument:
[`preprint/circle_packing_n26_preprint.pdf`](preprint/circle_packing_n26_preprint.pdf).
Its central theorem is strict local optimality of the enclosed 78-contact real
root; it makes no claim of global optimality or a new packing record.

## Verify

CPython 3.12.4 on Ubuntu x86-64 is the reference environment for the
NumPy/SciPy diagnostics. Exact-rational verification uses only the Python
standard library and is platform-independent.

The complete release gate requires a full Git clone with tags. GitHub or
Zenodo source archives do not contain the `.git` history needed to verify the
tracked-file manifest and protected evidence tag. From a source archive, the
standalone exact checks remain available through `scripts/verifier.py` and
`python3 -S scripts/prove_local_optimum.py`, but `./verify_all.sh` intentionally
fails with an explanatory message.

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
runs the tests, regenerates the local-optimum interval report, the audit table
and SVG, and updates the repository artifact manifest `SHA256SUMS`. CI repeats
the same command on Linux.

## Rebuild publication PDFs

The publication gate is local and does not depend on GitHub Actions. Its
reference toolchain is `rsvg-convert 2.61.3` (Cairo 1.18.4, Pango 1.57.0,
HarfBuzz 12.2.0, Fontconfig 2.17.1, STIX Two Text 2.13 b171), TeX Live 2022
(`pdfTeX 1.40.24`, `latexmk 4.77`), and `pdfinfo 26.05.0`.
Rebuild the three vector figures and the preprint, then refresh `SHA256SUMS`:

```bash
python3 scripts/build_publication.py --write
```

After committing the outputs, the release gate reconstructs all four PDFs in
an isolated temporary tree, requires byte identity with the versioned files,
validates each PDF, runs the complete verification suite, and requires a clean
Git worktree:

```bash
python3 scripts/build_publication.py --check
```

The TeX source suppresses volatile creation dates and trailer identifiers so
the reference toolchain produces deterministic PDF bytes. A different
rendering toolchain may produce a visually equivalent but byte-different PDF;
such a build is not accepted by the frozen release gate.

The primary review path is intentionally small:

- `data/certificates/`: the three tolerance-separated witnesses;
- `scripts/verifier.py`: independent standard-library rational verifier;
- `results/verification.json`: machine-readable feasibility margins;
- `data/leaderboard_audit.json` and `results/audit_tables.md`: a historical,
  tolerance-matched comparison snapshot with explicit reproducibility limits;
- `data/public_sources.json`, `scripts/acquire_public.py`, and
  `results/public_corpus_audit.*`: the reproducible, hash-authenticated public
  acquisition and tolerance-separated reevaluation;
- `data/local_optimum_certificate.json`, `scripts/prove_local_optimum.py`, and
  `results/local_optimum_interval.json`: the exact-rational interval proof for
  the 78-contact strict local optimum;
- `docs/METHODS.md`: method, exactness, provenance, limitations, and AI
  disclosure.

## Verify the strict local optimum

The 78-contact real root near the finite-decimal witness is certified as a
strict local maximizer. The default verifier uses only the Python standard
library; `-S` demonstrates that no installed numerical package participates:

```bash
python3 -S scripts/prove_local_optimum.py
```

It proves a unique root in a rational box of radius `1e-90`, nonsingularity of
the active Jacobian throughout that box, strict feasibility of all 351 inactive
geometric constraints, and positivity of all 78 interval-enclosed KKT
multipliers. See `docs/LOCAL_OPTIMUM_PROOF.md` for the theorem and exact scope.
The isolated contact root is slightly above the deliberately shrunken CSV
witness; this remains a local result and is not a proof of global optimality.

## Refresh the public corpus

Download and authenticate the manifested AlphaEvolve, ThetaEvolve,
EurekAgent, Hyra, Station, Packomania, Jason Liang, and AlphaZ-CORAL
artifacts, then reevaluate every complete witness:

```bash
python scripts/acquire_public.py
```

The command checks every payload against its SHA-256 before parsing it, never
imports third-party Python, and writes the machine-readable and human-readable
reports in `results/public_corpus_audit.*`. Downloaded payloads remain in the
ignored `work/public_corpus/cache/` directory and can be replayed without the
network:

```bash
python scripts/acquire_public.py --offline
```

GitHub artifacts are pinned to 40-character commits. Packomania does not offer
an immutable artifact URL: its observed payload is hash-pinned and a changed
download stops the run. `--allow-mutable-drift` is an explicit investigative
override and must not be used to reproduce the frozen report.

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

## Historical full evidence archive

The previous `v1.1.0` release attaches the legacy archive
`circle-packing-full-evidence-v1.1.0.zip` and its SHA-256 checksum. The archive
preserves the original model explanations and programs, historical logs, and
all 78 regenerated seeds and traces without placing 180 archival files on the
reviewer-facing branch. It contains a per-file `MANIFEST.json` and can be
rebuilt from the pinned commit
`2359ee29d5de8747a124a5439779b8d4c553cce0`. The builder also requires the
protected `v1.0.0` tag to resolve to that commit and verifies the expected ZIP
SHA-256 `d55ec1eae5b50c0eb81b89da86fa520c9988d122cbe77465c180af1b30181f87`.
This historical builder also requires a full Git clone with tags:

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
4. The unique real root of that 78-contact system in the certified `1e-90`
   box is a strict local maximizer, by exact-rational Krawczyk and dual interval
   certificates.

The reproducible public-corpus report places each primary certificate first
among the acquired witnesses valid under its matching rational tolerance. The
separate EurekAgent binary64 `atol=1e-6` reproduction also places our `1e-6`
certificate above the public EurekAgent witness. These are positions inside the
explicitly manifested corpus, not universal leaderboard claims. The older
30-candidate historical snapshot remains contextual only because its original
acquisition payloads were not preserved. Our other two certificates are
excluded from each comparison. Read `docs/METHODS.md` before citing these
results.

## Citation and license

This tree prepares version `v1.2.0`, whose version-specific DOI is reserved as
[DOI `10.5281/zenodo.21864592`](https://doi.org/10.5281/zenodo.21864592).
The historical `v1.1.0` artifact remains available under
[DOI `10.5281/zenodo.21853178`](https://doi.org/10.5281/zenodo.21853178).
Complete v1.2.0 citation metadata is in `CITATION.cff`.
Repository-authored code is MIT
licensed. External artifacts are not relicensed; `data/provenance.json`
records their sources and redistribution status.
