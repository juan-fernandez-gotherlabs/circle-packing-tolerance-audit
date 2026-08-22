# Methods, provenance, and limitations

## Numerical contracts

For tolerance `tau`, a wall or pairwise distance gap may be as small as
`-tau`. A tolerance-aware score must therefore never be compared directly with
a tolerance-zero score. The `1e-6` and `1e-10` certificates in this repository
pass only their named contracts and both fail at zero tolerance.

These repository contracts use exact rational arithmetic and a linear distance
allowance. In particular, the rational `tau=1e-6` decision is not asserted to
be identical at rounding boundaries to the public evaluator, which evaluates
`sqrt` in IEEE-754 binary64. Public-evaluator compatibility and rational
feasibility are separate statements.

## Exact finite-decimal certificate

Every coordinate and radius in `data/certificates/exact.csv` is a finite
decimal and therefore an exact rational number. `scripts/verifier.py` parses
the decimals as `Fraction` objects and decides all constraints without square
roots or floating-point tolerances:

```text
r_i > 0
r_i <= x_i <= 1-r_i
r_i <= y_i <= 1-r_i
(x_i-x_j)^2 + (y_i-y_j)^2 >= (r_i+r_j)^2
```

The exact rational sum of the 26 published radii is

```text
2.6359830849176077831865694854434817303966767982744748577457711298607038493344723396767997365079
```

The numerical boundary root has slightly more score. The certificate was
rounded to 90 decimal places and every radius was reduced by about `1e-75`, so
its smallest gap is strictly positive. “Exact” here means exact feasibility of
the serialized rational witness. It does not mean a radicals expression, an
interval proof of root uniqueness, or a proof of global optimality. The
separate interval proof below applies to the nearby real contact root, not to
the deliberately shrunken CSV.

## Contact reconstruction and refinement

The exact witness identifies 78 active constraints under the `1e-7` threshold
used for exploratory contact discovery: 58 circle contacts and 20 wall
contacts, matching the 78 variables `(x_i,y_i,r_i)`.
`scripts/prove_local_optimum.py` independently applies the much stricter
`1e-40` threshold when checking that the stored interval certificate names
only essentially vanishing seed gaps. Both thresholds select the same 78
constraints: the largest selected seed gap is approximately `1.019e-75`,
whereas the smallest unselected gap is approximately `7.188e-3`.
`scripts/contact_graph.py` reconstructs this system without the missing
historical `contact_flip.py` module.

`scripts/derive_nearby_strict.py` uses the published certificate as the seed,
stabilizes its detected contact root in binary64, performs Newton iterations at
120 decimal digits, rounds to 90 places, and applies a conservative uniform
radius reduction. The resulting CSV is checked independently by the rational
verifier. This is a derived nearby certificate, not independent reconstruction
of the published decimal serialization and not a byte-identical recovery path.

The contact root itself now has a rigorous local-optimality certificate.
`scripts/prove_local_optimum.py` uses exact rational interval endpoints to
prove a strict Krawczyk inclusion for the square 78-contact polynomial system,
strict separation of the 351 inactive constraints, and a second Krawczyk
inclusion for the dual stationarity equations with all 78 multipliers positive.
Since the active gap map is locally invertible, its gaps are local coordinates;
the strictly negative objective derivative in every feasible gap direction
proves a strict local maximum. The default proof path runs with the standard
library alone. Full details and the distinction between the real contact root
and the shrunken finite-decimal witness are in
`docs/LOCAL_OPTIMUM_PROOF.md`.

## Contact-release search

`scripts/search.py` releases one active constraint, follows the remaining
77-contact one-dimensional manifold by predictor-corrector continuation, and
stops at the first new contact. Layer 1 releases all 78 root contacts. Later
layers select the highest-scoring distinct positive-multiplier configurations,
deduplicating by contact set and by an isometry- and permutation-invariant
geometry signature.

The original AI-assisted research session did not preserve `contact_flip.py`
or its `.npz` seeds. The implementation here is a clean reconstruction, not a
claim of bitwise recovery. A complete rerun reproduced all 78 released
contacts and all 23 historical local-maximum classifications; the largest
endpoint-score difference was `3.311217966484037e-11`. See
`results/search_validation.json`.

## Reproducible public-corpus acquisition

The repository now also contains a smaller, independently repeatable public
acquisition. `data/public_sources.json` records immutable Git commits, raw
artifact URLs, expected SHA-256 values, parser identifiers, and observed
licenses. `scripts/acquire_public.py` downloads those artifacts into ignored
working storage, authenticates their bytes before parsing, and evaluates every
complete 26-circle witness with `scripts/verifier.py` at rational tolerances
zero, `1e-10`, and `1e-6`.

Third-party Python files and the AlphaEvolve notebook are parsed with Python's
AST and JSON readers; they are never imported or executed. Numeric source
tokens are recovered as decimal strings rather than first converted to
binary64. JSON floating-point tokens receive the same treatment. This makes
the uniform decisions exact for the public serialized decimals.

