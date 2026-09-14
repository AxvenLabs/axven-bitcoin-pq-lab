# BENCH-MLDSA-017 — scaling evidence validator

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds a fail-closed, cryptography-independent validator for BENCH-MLDSA-016 verification batch-scaling evidence. The validator recomputes median and nearest-rank p95 values from raw wall-clock and CPU samples, checks the named ML-DSA-44/65/87 FIPS 204 public-key/signature sizes, requires the approved reversible research hypothesis **ML-DSA + Classical AND PQ**, preserves the open Bitcoin decision gates, and emits a deterministic SHA-256 digest over canonical JSON evidence.

The validator deliberately does not perform signature verification; correctness remains the responsibility of the separate correctness-oracle checkpoint. This keeps correctness evidence separate from timing evidence and allows benchmark artifacts to be checked without loading the ML-DSA implementation.

No ML-DSA parameter set is selected as a deployment winner. Bitcoin Core remains unmodified. This checkpoint does not define transaction layout, Script/output commitment semantics, consensus rules, mainnet activation or fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics. No Axven Security Engine source or internals are used or copied.
