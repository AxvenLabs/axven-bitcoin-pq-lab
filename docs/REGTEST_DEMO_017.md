# REGTEST-DEMO-017 — independent E2E envelope validation

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds an independent fail-closed validator for the canonical real-regtest E2E evidence envelope introduced by REGTEST-DEMO-016. The validator recomputes the canonical envelope digest and rejects altered chain/transaction metadata, deployment-boundary drift, candidate-set/order drift, and false native-Windows resource-portability claims.

The validator remains separate from the runner/composer so a generated report can be checked without trusting the code path that assembled it. ML-DSA-44, ML-DSA-65, and ML-DSA-87 remain descriptive research candidates; none is selected or ranked.

Bitcoin Core/Script/consensus remain unmodified and Bitcoin Core does not validate ML-DSA. The experiment remains off-consensus on regtest. No Script/output/witness semantics, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production authorization semantics are defined.
