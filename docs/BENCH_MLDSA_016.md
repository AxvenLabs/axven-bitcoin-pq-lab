# BENCH-MLDSA-016 — verification batch scaling

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds a process-level batch-scaling benchmark for the three named reversible research candidates **ML-DSA-44, ML-DSA-65 and ML-DSA-87**. It records raw wall-clock and CPU samples for repeated verification batches (default 1, 10 and 100 verifications) plus process max-RSS evidence.

The benchmark performs only an untimed valid-signature preflight. Negative-message, corrupted-signature, wrong-key and cross-candidate rejection remain in the separate correctness oracle so correctness evidence is not silently conflated with timing evidence.

The approved isolated research hypothesis remains **ML-DSA + Classical AND PQ**. This checkpoint does not select ML-DSA-44/65/87 as a deployment winner and does not define Bitcoin transaction layout, Script/output commitment semantics, consensus rules, mainnet activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics. Bitcoin Core remains unmodified.