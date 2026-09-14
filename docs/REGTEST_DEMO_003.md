# REGTEST-DEMO-003 — deterministic hybrid authorization transcript

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint adds a small, reversible laboratory primitive for binding an experimental authorization transcript to a regtest outpoint and a caller-supplied message digest. It also makes the already-approved research-candidate hybrid rule explicit as a fail-closed **Classical AND PQ** gate.

The transcript is intentionally off-consensus. It is not a Bitcoin transaction, Script program, output commitment, witness format, soft-fork proposal, activation rule, or mainnet deployment mechanism. Upstream Bitcoin behavior outside the isolated experiment remains unchanged.

ML-DSA-44, ML-DSA-65, and ML-DSA-87 remain named research candidates only. The checkpoint does not rank them, select a winner, or choose production parameters. It does not decide treatment of legacy/lost UTXOs, recovery authority, trust roots, key custody, or production security semantics. It creates no coin/token and launches no network. No Axven Security Engine source or internals are used or copied.

The regression tests cover deterministic canonicalization, candidate binding, the complete Classical/PQ truth table, malformed outpoint/digest/candidate rejection, and rejection of truthy non-boolean verifier results.
