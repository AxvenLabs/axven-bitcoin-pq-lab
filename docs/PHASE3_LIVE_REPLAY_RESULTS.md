# Phase 3 Live Replay Evidence Checkpoint

Status: research-only, off-consensus experimental evidence.

This checkpoint records a fresh Bitcoin Core v31.1 regtest evidence run and deterministic replay validation performed after PHASE3-004. It does **not** replace or claim to reproduce the historical Phase 2 artifact.

## Safety boundary

- Bitcoin Core consensus was not modified.
- No Script, opcode, output, witness, or mainnet behavior was modified.
- The work remains off-consensus and research-only.
- No production ML-DSA parameter set was selected.
- No production recovery authority, trust root, key custody, or authorization semantics were selected.
- ML-DSA candidates and Classical AND PQ remain experimental research candidates only.

## Exact code checkpoint

PHASE3-004 exact tested head:

`36836b6685b2a67ce3deeb9b35ae3c8cdee5b995`

Targeted exact-head regression gate:

- Phase 3 replay/receipt tests: 8/8 passed.
- Phase 2 validator regression tests: 7/7 passed.
- Total: 15/15 passed.
- Linux Python: 3.12.3.
- pytest: 9.1.1.

PHASE3-004 was subsequently merged by PR #65 after exact-head GitHub CI completed successfully with no submitted reviews or review threads. Merge commit: `164cdb369182bbb6679882999a5637a369b44f0d`.

## Bitcoin Core provenance used for the live run

- Bitcoin Core binary version: v31.1.0.
- Source/tag commit: `9be056a8a72b624dae9623b2f7bded92c2a21c91`.
- Annotated v31.1 tag object: `bfa6a4b79cd4c1562fd32857e3147763efae37fb`.
- Linux x86_64 archive SHA-256 observed and matched against the downloaded SHA256SUMS entry: `b80d9c3e04da78fb6f0569685673418cf686fadba9042d926d13fb87ff503f9e`.

This checkpoint does not claim independent PGP signer verification of SHA256SUMS.

## Fresh live regtest evidence

Artifact directory used during the run:

`/home/enis/axven-phase3-live-evidence`

Fresh canonical E2E evidence SHA-256:

`cf5e2c938e3d21c473bacabedc19c69d208310c937ccf4782ba5c77dffda1a2d`

Fresh `e2e.json` byte-level SHA-256:

`859c0e80a37d1af579261ac6c7aa5c52b54fe23ae184a63f9aa1ad52110c345f`

The independent E2E validator returned the same canonical evidence digest.

These are **new Phase 3 live-run values**. They are not expected to equal the historical Phase 2 evidence hashes because the checkpoint creates a fresh regtest chain, addresses, transaction, block, runtime benchmark observations, and provenance envelope.

## Deterministic replay

The same fresh `e2e.json` was replayed twice using the PHASE3-004 implementation. Both UTF-8 replay files were byte-identical.

Replay file SHA-256 for both runs:

`c00db3f7e04d19dce132dbe440e185d4a1ccabd434b07854bb1252e6ecb617b5`

Result:

`REPLAY BYTE DETERMINISM = PASS`

The independent replay-receipt validator accepted the intact receipt and returned:

`f636897379337e61ebbc6c596fb3fa95bb9b1ae320b4dfc18ea0dd72dbd9f56c`

The accepted receipt explicitly recorded:

- `bitcoin_core_modified: false`
- `mainnet_intended: false`
- `off_consensus: true`
- `parameter_set_selected: false`
- `research_only: true`
- `validator_result: accepted`

## Live fail-closed negative test

A copy of the accepted receipt was modified without changing the original. Its `input_e2e_sha256` was replaced with 64 zeroes.

The independent validator rejected the tampered receipt with:

`ValueError: replay receipt digest mismatch`

Process exit code:

`1`

Result: tampered receipt failed closed.

## Interpretation

This checkpoint demonstrates, for this exact research implementation and fresh regtest run, that validated E2E evidence can be reduced to a deterministic, safety-bounded replay receipt; repeated replay produces byte-identical output; the independent receipt validator accepts the intact receipt; and a controlled digest tamper is rejected fail-closed.

It does not demonstrate Bitcoin consensus support for ML-DSA, production readiness, mainnet authorization semantics, or selection of any post-quantum migration policy.
