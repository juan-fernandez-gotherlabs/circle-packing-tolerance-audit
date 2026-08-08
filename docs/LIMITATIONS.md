# Limitations and non-claims

1. **No global optimum proof.** The exact certificate is a rigorous feasible
   lower bound and a numerically isolated stationary configuration. It does not
   enumerate every possible packing or contact graph.
2. **No new Packomania decimal claimed.** The exact score rounds to the current
   Packomania `n=26` value at 12 decimal places. The downloadable Packomania
   ASCII file is too rounded to resolve the additional digits.
3. **Corpus-bounded rankings.** “Rank 1” means first among the complete public
   artifacts in the frozen audit dated 2026-08-06. Private results and claims
   without witnesses are outside the ranking.
4. **Tolerance-specific benchmark results.** The `1e-6` and `1e-10`
   certificates are invalid at tolerance zero and must never be described as
   strict geometric records.
5. **Historical search state was incomplete.** The original response attached
   summaries and logs, but not `contact_flip.py` or its `.npz` seeds. The module
   and seed generation in this repository are a documented reimplementation,
   not a byte-identical recovery of the temporary sandbox.
6. **Historical narrative and final logs differ.** The model response described
   390 additional second-layer transitions and a third layer paused at 264/468.
   The attached final logs contain 312 second-layer transitions and 468/468
   third-layer transitions. The defensible interpretation is 390 cumulative
   traces through layers 1 and 2 (`78+312`), followed by 468 third-layer traces.
   This repository reports the file counts and preserves the earlier prose as
   historical context. No global conclusion follows from completing three layers.
7. **Stationarity is not formal local optimality.** Full rank and signed KKT
   multipliers are strong numerical diagnostics. A validated interval proof of
   the nearby root and multiplier signs would strengthen a journal submission.
8. **External licensing varies.** Unlicensed or ambiguously licensed upstream
   witnesses are not vendored. Their derived numerical audit metrics and source
   identifiers are retained for reproducibility and attribution.
