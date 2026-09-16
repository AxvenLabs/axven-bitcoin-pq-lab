# REGTEST-DEMO-018 — E2E execution provenance

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This reversible checkpoint records execution provenance beside the existing canonical E2E evidence: repository commit, pinned Bitcoin Core v31.1 binary version plus the already-locked upstream tag/commit identity, Python version, `cryptography` version, OS identity and machine architecture.

The runner still uses an unmodified Bitcoin Core regtest node. Bitcoin Core does not validate ML-DSA. The ML-DSA-44/65/87 laboratory layer remains off-consensus and candidate-neutral. No Bitcoin Script/output/witness semantics, deployment parameter set, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody or production authorization semantics are selected.

Native Windows Python `resource` portability remains open; Linux/WSL remains the demonstrated resource-measurement environment.

Provenance is intentionally emitted as an independent evidence file in this checkpoint. Binding its digest into the top-level E2E envelope is deferred until a separate fail-closed provenance validator is present.
