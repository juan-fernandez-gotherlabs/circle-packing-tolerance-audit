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
interval proof of root uniqueness, or a proof of global optimality.

## Contact reconstruction and refinement

The exact witness identifies 78 active constraints under a `1e-7` discovery
threshold: 58 circle contacts and 20 wall contacts, matching the 78 variables
`(x_i,y_i,r_i)`. `scripts/contact_graph.py` reconstructs this system without
the missing historical `contact_flip.py` module.

`scripts/derive_nearby_strict.py` uses the published certificate as the seed,
stabilizes its detected contact root in binary64, performs Newton iterations at
120 decimal digits, rounds to 90 places, and applies a conservative uniform
radius reduction. The resulting CSV is checked independently by the rational
verifier. This is a derived nearby certificate, not independent reconstruction
of the published decimal serialization and not a byte-identical recovery path.

## Contact-release search

`scripts/search.py` releases one active constraint, follows the remaining
77-contact one-dimensional manifold by predictor-corrector continuation, and
stops at the first new contact. Layer 1 releases all 78 root contacts. Later
layers select the highest-scoring distinct positive-multiplier configurations,
deduplicating by contact set and by an isometry- and permutation-invariant
geometry signature.

The original ChatGPT sandbox did not provide `contact_flip.py` or its `.npz`
seeds. The implementation here is a clean reconstruction, not a claim of
bitwise recovery. A complete rerun reproduced all 78 released contacts and all
23 historical local-maximum classifications; the largest endpoint-score
difference was `3.311217966484037e-11`. See
`results/search_validation.json`.

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

The three primary certificates and the historical files were recovered from
the local ChatGPT conversation “Mejorar resultado matemático”
(`6a6b0f23-f53c-83eb-8a83-b3d4cdaa383d`). The verified original bundle hash
was `58b10f73a53cd1342f1b68d0bc717c69e8859b5a701fb6b7cf88bfdf664eba02`.
This is author-declared provenance: an external reviewer cannot authenticate
the private conversation from this public repository. Public certificate
validity does not depend on accepting that provenance claim.

Bulky historical outputs, original model explanations, original programs, and
the 78 regenerated seeds and traces are kept out of the reviewer-facing tree.
They are intended for the immutable `v1.1.0` release attachment
`circle-packing-full-evidence-v1.1.0.zip`, which contains its own per-file
manifest. Before that release exists, the attachment is a release-candidate
artifact. `python scripts/build.py --evidence-archive <path>` requires a full
Git clone with tags, verifies that protected tag `v1.0.0` resolves to pinned
commit `2359ee29d5de8747a124a5439779b8d4c553cce0`, archives by commit rather than
tag name, and checks the expected deterministic ZIP hash.

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
4. Full rank and signed KKT multipliers are numerical stationarity diagnostics,
   not a validated proof of local optimality.
5. The historical prose called 390 transitions “additional” in layer 2 and
   described layer 3 at 264/468. The final logs instead contain 312 second-layer
   transitions—390 cumulatively with layer 1—and all 468 third-layer
   transitions. No global conclusion follows from those three layers.
6. The exact verifier checks 429 geometric inequalities plus 26 radius
   positivity conditions per certificate. The historical leaderboard JSON's
   `constraints_checked` field refers only to the 429 geometric inequalities.

## AI assistance disclosure

ChatGPT performed much of the exploratory computation and generated the
original artifacts. Codex recovered, organized, independently checked, and
reimplemented missing reproducibility components. Human authors remain
responsible for every claim, interpretation, and submission. An AI system must
not be listed as an author; venue-specific disclosure requirements still
apply.
