# REGTEST-DEMO-009 — deterministic public vector manifest

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds a small deterministic manifest over the independently validated REGTEST-DEMO-007/008 public correctness-vector bundle. The manifest binds the validated source bundle SHA-256, six-vector count, candidate-neutral ML-DSA-44/65/87 ordering, Classical AND PQ research semantics, and the laboratory safety boundary without copying private keys, lab seeds, raw signatures, or timing data.

The manifest remains correctness metadata only. It does not rank, score, recommend, prefer, or select an ML-DSA parameter set and does not define a Bitcoin transaction, Script/output/witness commitment, consensus rule, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust root, key-custody model, or production security semantics.

This remains an isolated reversible regtest/laboratory artifact. Upstream Bitcoin behavior is unchanged; no coin/token or network is created or launched. No Axven Security Engine source or internals are used or copied.
