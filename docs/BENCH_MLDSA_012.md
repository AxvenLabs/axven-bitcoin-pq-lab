# BENCH-MLDSA-012 — reproducible report adapter

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adapts the existing ML-DSA-44, ML-DSA-65 and ML-DSA-87 verification measurements into the repository's generic benchmark-report contract. It preserves the raw wall-clock and CPU samples and validates each adapted report independently before emission.

The adapter requires callers to provide an explicit source identity and UTC timestamp. Machine/runtime metadata is collected through the existing benchmark environment helper. Every candidate produces separate wall-clock and CPU reports with the existing nearest-rank p95 methodology.

## Safety boundary

This checkpoint does **not** select ML-DSA-44, ML-DSA-65 or ML-DSA-87 as a deployment winner. The approved lab hypothesis remains **Classical AND PQ** only for reversible isolated research. No Bitcoin Script/output commitment semantics, Bitcoin consensus change, mainnet activation/fork policy, legacy/lost UTXO policy, recovery authority, trust root, key custody or production security semantics are selected. Bitcoin Core is not modified and no Axven Security Engine source or internals are used.

## Fail-closed checks

The adapter rejects candidate-set/order drift, non-ML-DSA input, Classical-OR-PQ semantics, any parameter-set/deployment-winner selection, Bitcoin Core/Script/consensus selection flags, malformed iteration counts, sample-count mismatch and aggregate statistics that cannot be recomputed from raw samples.

`warmups` is recorded as zero because the current ML-DSA candidate runner does not perform a separate warmup phase. A later checkpoint may add an explicit warmup phase without changing the research decision gates.
