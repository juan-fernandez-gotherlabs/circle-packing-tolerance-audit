# Data layout

Each numerical contract has its own directory. `certificate.csv` is the stable
name consumed by repository scripts; the original downloaded filename is kept
beside it with byte-identical contents.

| Directory | Stable file | Original filename | Tolerance |
| --- | --- | --- | ---: |
| `tolerance_1e-6/` | `certificate.csv` | `coordinates_public_record.csv` | `1e-6` |
| `tolerance_1e-10/` | `certificate.csv` | `coordinates_internal_1e10.csv` | `1e-10` |
| `exact/` | `certificate.csv` | `strict_high_precision.csv` | `0` |

Every directory also preserves the model explanation for that regime. The
exact directory contains the high-precision report and the older float64 strict
reference program. Historical continuation artifacts are kept separately under
`historical_search/` so their incomplete temporary paths cannot be mistaken for
the clean reproduction pipeline in `scripts/`.
