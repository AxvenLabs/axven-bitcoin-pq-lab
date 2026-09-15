# REGTEST-DEMO-008 — independent public vector-bundle validator

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds an independent fail-closed validator for the deterministic public correctness-vector bundle produced by REGTEST-DEMO-007. It binds the complete ML-DSA-44/65/87 × classical-false/true matrix, candidate-specific signature sizes, public digest shapes, altered-transcript rejection, the Classical AND PQ authorization result, and the canonical bundle SHA-256.

The validator rejects candidate reordering, field/schema drift, safety-boundary drift, digest tampering, incorrect authorization results, selection/ranking fields, and accidental exposure fields for private keys, lab seeds, or raw signatures. Correctness evidence remains separate from timing benchmarks and no candidate is ranked or selected.

This remains an isolated reversible regtest/laboratory artifact. It does not modify Bitcoin Core, define Bitcoin Script/output commitment/witness semantics, change consensus, choose activation/fork deployment, decide legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics, create a coin/token, or launch a network. Upstream Bitcoin behavior remains unchanged. No Axven Security Engine source or internals are used or copied.
