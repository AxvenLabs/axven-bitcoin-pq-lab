# REGTEST-DEMO-010 — fail-closed vector manifest validation

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint independently validates the deterministic public manifest produced by REGTEST-DEMO-009. It binds the regtest/off-consensus safety flags, candidate-neutral ML-DSA-44/65/87 ordering, Classical AND PQ research semantics, six-vector count, correctness-oracle separation, absence of timing data, source-bundle digest shape, and the manifest's canonical SHA-256 digest.

The validator fails closed on safety-boundary drift, candidate reordering, digest tampering, candidate-selection/ranking fields, and secret/private-key/raw-signature fields. It does not select an ML-DSA parameter set or define Bitcoin Script/output/witness semantics.

This remains an isolated reversible laboratory artifact. It does not modify Bitcoin Core, change consensus, choose activation/fork deployment, decide legacy/lost UTXO treatment, define recovery authority or trust roots, choose key custody or production security semantics, create a coin/token, or launch a network. No Axven Security Engine source or internals are used or copied.
