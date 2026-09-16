# REGTEST-DEMO-014 — raw benchmark evidence envelope

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This reversible checkpoint packages the existing candidate-neutral ML-DSA verification benchmark as raw evidence for the real-regtest E2E path. It records every wall-clock and process-CPU verification sample, median/p95/min/max summaries, Python peak allocation, process max RSS, environment provenance, and a canonical SHA-256 evidence digest for ML-DSA-44/65/87 without ranking or selecting a candidate.

Correctness remains a separate oracle: valid signatures must verify and altered messages must be rejected before timing collection is accepted. Timing/resource observations are descriptive measurements and are not deterministic values; the evidence digest binds the exact observed run rather than claiming repeatable timings across machines.

Bitcoin Core/Script/consensus remain unmodified and Bitcoin Core does not validate ML-DSA. No Script/output/witness semantics, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, production authorization semantics, or ML-DSA deployment parameter set are selected. Native Windows Python `resource` portability remains open; WSL/Linux remains the demonstrated environment.
