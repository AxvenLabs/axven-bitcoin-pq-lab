# BENCH-MLDSA-018 — candidate-neutral scaling summary

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds a deterministic summary layer over already-validated BENCH-MLDSA-016/017 evidence. It reports ML-DSA-44, ML-DSA-65 and ML-DSA-87 public-key/signature sizes, process RSS observations, batch medians, and simple integer per-verification derived timing values while preserving candidate order.

The summary is intentionally candidate-neutral: it performs no ranking, scoring, recommendation, preference, winner selection, or parameter-set selection. Source evidence must first pass the BENCH-MLDSA-017 fail-closed validator.

The approved reversible research hypothesis remains **ML-DSA + Classical AND PQ** for this isolated laboratory track only. Bitcoin Core is not modified here. No Bitcoin Script/output commitment semantics, consensus/mainnet activation, fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics are selected. No Axven Security Engine source or internals are used or copied.
