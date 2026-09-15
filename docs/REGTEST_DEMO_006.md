# REGTEST-DEMO-006 — independent hybrid harness evidence validator

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint independently validates the deterministic report emitted by REGTEST-DEMO-005 for each named research candidate, ML-DSA-44/65/87, without ranking or selecting one. It binds the research-only/off-consensus safety flags, candidate-specific signature sizes, candidate-to-transcript consistency, successful PQ verification, altered-transcript rejection, and the approved laboratory Classical AND PQ truth condition. It recomputes the canonical report SHA-256 and fails closed on tampering, schema/safety drift, or nested selection/ranking fields.

The validator consumes only public report/evidence fields; it does not handle private keys or raw signatures. Correctness/evidence validation remains separate from benchmark timing and presentation.

This isolated reversible regtest/laboratory checkpoint does not modify Bitcoin Core, define Bitcoin Script/output commitment/witness semantics, change consensus, choose activation/fork deployment, decide legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics, create a coin/token, or launch a network. Upstream Bitcoin behavior remains unchanged. No Axven Security Engine source or internals are used or copied.
