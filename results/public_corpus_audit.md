# Reproducible public-corpus audit

Snapshot date: **2026-08-08**. Acquisition status: **PASS**.

> Scope: this is a reproducible comparison inside the explicitly manifested corpus, not an exhaustive literature leaderboard. Each table uses one common exact-rational tolerance and exactly one matching author certificate.

> Safety: downloaded Python files and notebooks are parsed as data. No third-party program is imported or executed.

## Authenticated acquisitions

| Project | Pin | SHA-256 | License | Status |
| --- | --- | --- | --- | --- |
| AlphaEvolve | `8f447457957d` | `e7a304378a5ca80c…` | `Apache-2.0` | match |
| ThetaEvolve | `7c12898f5d76` | `c20023f5a4d3e140…` | `Apache-2.0` | match |
| EurekAgent | `38585790ff56` | `21304b7864de0cc4…` | `AGPL-3.0-only` | match |
| EurekAgent evaluator | `38585790ff56` | `f417007dd60c9781…` | `AGPL-3.0-only` | match |
| Hyra | `26ebfbe7d491` | `c16d2472e9516005…` | `Apache-2.0` | match |
| Station | `88f052eb1f4a` | `6a118ae8a2724904…` | `Apache-2.0` | match |
| Packomania | `mutable` | `d8dcaac266022293…` | `NOASSERTION` | match |
| Jason Liang public SOTA corpus | `c36af71dbe0b` | `b28701f7bcf4ea05…` | `NOASSERTION` | match |
| AlphaZ-CORAL | `3cd38221847e` | `405c6bf6b30d64d9…` | `NOASSERTION` | match |

## Corpus position at rational tolerance `0`

| Position | Candidate | Recomputed score | Source |
| ---: | --- | ---: | --- |
| 1 | Author exact certificate | `2.63598308491760778` | `this_repository` |
| 2 | Jason Liang csqv26 | `2.635983084893` | `jason_liang` |
| 3 | Theta corpus: 8B-w_RL@65-Formal | `2.63598307738811934` | `thetaevolve` |
| 4 | Theta corpus: ShinkaEvolve | `2.63598282664580639` | `thetaevolve` |
| 5 | Theta corpus: AlphaEvolve | `2.63586275641369812` | `thetaevolve` |

## Corpus position at rational tolerance `1e-10`

| Position | Candidate | Recomputed score | Source |
| ---: | --- | ---: | --- |
| 1 | Author 1e-10 certificate | `2.63598308647338795` | `this_repository` |
| 2 | Packomania csqv26 | `2.635983084919` | `packomania` |
| 3 | AlphaEvolve v2 | `2.6359830849176068` | `alphaevolve_v2` |
| 4 | Station | `2.63598308491754725` | `station` |
| 5 | Jason Liang csqv26 | `2.635983084893` | `jason_liang` |
| 6 | Theta corpus: 8B-w_RL@65-Formal | `2.63598307738811934` | `thetaevolve` |
| 7 | Theta corpus: ShinkaEvolve | `2.63598282664580639` | `thetaevolve` |
| 8 | Theta corpus: AlphaEvolve | `2.63586275641369812` | `thetaevolve` |

## Corpus position at rational tolerance `1e-6`

| Position | Candidate | Recomputed score | Source |
| ---: | --- | ---: | --- |
| 1 | Author 1e-6 certificate | `2.63599872089287514` | `this_repository` |
| 2 | Theta corpus: 8B-w_RL@65 | `2.63598566124089912` | `thetaevolve` |
| 3 | Hyra | `2.63598309510684482` | `hyra` |
| 4 | Packomania csqv26 | `2.635983084919` | `packomania` |
| 5 | AlphaEvolve v2 | `2.6359830849176068` | `alphaevolve_v2` |
| 6 | Station | `2.63598308491754725` | `station` |
| 7 | Jason Liang csqv26 | `2.635983084893` | `jason_liang` |
| 8 | Theta corpus: 8B-w_RL@65-Formal | `2.63598307738811934` | `thetaevolve` |
| 9 | Theta corpus: ShinkaEvolve | `2.63598282664580639` | `thetaevolve` |
| 10 | Theta corpus: AlphaEvolve | `2.63586275641369812` | `thetaevolve` |

## Uniform validity matrix

