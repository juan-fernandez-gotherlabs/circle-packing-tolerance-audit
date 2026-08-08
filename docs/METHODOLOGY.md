# Methodology

## Numerical contracts

For a tolerance `tau`, the audit accepts wall gaps and pairwise distance gaps
down to `-tau`.  A strictly feasible packing can be transformed by

```text
c'_i = (1+t)c_i - (t/2,t/2)
r'_i = (1+t)r_i + t/2
```

with `t < tau`.  Every original gap `g` becomes `(1+t)g-t`, while the objective
becomes

```text
S' = S + t(S + n/2).
```

For `n=26`, the added term is `t(S+13)`.  This is why a tolerance-aware score
must not be compared directly with a tolerance-zero score.

## Contact reconstruction

The exact certificate has 78 near-active constraints under a `1e-7` discovery
threshold: 58 circle pairs and 20 walls.  There are also 78 variables
`(x_i,y_i,r_i)`.  Solving the contact equations yields a full-rank Jacobian and
the stationary diagnostics recorded in `data/exact/search_report.json`.

## High-precision certificate

`scripts/refine_exact.py` performs four operations:

1. solve the active graph in binary64 to stabilize the seed;
2. run Newton iterations at 120 decimal digits;
3. round all values to 90 decimal places;
4. shrink every radius uniformly until the finite-decimal witness has at least
   `1e-75` conservative clearance.

The final feasibility decision is then repeated independently with rational
arithmetic by `scripts/verifier.py`.

## Contact-release exploration

`scripts/trace_graph.py` removes one active constraint, follows the remaining
77-contact one-dimensional manifold by predictor-corrector continuation, and
stops at the first newly active wall or pair contact.  The resulting 78-contact
system is solved and stored as a fresh `.npz` seed.

`scripts/run_search.py` provides a deterministic orchestration policy.  Layer 1
releases all 78 root contacts.  Later layers deduplicate by contact set and
by an isometry- and permutation-invariant geometry signature, exclude branches
that return to the root, retain positive-multiplier stationary configurations,
and continue the highest-scoring distinct families. The selection policy is
explicit so a rerun does not depend on a private temporary directory.

## Public-corpus audit

The frozen audit recomputed the score and all 429 inequalities for each complete
witness it could obtain.  It interpreted serialized decimals exactly and
binary64 arrays as their exact IEEE-754 values.  Claims without a downloadable
witness, including the reported Numaro `n=26` value, were documented but not
ranked.
