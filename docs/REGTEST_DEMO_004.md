# REGTEST-DEMO-004 — fail-closed hybrid evidence validator

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds a deterministic evidence envelope and independent fail-closed validator around the off-consensus REGTEST-DEMO-003 hybrid authorization transcript. The evidence binds the validated regtest transcript to the complete Classical AND PQ research truth table and a canonical SHA-256 digest.

The validator rebuilds the canonical transcript and evidence from protected inputs and rejects field drift, extra fields, changed authorization results, changed digests, non-boolean verifier results, mainnet intent, Script/consensus flags, and candidate-selection drift. ML-DSA-44, ML-DSA-65, and ML-DSA-87 remain named research candidates without ranking or selection.

This remains an isolated reversible laboratory artifact. It is not a Bitcoin transaction, Script program, output commitment, witness format, soft-fork proposal, activation rule, consensus change, mainnet deployment mechanism, recovery policy, trust-root design, or key-custody design. Upstream Bitcoin behavior is unchanged. No coin/token or network is created or launched. No Axven Security Engine source or internals are used or copied.
