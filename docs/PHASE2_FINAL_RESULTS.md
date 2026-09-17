# Phase 2 Final Results

**Research only. Off-consensus. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This document records the final publication checkpoint for Phase 2 of Axven Bitcoin PQ Lab. It does **not** claim that Bitcoin is quantum-safe or that post-quantum cryptography has been integrated into Bitcoin Core.

## Evaluated repository state

- Final evaluated Git HEAD: `901a1fbe7b98cf41d16dd67a3218fc8d54374f5d`
- Final WSL/Linux suite: **239/239 passed, 0 failures, 0 errors, 0 skipped**
- Independent final validator: **exit 0**
- Phase 2 final canonical evidence SHA-256: `d3fdb272903fb6112db18ec6ad044fbe268937a3302da626914e540cdf863540`
- Final `e2e.json` byte-level SHA-256: `1e6e41fb445be0296b5b89e5d9d428d96d30041850cac793fa2cb3cc41adcacd`
- Independent validator recomputation matched the canonical evidence digest exactly.

Native Windows Python `resource` portability remains **not demonstrated**. The final acceptance run above was performed under WSL/Linux.

## Bitcoin Core provenance

The experiment used Bitcoin Core v31.1 on regtest with pinned source identity:

- source commit: `9be056a8a72b624dae9623b2f7bded92c2a21c91`
- tag: `v31.1`
- annotated tag object: `bfa6a4b79cd4c1562fd32857e3147763efae37fb`
- `bitcoind` SHA-256: `eecebe255870956243c966ff061fa0e46c4bf3e0c8313e419335aed097d82632`
- `bitcoin-cli` SHA-256: `4a939c2eb5971dc3cb87169f33a2a658d04550006cefb33ba39718dc428bb1eb`
- Python: 3.12.3
- cryptography: 48.0.0
- OpenSSL runtime: `OpenSSL 4.0.0 14 Apr 2026`

These source pins and binary digests identify the tested inputs; they are **not** a reproducible-build proof that independently derives the binaries from the pinned source.

## Real regtest evidence

The evidence-complete run bound a real Bitcoin Core v31.1 regtest transaction/outpoint into the final evidence envelope:

- txid: `5026bb8c1af4d4275e408847d7ae9f301f512132354d61432ec7c03ad1e1f51b`
- vout: `0`
- confirmations: `1`
- block height: `102`
- block hash: `484d50325f01845ac91965b3cc584be4ca0d9cd8fc3d26b5306e6830972a8c58`
- serialized transaction bytes: `222`
- weight: `561`
- vbytes: `141`
- raw transaction SHA-256: `07b886150fed18a78d9de166c3560c27fc1bf9883817fad5c6bc3b9bc9d01b49`

Bitcoin Core itself does **not** validate ML-DSA in this experiment. ML-DSA validation is performed by the external laboratory code and is bound to regtest evidence off-consensus.

## Candidate-neutral ML-DSA observations

Phase 2 exercised ML-DSA-44, ML-DSA-65 and ML-DSA-87 as research candidates. No production parameter set was selected.

| Candidate | Public key bytes | Secret-key serialized size only | Signature bytes | Valid accepted | Altered transcript rejected |
| --- | ---: | ---: | ---: | --- | --- |
| ML-DSA-44 | 1312 | 32 | 2420 | yes | yes |
| ML-DSA-65 | 1952 | 32 | 3309 | yes | yes |
| ML-DSA-87 | 2592 | 32 | 4627 | yes | yes |

The persistent benchmark evidence also contains the raw sign/verify wall-clock and CPU samples, derived min/median/p95/max summaries, RSS observations and Python peak-allocation observations for the tested run. These are observations from the recorded environment, not universal performance claims.

Secret/private key material is not published or persisted by the Phase 2 evidence artifact. Only the serialized secret-key **size** is recorded. Raw signatures are not persisted in the publication evidence.

## Cross-candidate fail-closed checks

All six tested mismatched signer/verifier candidate directions rejected:

- ML-DSA-44 -> ML-DSA-65
- ML-DSA-44 -> ML-DSA-87
- ML-DSA-65 -> ML-DSA-44
- ML-DSA-65 -> ML-DSA-87
- ML-DSA-87 -> ML-DSA-44
- ML-DSA-87 -> ML-DSA-65

Result: **6/6 tested mismatches rejected**.

This result is limited to the tested wrong-candidate/key/signature cases in the laboratory backend. It is not a general proof of domain separation, replay protection or network security.

## Classical AND PQ research semantics

The isolated laboratory model retained the research candidate semantics **Classical AND PQ**. For each candidate, the positive case required both laboratory inputs to be true, and the negative case with classical=false and PQ=true remained unauthorized.

The classical verifier in this experiment is an external laboratory boolean oracle. It is not Bitcoin Core authorization and does not define Bitcoin Script, output, witness or production authorization semantics.

## Evidence binding and independent validation

Phase 2 binds chain evidence, composition evidence, benchmark evidence and runtime/Core provenance into the top-level canonical E2E evidence digest. The independent validator recalculates nested and top-level canonical digests and fails closed on the covered evidence/safety-boundary drift.

Final canonical evidence SHA-256:

`d3fdb272903fb6112db18ec6ad044fbe268937a3302da626914e540cdf863540`

The independent validator reproduced this exact digest with exit 0 on the final WSL/Linux closure.

## Explicit non-claims

Phase 2 does **not** establish any of the following:

- Bitcoin is quantum-safe.
- Bitcoin Core has post-quantum integration.
- Bitcoin Core validates ML-DSA.
- A Bitcoin consensus or Script change has been implemented.
- Any opcode, output or witness semantics have been selected.
- Mainnet deployment or activation has been designed or approved.
- A production ML-DSA parameter set has been selected.
- Legacy/lost UTXO treatment has been selected.
- Recovery authority, trust roots or key-custody policy have been selected.
- Transcript/evidence tamper detection is network-level replay protection.

Bitcoin Core, consensus and Script remain unmodified by this experiment.

## Publication limitations

The final-main-head transcript did not retain the exact final runner invocation/runner-exit line, separate byte-level SHA-256 values for every nested artifact, or standalone process exit codes for every individual tamper category. The final suite nevertheless covered the corresponding fail-closed tamper tests and completed 239/239 successfully. These missing audit metadata items must not be invented or represented as captured.
