# REGTEST-DEMO-016 — canonical E2E evidence envelope

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint makes the real-regtest runner emit one top-level machine-readable evidence envelope. The envelope binds the independently generated chain-evidence, candidate-neutral ML-DSA/Classical-AND-PQ composition, and raw benchmark/resource evidence digests while retaining the observed outpoint, confirmation block, and transaction metrics.

The composition remains off-consensus. Bitcoin Core/Script/consensus are unmodified and Bitcoin Core does not validate ML-DSA. ML-DSA-44, ML-DSA-65, and ML-DSA-87 remain descriptive research candidates; no deployment parameter set is selected or ranked.

Fail-closed tests reject chain/composition outpoint mismatch, deployment-boundary drift, and any false claim that native Windows `resource` portability has been demonstrated. Linux/WSL remains the demonstrated resource-measurement environment.

No Script/output/witness semantics, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production authorization semantics are defined by this checkpoint.
