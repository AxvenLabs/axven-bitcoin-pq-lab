# REGTEST-DEMO-020 — Phase 2 evidence-complete E2E

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint does not add a Bitcoin consensus, Script, opcode, output, witness or mainnet feature. It makes the existing off-consensus regtest experiment evidence-complete.

The one-command runner now requires a pinned Bitcoin Core v31.1 source checkout and built binary directory, verifies source commit `9be056a8a72b624dae9623b2f7bded92c2a21c91` and annotated tag object `bfa6a4b79cd4c1562fd32857e3147763efae37fb`, records binary SHA-256 identities plus Python/cryptography/OpenSSL/OS/architecture provenance, and binds that provenance into the top-level canonical E2E digest.

Raw ML-DSA-44/65/87 benchmark evidence is persisted, including public/secret-key **sizes only**, signature size, raw sign/verify wall and CPU samples, derived min/median/p95/max, RSS and Python allocation observations, correctness oracles, and six explicit wrong-candidate key/signature rejection cases. Private/secret key material and raw signatures are not persisted.

Chain evidence preserves confirmed outpoint amount/confirmations, block hash/height, raw transaction digest and serialized size/weight/vbytes. Independent validation recomputes nested and top-level canonical digests and fails closed on provenance, chain, benchmark, candidate or safety-boundary drift.

Native Windows Python `resource` portability remains explicitly not demonstrated. ML-DSA-44/65/87 remain candidate-neutral; no production parameter set is selected.