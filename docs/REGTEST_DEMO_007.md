# REGTEST-DEMO-007 — deterministic public hybrid vector bundle

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint packages the already validated REGTEST-DEMO-005/006 behavior into a deterministic public vector bundle for all three named research candidates, ML-DSA-44/65/87, and both classical-oracle outcomes. Each vector records only public digests, signature size, altered-transcript rejection, and the resulting Classical AND PQ authorization boolean. It does not expose private keys, deterministic lab seeds, or raw signatures.

The bundle is intended as a reproducible correctness artifact, separate from timing benchmarks. It preserves candidate order without ranking, scoring, recommendation, preference, winner selection, or parameter-set selection.

This remains an isolated reversible regtest/laboratory artifact. It does not modify Bitcoin Core, define Bitcoin Script/output commitment/witness semantics, change consensus, choose activation/fork deployment, decide legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics, create a coin/token, or launch a network. Upstream Bitcoin behavior remains unchanged. No Axven Security Engine source or internals are used or copied.
