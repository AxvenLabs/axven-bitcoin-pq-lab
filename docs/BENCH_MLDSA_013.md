# BENCH-MLDSA-013 — negative correctness oracle

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint keeps correctness evidence separate from the timing benchmark. For each named reversible research candidate — ML-DSA-44, ML-DSA-65 and ML-DSA-87 — it verifies a valid signature and fail-closed rejection of an altered message, corrupted signature, wrong same-candidate public key, truncated signature and oversized signature.

The oracle uses deterministic public lab seeds only to make candidate identity reproducible. It is not a key-custody design and must not be reused for production keys.

## Safety boundary

The isolated research hypothesis remains **Classical AND PQ**. This checkpoint does not select ML-DSA-44/65/87 as a deployment winner, define Bitcoin Script/output commitment semantics, modify Bitcoin Core or consensus, choose activation/fork policy, decide legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics. No Axven Security Engine source or internals are used or copied.

The report validator also rejects silent changes to these protected research fields and rejects candidate-set/order drift or any failed negative-case result.
