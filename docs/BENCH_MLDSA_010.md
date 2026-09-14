# BENCH-MLDSA-010 — recomputable raw timing evidence

> **Research only.** Not endorsed by Bitcoin Core and not intended for mainnet deployment.

This checkpoint makes the existing ML-DSA-44/65/87 research benchmark independently recomputable from the emitted evidence instead of trusting only aggregate timing fields.

For every named candidate the report now retains the complete wall-clock and process-CPU timing sample arrays, together with median, nearest-rank p95, minimum, and maximum values. CI recomputes those aggregates from the raw samples and fails closed if the report is internally inconsistent.

The correctness oracle remains separate from the timing loop. Public-key/signature size checks remain pinned to the expected FIPS 204 sizes, and process RSS plus Python allocation-peak evidence remain present.

## Interpretation boundary

Raw timing evidence improves reproducibility; it does **not** make measurements from different machines directly interchangeable. The runtime/backend and host still matter.

No ML-DSA parameter set is selected for deployment. This checkpoint does not define Bitcoin Script or output-commitment semantics, alter Bitcoin Core or consensus, select activation/fork policy, decide legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics. The isolated research hypothesis remains **classical AND PQ** and the benchmark still measures only the ML-DSA factor.
