# REGTEST-DEMO-019 — independent provenance validation

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This reversible checkpoint adds an independent fail-closed validator for the E2E provenance evidence introduced in REGTEST-DEMO-018. It validates the pinned Bitcoin Core v31.1 tag/commit and binary-version claim, repository/runtime identity, canonical provenance digest, and research-boundary flags.

The validator rejects provenance digest tampering, Bitcoin Core pin drift, parameter-set selection overclaims, and claims that native Windows Python `resource` portability has been demonstrated.

Bitcoin Core/Script/consensus remain unmodified. Bitcoin Core does not validate ML-DSA. ML-DSA-44/65/87 remain candidate-neutral and off-consensus. No Script/output/witness semantics, deployment parameter set, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody or production authorization semantics are selected.

Binding the validated provenance digest into the top-level E2E envelope remains a separate small checkpoint so its composition and tamper behavior can be reviewed independently.