| Candidate | Score | exact | `1e-10` | `1e-6` |
| --- | ---: | :---: | :---: | :---: |
| AlphaEvolve v2 | `2.6359830849176068` | no | yes | yes |
| Theta corpus: AlphaEvolve | `2.63586275641369812` | yes | yes | yes |
| Theta corpus: 8B-w_RL@65 | `2.63598566124089912` | no | no | yes |
| Theta corpus: 8B-w_RL@65-Formal | `2.63598307738811934` | yes | yes | yes |
| Theta corpus: ShinkaEvolve | `2.63598282664580639` | yes | yes | yes |
| EurekAgent | `2.63599872085988286` | no | no | no |
| Hyra | `2.63598309510684482` | no | no | yes |
| Station | `2.63598308491754725` | no | yes | yes |
| Packomania csqv26 | `2.635983084919` | no | yes | yes |
| Jason Liang csqv26 | `2.635983084893` | yes | yes | yes |

## Source-native compatibility

These checks independently reimplement the published binary64 decision path; they do not execute the upstream evaluator.

| Candidate | Published contract reimplemented | Valid | Binary64 score |
| --- | --- | :---: | ---: |
| AlphaEvolve v2 | independent binary64 reimplementation of the notebook's zero-tolerance check | yes | `2.6359830849176076` |
| EurekAgent | independent binary64 reimplementation of adapted_validate_packing(atol=1e-6) | yes | `2.6359987208598832` |

## AlphaEvolve notebook binary64 zero-tolerance corpus position

| Position | Candidate | Binary64 score | Source |
| ---: | --- | ---: | --- |
| 1 | AlphaEvolve v2 | `2.6359830849176076` | `alphaevolve_v2` |
| 2 | Station | `2.6359830849175476` | `station` |
| 3 | Jason Liang csqv26 | `2.6359830848930002` | `jason_liang` |
| 4 | Theta corpus: 8B-w_RL@65-Formal | `2.635983077388119` | `thetaevolve` |
| 5 | Theta corpus: ShinkaEvolve | `2.6359828266458067` | `thetaevolve` |
| 6 | Theta corpus: AlphaEvolve | `2.6358627564136983` | `thetaevolve` |

## EurekAgent binary64 `atol=1e-6` corpus position

| Position | Candidate | Binary64 score | Source |
| ---: | --- | ---: | --- |
| 1 | Author 1e-6 certificate | `2.635998720892875` | `this_repository` |
| 2 | EurekAgent | `2.6359987208598832` | `eurekagent` |
| 3 | Theta corpus: 8B-w_RL@65 | `2.6359856612408987` | `thetaevolve` |
| 4 | Hyra | `2.6359830951068446` | `hyra` |
| 5 | Packomania csqv26 | `2.6359830849189998` | `packomania` |
| 6 | AlphaEvolve v2 | `2.6359830849176076` | `alphaevolve_v2` |
| 7 | Station | `2.6359830849175476` | `station` |
| 8 | Jason Liang csqv26 | `2.6359830848930002` | `jason_liang` |
| 9 | Theta corpus: 8B-w_RL@65-Formal | `2.635983077388119` | `thetaevolve` |
| 10 | Theta corpus: ShinkaEvolve | `2.6359828266458067` | `thetaevolve` |
| 11 | Theta corpus: AlphaEvolve | `2.6358627564136983` | `thetaevolve` |

## Excluded from witness rankings

| Project | Reported score | Reason |
| --- | ---: | --- |
| [AlphaZ-CORAL](https://raw.githubusercontent.com/Kurorz2004/alphaz-coral/3cd38221847e442d4b11822d2cf31646db2daa47/task1/result/best_program.py) | `not serialized` | Publishes 26 centers but derives radii by solving a linear program at runtime; it is not a serialized complete witness and is excluded from witness rankings. |
| [Numaro](https://numaro.tech/research/circle-packing-unit-square-2026/) | `2.6359830853` | No downloadable complete n=26 coordinate-and-radius witness was located in the public report. |
| [HELIX](https://arxiv.org/abs/2603.07642) | `2.6359830849` | No downloadable complete n=26 coordinate-and-radius witness was located with the paper. |

## Interpretation boundary

A position in these tables is mechanically reproducible for this pinned corpus only. It is not a claim that every paper, private run, mutable webpage, or unavailable witness has been covered. Scores from different tolerance tables are not interchangeable.
