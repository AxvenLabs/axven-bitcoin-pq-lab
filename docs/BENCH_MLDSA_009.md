# BENCH-MLDSA-009 — measurement hardening

> **Research only.** Not endorsed by Bitcoin Core and not intended for mainnet deployment.

This checkpoint hardens the existing named ML-DSA-44/65/87 research benchmark without selecting a deployment parameter set.

## Added measurements and checks

For each candidate the benchmark now records:

- verification wall-clock median/min/max;
- verification process CPU-time median/min/max;
- Python allocation peak measured with `tracemalloc`;
- process maximum RSS and max-RSS delta;
- FIPS 204 public-key and signature byte lengths;
- a separate correctness oracle requiring a valid signature to verify and an altered message to raise `InvalidSignature`.

The benchmark fails closed if the backend produces an unexpected public-key or signature size:

| Candidate | Public key | Signature |
| --- | ---: | ---: |
| ML-DSA-44 | 1,312 B | 2,420 B |
| ML-DSA-65 | 1,952 B | 3,309 B |
| ML-DSA-87 | 2,592 B | 4,627 B |

## Interpretation boundary

The measurements describe the pinned benchmark backend and machine/runtime recorded in the report. They do not select ML-DSA-44, ML-DSA-65, or ML-DSA-87 for Bitcoin or production use.

This checkpoint does not define Bitcoin Script/output commitment semantics, change Bitcoin consensus, select activation/fork policy, decide legacy or lost UTXO treatment, create recovery authority, choose trust roots or key custody, or alter production security semantics. Bitcoin Core remains unmodified. The approved isolated research hypothesis remains **classical AND PQ**, but this benchmark measures only the ML-DSA factor.