The report additionally contains independent binary64 reimplementations of the
published AlphaEvolve zero-tolerance check and EurekAgent
`adapted_validate_packing(atol=1e-6)`. The upstream evaluator source is itself
commit- and hash-pinned, but is not executed. This separate view is necessary:
the EurekAgent witness passes its public binary64 evaluator while missing the
repository's exact-rational `1e-6` boundary by a sub-decimal rounding amount.
The corresponding source-native table applies one evaluator to the complete
acquired corpus and puts the matching author certificate in that same table.

Only serialized centers and radii enter witness rankings. AlphaZ-CORAL is
downloaded and authenticated but excluded because the published file stores
centers and computes radii by solving a linear program at runtime. Numaro and
HELIX are documented as reported claims because no complete downloadable n=26
witness was located. Their reported scores are not treated as verified data.

Packomania is the sole complete-witness source without an immutable artifact
URL. Its 2026-08-08 payload is protected by an expected SHA-256 and the default
acquisition fails closed if the page changes. No matching Internet Archive
payload was available during preparation. Consequently a future online replay
depends on that mutable payload remaining available; an already authenticated
local cache can be replayed with `--offline`. This limitation is explicit in
the source manifest and report.

`results/public_corpus_audit.json` is the full machine-readable output;
`results/public_corpus_audit.md` is its compact rendering. Positions in those
files are mechanically reproducible within the manifested corpus. They are not
claims of exhaustive literature coverage.

## Historical public-corpus snapshot

The 2026-08-06 snapshot reports recomputed scores and 429 geometric constraints
for the complete public witnesses acquired at that time. Serialized decimals
were interpreted exactly and binary64 arrays as their exact IEEE-754 values.
Claims without a downloadable witness were documented but not ranked.

This snapshot is not reproducible from end to end: the acquisition/parsing
program and all exact upstream payloads were not preserved. The repository can
check internal ordering and provenance coverage, but a reviewer cannot repeat
the original acquisition and reevaluation of all 30 candidates. Consequently
the snapshot is contextual evidence, not independent proof of a leaderboard
position. Each displayed tolerance comparison contains the matching author
certificate and external candidates only; the author's other certificates are
excluded. `data/provenance.json` fixes commits and SHA-256 values where they
are publicly recoverable and labels the remaining gaps.

## Provenance and evidence archive

The three primary certificates and the historical files were recovered from a
private Göther Labs AI-assisted research session
(`6a6b0f23-f53c-83eb-8a83-b3d4cdaa383d`). The verified original bundle hash
was `58b10f73a53cd1342f1b68d0bc717c69e8859b5a701fb6b7cf88bfdf664eba02`.
This is author-declared provenance: an external reviewer cannot authenticate
the private session from this public repository. Public certificate validity
does not depend on accepting that provenance claim.

Bulky historical outputs, original model explanations, original programs, and
the 78 regenerated seeds and traces are kept out of the reviewer-facing tree.
They are preserved in the immutable historical `v1.1.0` release attachment
`circle-packing-full-evidence-v1.1.0.zip`, which contains its own per-file
manifest. `python scripts/build.py --evidence-archive <path>` requires a full
Git clone with tags, verifies that protected tag `v1.0.0` resolves to pinned
commit `2359ee29d5de8747a124a5439779b8d4c553cce0`, archives by commit rather than
tag name, and checks the expected deterministic ZIP hash.

The complete `./verify_all.sh` gate likewise requires a full Git clone because
it checks the tracked-file manifest and protected historical tag. Standalone
exact feasibility and interval verification do not depend on Git history. The
separate `scripts/build_publication.py` gate rebuilds and byte-compares the
three figure PDFs and the preprint PDF under the pinned reference publication
toolchain documented in `README.md`; it is a manual release check and does not
require GitHub Actions.

Repository-authored code is MIT licensed. Unlicensed or ambiguously licensed
third-party witnesses are not vendored; only derived audit metrics and source
identifiers are retained. These license observations are not legal advice.

## Limitations and non-claims

1. The exact certificate is a rigorous feasible lower bound, not a global
   optimum proof.
2. No new Packomania decimal is claimed; the strict score rounds to the current
   published `n=26` value at 12 decimal places.
3. The historical comparison is observational and not an independently
   reproducible rank claim.
4. Numerical full rank and multiplier signs alone would not prove local
   optimality. The new claim is limited to the one contact root enclosed by the
   rational primal and dual interval certificates; it says nothing global.
5. The historical prose called 390 transitions “additional” in layer 2 and
   described layer 3 at 264/468. The final logs instead contain 312 second-layer
   transitions—390 cumulatively with layer 1—and all 468 third-layer
   transitions. No global conclusion follows from those three layers.
6. The exact verifier checks 429 geometric inequalities plus 26 radius
   positivity conditions per certificate. The historical leaderboard JSON's
   `constraints_checked` field refers only to the 429 geometric inequalities.
7. The new public acquisition is reproducible for its explicitly manifested
   corpus, not exhaustive. Packomania remains a hash-guarded mutable source,
   and claims without complete public witnesses cannot be ranked.

## AI assistance disclosure

This work used a Göther Labs AI-assisted research pipeline. Internally
coordinated agents contributed to exploratory computation, generation and
recovery of artifacts, software implementation, verification, and drafting.
Every public claim is backed by inspectable certificates and reproducible
checks; the human author remains responsible for every claim, interpretation,
and submission. No AI system is an author, and venue-specific disclosure
requirements still apply.
