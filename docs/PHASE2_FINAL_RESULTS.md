# Phase 2 Final Results

## Evidence-Complete Off-Consensus Regtest Checkpoint

This document records the final publication checkpoint for Phase 2 of the Axven Bitcoin PQ Lab.

> **Research only.** This experiment is off-consensus. It does not modify Bitcoin Core consensus or Bitcoin Script, does not make Bitcoin Core validate ML-DSA, and is not a mainnet or production deployment claim.

## Evaluated revision

- Axven Bitcoin PQ Lab evaluated Git HEAD: `901a1fbe7b98cf41d16dd67a3218fc8d54374f5d`
- Final environment: WSL2 / x86_64
- Final test suite: **239/239 passed**
- Failures: 0
- Errors: 0
- Skipped: 0
- Suite exit: 0

Native Windows portability was not demonstrated by this checkpoint.

## Bitcoin Core provenance

The experiment used an unmodified Bitcoin Core v31.1 regtest environment.

- Bitcoin Core: `v31.1`
- Source commit: `9be056a8a72b624dae9623b2f7bded92c2a21c91`
- Tag: `v31.1`
- Tag object: `bfa6a4b79cd4c1562fd32857e3147763efae37fb`
- `bitcoind` SHA-256: `eecebe255870956243c966ff061fa0e46c4bf3e0c8313e419335aed097d82632`
- `bitcoin-cli` SHA-256: `4a939c2eb5971dc3cb87169f33a2a658d04550006cefb33ba39718dc428bb1eb`

Bitcoin Core source, consensus and Script semantics were not modified by the experiment.

## Real regtest evidence

The saved evidence-complete artifact records a real confirmed regtest transaction/UTXO:

- txid: `5026bb8c1af4d4275e408847d7ae9f301f512132354d61432ec7c03ad1e1f51b`
- vout: `0`
- confirmations: `1`
- block height: `102`
- block hash: `484d50325f01845ac91965b3cc584be4ca0d9cd8fc3d26b5306e6830972a8c58`
- serialized transaction: `222 bytes`
- weight: `561 WU`
- vbytes: `141`
- raw transaction SHA-256: `07b886150fed18a78d9de166c3560c27fc1bf9883817fad5c6bc3b9bc9d01b49`
- chain evidence SHA-256: `5d8274b7433eadb75929d0e055411e254222d8717f97c026ca91dd11cdb272af`

These transaction values are from the saved detailed evidence-complete artifact. The final-main-head transcript did not reprint the complete transaction JSON, so this publication does not characterize them as a fresh remeasurement at the final HEAD.

## ML-DSA observations

Phase 2 exercised ML-DSA-44, ML-DSA-65 and ML-DSA-87 as research candidates. This does **not** select a production parameter set.

| Candidate | Public key | Serialized secret-key representation size* | Signature | Verify wall median |
| --- | ---: | ---: | ---: | ---: |
| ML-DSA-44 | 1312 B | 32 B | 2420 B | 279346 ns |
| ML-DSA-65 | 1952 B | 32 B | 3309 B | 419194 ns |
| ML-DSA-87 | 2592 B | 32 B | 4627 B | 655441 ns |

\* The 32-byte value is the serialized representation size exposed by the tested API. It is not presented as a universal ML-DSA secret-key size. No secret/private key material is published here.

For each candidate, a valid signature was accepted and an altered transcript was rejected. Benchmark evidence SHA-256: `3aa132b069300f248ecc75da2a8abcbffc66f520593c8c01682ca1c99f5e79b2`.

Timings are observations from the recorded test environment, not universal performance claims.

## Cross-candidate negative testing

Six explicitly tested candidate-mismatch directions were rejected:

- ML-DSA-44 -> ML-DSA-65
- ML-DSA-44 -> ML-DSA-87
- ML-DSA-65 -> ML-DSA-44
- ML-DSA-65 -> ML-DSA-87
- ML-DSA-87 -> ML-DSA-44
- ML-DSA-87 -> ML-DSA-65

Result: **6/6 tested mismatches rejected**.

This is a result for these six tested cases only. It is not a general proof of domain separation or cryptographic security.

## Classical AND PQ laboratory semantics

The off-consensus laboratory composition exercised a Classical AND PQ authorization model for all three candidates. In the tested model, authorization required both the external classical laboratory boolean and the PQ verification result. The classical input is an external laboratory boolean oracle; it is **not** Bitcoin Core authorization.

No Bitcoin Script, output, witness, activation, fork, recovery, trust-root, custody or lost-UTXO production policy is selected by this experiment.

## Provenance and independent validation

Provenance is embedded into and digest-bound by the canonical E2E evidence.

- Provenance SHA-256: `22458f34ff52ff0e21308d9af7a7c4c36998c198c389aeef6f37828c3c7ef691`
- Phase 2 final canonical evidence SHA-256: `d3fdb272903fb6112db18ec6ad044fbe268937a3302da626914e540cdf863540`
- Independent validator recomputation: **exact canonical digest match**
- Independent validator exit: `0`
- Final `e2e.json` byte-level SHA-256: `1e6e41fb445be0296b5b89e5d9d428d96d30041850cac793fa2cb3cc41adcacd`

The canonical evidence digest and the byte-level `e2e.json` file digest are different identifiers and must not be conflated.

Tamper/fail-closed coverage in the final suite included vout, chain, benchmark, provenance, candidate and safety-overclaim cases. The final suite observed the expected rejection behavior. Standalone shell exit codes for each individual tamper category were not captured and are therefore not claimed.

## Publication boundary

This checkpoint supports the statement that Axven Bitcoin PQ Lab completed a reproducible, evidence-driven **off-consensus Bitcoin regtest research experiment** covering real regtest transaction evidence, candidate-neutral ML-DSA-44/65/87 measurements, tested Classical AND PQ laboratory semantics, negative mismatch tests, provenance binding and independent canonical-evidence validation.

It does **not** support claims that:

- Bitcoin is quantum-safe.
- Bitcoin Core has integrated post-quantum cryptography.
- Bitcoin Core validates ML-DSA.
- A production/mainnet migration is complete or ready.
- Consensus or Bitcoin Script integration has been completed.
- A winning or production ML-DSA parameter set has been selected.
- Bitcoin Script/output/witness semantics or activation policy have been selected.

## Audit-trail limitations

Three metadata gaps do not change the recorded Phase 2 test outcome but remain explicit:

1. The final-main-head runner's exact invocation/exit line was not captured as a separate publication record.
2. Separate byte-level SHA-256 values for each of the five final-main-head component artifact files were not captured.
3. Standalone validator process exit codes for each of the six tamper categories were not captured; their expected rejection is recorded through the final test suite.

Phase 2 is therefore published as an **evidence-complete research checkpoint**, not as a production or consensus-integration milestone.
