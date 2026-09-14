# BENCH-MLDSA-019 — candidate-neutral summary evidence validator

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds a fail-closed validator for the deterministic candidate-neutral summary produced by BENCH-MLDSA-018. It binds the named ML-DSA-44/65/87 candidate order, standardized public-key/signature sizes, non-negative process RSS observations, batch order 1/10/100, and the arithmetic relationship between total median timing and the displayed integer per-verification value.

The validator rejects schema downgrade, candidate reordering, size drift, inconsistent derived timing, selection/ranking flags, and nested winner/recommendation/rank/score/preference fields. It also emits a SHA-256 digest over canonical JSON after validation so summary evidence can be reproduced independently.

This remains a candidate-neutral laboratory measurement checkpoint. It does **not** select ML-DSA-44, ML-DSA-65, or ML-DSA-87; modify Bitcoin Core; define Bitcoin Script/output commitment semantics; change consensus; select activation/fork deployment; decide legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics; create a coin/token; or launch a network. No Axven Security Engine source or internals are used or copied.
