# REGTEST-DEMO-005 — runnable candidate-neutral ML-DSA hybrid harness

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint connects the deterministic off-consensus regtest transcript/evidence layer to real ML-DSA signing and verification for all three named research candidates: ML-DSA-44, ML-DSA-65, and ML-DSA-87. It deliberately does not select a parameter set. The classical side of the approved research-only Classical AND PQ gate remains an external boolean laboratory oracle, so this checkpoint does not silently choose a classical production authorization scheme.

For reproducible laboratory identity, each candidate uses a public deterministic seed that is explicitly unsuitable for secret production key material. The harness signs the transcript digest, verifies the valid signature, requires an altered transcript to fail verification, then feeds only the resulting boolean PQ validity into the already validated hybrid evidence layer. The report contains no private key or raw signature and exposes only deterministic public-key hash/size and validated evidence fields.

This is an isolated reversible regtest/laboratory artifact. It does not modify Bitcoin Core, define Bitcoin Script/output commitment/witness semantics, change consensus, choose activation or fork deployment, decide legacy/lost UTXO treatment, define recovery authority or trust roots, choose key custody, create a coin/token, or launch a network. Upstream Bitcoin behavior remains unchanged. No Axven Security Engine source or internals are used or copied.
