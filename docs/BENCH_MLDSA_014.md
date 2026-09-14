# BENCH-MLDSA-014 — cross-candidate correctness oracle

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint extends the ML-DSA correctness oracle so every named reversible research candidate — ML-DSA-44, ML-DSA-65 and ML-DSA-87 — must reject a signature produced by either of the other candidate parameter sets.

The resulting 3-by-2 rejection matrix is validated fail-closed and kept separate from benchmark timing collection. The validator rejects candidate-order drift, matrix-order drift, false rejection results and schema downgrade. Deterministic public lab seeds exist only to make candidate identity reproducible and are not a key-custody design.

## Safety boundary

The isolated research hypothesis remains **ML-DSA + Classical AND PQ** only as a reversible regtest/lab research candidate. This checkpoint does not select ML-DSA-44/65/87 as a deployment winner, define Bitcoin Script/output commitment semantics, modify Bitcoin Core or Bitcoin consensus, choose activation/fork policy, decide legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics. No Axven Security Engine source or internals are used or copied.
