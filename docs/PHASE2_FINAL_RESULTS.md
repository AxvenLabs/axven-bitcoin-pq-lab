# Phase 2 Final Results — Evidence-Complete Research Checkpoint

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This document publishes the final Phase 2 evidence-complete checkpoint for the Axven Bitcoin PQ Lab. The experiment is off-consensus and uses an unmodified Bitcoin Core regtest environment as chain evidence. Bitcoin Core does not validate ML-DSA.

## Evaluated repository state

- Final evaluated main commit: `901a1fbe7b98cf41d16dd67a3218fc8d54374f5d`
- Final WSL/Linux suite: **239/239 passed, 0 failures, 0 errors, 0 skipped**
- Final canonical evidence SHA-256: `d3fdb272903fb6112db18ec6ad044fbe268937a3302da626914e540cdf863540`
- Final `e2e.json` byte-level SHA-256: `1e6e41fb445be0296b5b89e5d9d428d96d30041850cac793fa2cb3cc41adcacd`
- Independent validator recomputed the canonical evidence digest exactly and exited successfully.

The canonical evidence digest and the byte-level file digest are different identities and must not be interchanged.

## Bitcoin Core provenance boundary

The evidence records Bitcoin Core v31.1 with pinned source identity:

- source commit: `9be056a8a72b624dae9623b2f7bded92c2a21c91`
- tag: `v31.1`
- annotated tag object: `bfa6a4b79cd4c1562fd32857e3147763efae37fb`

The evidence also binds the observed Bitcoin binaries and Python/cryptography/OpenSSL/OS/architecture runtime provenance into the canonical E2E envelope. A pinned source identity plus binary digest is provenance evidence; it is not a claim of reproducible-build equivalence.

## ML-DSA candidate measurements

Phase 2 retains candidate-neutral measurements for ML-DSA-44, ML-DSA-65 and ML-DSA-87. The persisted benchmark evidence includes public-key size, secret-key serialized **size only**, signature size, raw sign/verify wall and CPU samples, derived min/median/p95/max statistics, process RSS observations, Python peak allocation observations and correctness-oracle outcomes.

No production ML-DSA parameter set is selected.

## Negative and hybrid research checks

All six tested cross-candidate signer/verifier mismatch directions were rejected:

- ML-DSA-44 -> ML-DSA-65
- ML-DSA-44 -> ML-DSA-87
- ML-DSA-65 -> ML-DSA-44
- ML-DSA-65 -> ML-DSA-87
- ML-DSA-87 -> ML-DSA-44
- ML-DSA-87 -> ML-DSA-65

This result is limited to those tested laboratory cases and is not a general network-security or domain-separation proof.

The laboratory also exercises candidate-neutral **Classical AND PQ** research semantics. The classical side is an external laboratory oracle; it is not Bitcoin Core authorization and does not modify Bitcoin Script or consensus.

## Safety and confidentiality

The publication evidence does not persist private/secret key material. Secret-key observations are serialized sizes only. Raw private/secret keys are not publication artifacts. The Phase 2 checkpoint does not publish Axven Security Engine proprietary code or internals.

## Explicit non-claims

Phase 2 does **not** claim any of the following:

- Bitcoin is quantum-safe.
- Bitcoin Core has post-quantum integration.
- Bitcoin Core validates ML-DSA.
- A Bitcoin consensus, Script, opcode, output or witness change has been implemented or selected.
- A mainnet activation or fork deployment has been designed or selected.
- A production ML-DSA parameter set has been selected.
- Legacy/lost UTXO treatment, recovery authority, trust roots, key custody or production authorization semantics have been selected.
- Transcript/evidence tamper detection is network-level replay protection.
- Native Windows Python `resource` portability has been demonstrated.

## Publication status

Within these boundaries, Phase 2 is an evidence-complete, reproducible research checkpoint suitable for public technical review. Historical checkpoint documents remain unchanged so the repository retains an auditable progression of the research.