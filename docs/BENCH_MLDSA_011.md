# BENCH-MLDSA-011 — fail-closed benchmark evidence validation

> **Research only.** Not endorsed by Bitcoin Core and not intended for mainnet deployment.

This checkpoint adds an independent consumer-side validator for the ML-DSA-44/65/87 benchmark evidence emitted by the lab. The validator recomputes timing aggregates from raw samples, checks the exact named candidate set and FIPS 204 key/signature sizes, verifies correctness-oracle results, requires runtime provenance fields, and fails closed if any protected selection flag changes.

The validator also emits a SHA-256 digest of canonical JSON evidence. The digest identifies a specific report byte-semantically after canonical key ordering; it is not a cryptographic attestation of the machine that produced the measurements.

This checkpoint does not select ML-DSA-44, ML-DSA-65, or ML-DSA-87 for deployment. It does not define Bitcoin Script/output commitment semantics, alter Bitcoin Core or consensus, choose activation/fork policy, decide legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics. The isolated reversible research hypothesis remains **Classical AND PQ**.
