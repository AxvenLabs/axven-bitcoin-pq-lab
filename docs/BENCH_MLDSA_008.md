# BENCH-MLDSA-008 — named ML-DSA candidate comparison

> **Research only.** Not endorsed by Bitcoin Core and not intended for mainnet deployment.

This checkpoint measures ML-DSA-44, ML-DSA-65, and ML-DSA-87 as **named reversible research candidates** using `cryptography==48.0.0`. Candidate measurement does not select a Bitcoin or production deployment winner.

The benchmark reports public-key bytes, signature bytes, verification median/min/max wall-clock nanoseconds, process maximum RSS, runtime/backend provenance, and an explicit correctness oracle. The correctness oracle first verifies a valid signature and separately requires the same signature to fail for an altered message before timing samples are collected.

The private keys are reconstructed from deterministic 32-byte lab seeds solely to make candidate key identity reproducible. Those seeds are public test material and must never be treated as production key material.

## Run

```bash
python -m pip install cryptography==48.0.0
python -m scripts.benchmark_mldsa_candidates --iterations 25
```

## Interpretation boundary

These measurements answer only: “On this recorded software/backend/machine environment, what size and local verification-cost characteristics do these three ML-DSA parameter sets exhibit?” They do **not** establish Bitcoin Script semantics, output commitment design, consensus rules, activation, mainnet deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics.

The already approved hybrid research hypothesis remains **classical AND PQ**, but this benchmark does not implement a Bitcoin authorization path and does not patch Bitcoin Core.

No proprietary Axven Security Engine source or internals are used or copied.
