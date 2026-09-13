# BENCH-MLDSA-008 — real ML-DSA candidate verification benchmark

> **Research only.** This work is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

This checkpoint measures real FIPS 204 verification for the three named ML-DSA parameter sets as **separate research candidates**:

- ML-DSA-44 — public key 1,312 bytes; signature 2,420 bytes;
- ML-DSA-65 — public key 1,952 bytes; signature 3,309 bytes;
- ML-DSA-87 — public key 2,592 bytes; signature 4,627 bytes.

The benchmark does **not** select one of these parameter sets for deployment. `parameter_set_selected` and `deployment_winner_selected` remain false in the report.

## Reproducible verifier provenance

The benchmark uses the public `mldsa` Python verifier package version **1.0.1** only as a research measurement dependency. The universal wheel is hash-pinned in `requirements-mldsa-bench.txt`.

Source and test-vector provenance are pinned to:

`FiloSottile/mldsa-py@b84df503a3cf57ede27f33a81185a63305579a95`

CI checks out that exact upstream commit and uses one valid verification vector for each parameter set. The benchmark refuses a different source commit, package version, algorithm label, public-key length, or signature length.

## Correctness before timing

Each candidate runs in its own subprocess. Before timing begins the worker:

1. verifies the pinned valid vector;
2. flips one signature byte;
3. requires the corrupted signature to be rejected.

Only after both correctness-oracle checks succeed are timing and memory samples collected.

## Measurements

For each named candidate the report records:

- public-key and signature size;
- message/context size;
- wall-clock verification median/min/max;
- process CPU-time median/min/max;
- Python allocation peak via `tracemalloc`;
- process max-RSS before/after/delta.

The subprocess boundary keeps max-RSS measurements isolated between parameter sets. These measurements describe this verifier implementation and benchmark environment; they are not universal ML-DSA costs.

## Explicit non-claims

This benchmark is not:

- a Bitcoin Script benchmark;
- a Bitcoin consensus-validation benchmark;
- a combined classical + PQ authorization benchmark;
- a parameter-set recommendation;
- a mainnet/fork/activation proposal;
- a decision about legacy/lost UTXOs, recovery, trust roots, or key custody.

The approved research hypothesis remains **classical AND PQ**, but this checkpoint measures only the ML-DSA verification factor. Bitcoin Core is not modified and no coin, token, or network is created.
