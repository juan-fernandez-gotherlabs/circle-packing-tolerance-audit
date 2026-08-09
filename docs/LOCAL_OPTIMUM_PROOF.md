# Rigorous local-optimality certificate

## Claim and object being certified

There is a unique real configuration `x*` in the rational box recorded by
`data/local_optimum_certificate.json` at which the detected 58 circle-circle
contacts and 20 circle-wall contacts are all equalities. This configuration is
a **strict local maximizer** of the sum of the 26 radii among feasible packings
in the unit square.

The root `x*` is not the finite-decimal witness in
`data/certificates/exact.csv`. That CSV was obtained by rounding the contact
root and shrinking every radius, so it is a nearby strictly feasible lower
bound. The interval proof concerns the exact real contact root isolated around
it. It proves neither global optimality nor uniqueness outside the certified
local box.

## Polynomial formulation

Write the variables as

```text
x = (x_0,y_0,r_0,...,x_25,y_25,r_25) in R^78.
```

The four wall gaps of circle `i` are

```text
x_i-r_i,  1-x_i-r_i,  y_i-r_i,  1-y_i-r_i.
```

For circles `i<j`, use the squared separation gap

```text
q_ij = (x_i-x_j)^2 + (y_i-y_j)^2 - (r_i+r_j)^2.
```

All feasible packings have these 429 geometric gaps nonnegative and all radii
positive. Because the proof certifies positive radii, `q_ij>=0` is equivalent
to ordinary non-overlap. The 78 active gaps form a polynomial map
`g:R^78 -> R^78`; its Jacobian is affine, so its interval extension requires
no square roots or transcendental rounding.

## Exact interval computation

The default command is

```bash
python3 -S scripts/prove_local_optimum.py
```

`-S` disables third-party site packages. The verifier parses every decimal in
the certificate as a `Fraction` and performs all proof decisions with closed
rational intervals. NumPy and mpmath are not imported on this path. They are
used only by the optional
`--regenerate-certificate` mode to propose replacement rational data; the
result still has to pass the same exact verifier.

For midpoint `m`, rational preconditioner `C`, and box `X`, the verifier forms

```text
K(X) = m - C g(m) + (I - C J(X))(X-m).
```

The exact interval result satisfies `K(X) subset int(X)`. By the Krawczyk
existence-and-uniqueness theorem, `X` therefore contains one unique zero `x*`.
The additional bound `||I-CJ(X)||_infinity < 1` proves that `C` and every
Jacobian represented in the box are nonsingular. The operator originates in
R. Krawczyk, “Newton-Algorithmen zur Bestimmung von Nullstellen mit
Fehlerschranken,” *Computing* 4 (1969), 187–201,
[doi:10.1007/BF02234767](https://doi.org/10.1007/BF02234767).

The certified numerical bounds are:

```text
primal box radius                          1e-90
maximum Krawczyk component/radius ratio   < 8.551052960068879e-15
||I-CJ(X)||_infinity                      < 8.551052960068879e-15
minimum inactive polynomial gap           > 0.0071877548062774697881043072924253371679
minimum radius                             > 0.0691806763572344820974407544002623682677
```

Thus all 351 inactive geometric constraints are strict at `x*`, and the active
equalities describe an actual packing.

## Rigorous dual certificate

Let `f(x)=sum_i r_i`. With gaps written as `g>=0` for a maximization problem,
stationarity has the sign convention

```text
grad(f)(x*) + J(x*)^T lambda = 0.
```

The verifier applies a second rational Krawczyk test to this 78-by-78 linear
system, using `J(X)^T` as an interval enclosure. Its image is strictly inside a
dual box of radius `1e-10`; the largest inclusion ratio is below
`7.677651441669678e-6`. Every multiplier is certified larger than
`0.020825602106288`.

## Why this proves a strict local maximum

Nonsingularity of `J(x*)` makes the 78 active gaps local coordinates by the
inverse function theorem. Put `z=g(x)` and write the objective in these
coordinates as `F(z)=f(g^{-1}(z))`. At the contact root,

```text
grad_z F(0) = J(x*)^{-T} grad(f)(x*) = -lambda.
```

Every component is strictly negative. By continuity, all components remain
negative in a sufficiently small box around `z=0`. A nearby feasible packing
has `z>=0`; if it differs from `x*`, then `z` is nonzero. Integrating the
gradient of `F` along the segment from `0` to `z` gives
`F(z)<F(0)`. Hence `x*` is a strict local maximizer.

No Hessian test is needed: the active Jacobian is square and nonsingular, so
the critical cone is trivial. This argument would not be valid from numerical
rank and approximate multiplier signs alone; the two interval inclusions are
the parts that turn it into a rigorous statement.

## Score enclosure and limits

The sum of radii at the contact root lies in the interval recorded in
`results/local_optimum_interval.json`, beginning

```text
2.635983084917607783186569485443481730396676798274474857745771129860703849360472...
```

This is slightly above the deliberately shrunken finite-decimal certificate.
The proof is local to the named contact topology and box. It does not rule out
another configuration elsewhere with a larger score, does not establish a new
Packomania record, and does not prove global optimality.
