# What “exact” means here

Every coordinate and radius in `data/exact/certificate.csv` is a finite decimal.
A finite decimal represents a rational number exactly.  The verifier parses
those values as `Fraction` objects and checks:

```text
r_i > 0
r_i <= x_i <= 1-r_i
r_i <= y_i <= 1-r_i
(x_i-x_j)^2 + (y_i-y_j)^2 >= (r_i+r_j)^2
```

No square root and no floating-point tolerance participates in any pass/fail
decision.  The certificate therefore establishes an exact lower bound equal to
the exact rational sum of its 26 radii:

```text
2.6359830849176077831865694854434817303966767982744748577457711298607038493344723396767997365079
```

The boundary contact root is a different object.  It is computed numerically at
120 decimal digits and has score

```text
2.635983084917607783186569485443481730396676798274474857745771129860703849360472…
```

The published certificate is rounded and then all radii are reduced by about
`1e-75`.  Its score consequently ends in `…849334472…`, and its smallest gap is
strictly positive.

`data/exact/high_precision_report.json` records more digits for the in-memory
high-precision values than were serialized into the CSV. Those extra report
digits are diagnostic, not part of the finite-decimal rational certificate. The
CSV and the exact sum above are authoritative for the citable lower bound.

“Exact” does **not** mean that the contact root has been expressed in radicals,
that an interval proof of uniqueness has been supplied, or that the packing is
globally optimal among all possible contact graphs.
