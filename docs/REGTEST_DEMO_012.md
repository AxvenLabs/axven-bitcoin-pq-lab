# REGTEST-DEMO-012 — real-regtest chain evidence runner

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint begins the single reproducible E2E evidence path from the verified 2026-09-15 baseline. `scripts/run_regtest_e2e_checkpoint.sh` starts an unmodified Bitcoin Core regtest node, creates a wallet, matures test BTC, creates and confirms a real transaction, and records the observed outpoint amount/confirmations plus exact confirming block hash/height and transaction serialized bytes/weight/vbytes. Raw transaction bytes are hashed rather than published in the canonical report.

`scripts.regtest_chain_evidence` validates metric consistency and emits a deterministic canonical evidence digest. Unit tests cover deterministic output and fail-closed inconsistent/unconfirmed observations.

This checkpoint intentionally does **not** claim Bitcoin Core validates ML-DSA. The existing ML-DSA-44/65/87 and Classical AND PQ laboratory harness remains off-consensus and is not yet invoked by this shell runner; composing that already-tested layer into one final E2E report is the next reversible checkpoint.

Bitcoin Core/Script/consensus remain unmodified. No Script/output/witness semantics, ML-DSA deployment parameter set, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production authorization semantics are selected. Native Windows `resource` portability remains open; WSL/Linux remains the demonstrated environment.
