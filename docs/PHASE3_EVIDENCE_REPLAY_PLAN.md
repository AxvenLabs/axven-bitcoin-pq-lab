# Phase 3 — Evidence Replay Boundary

Status: research-only planning checkpoint.

This document defines the first Phase 3 work item after the Phase 2 evidence-complete closure. It deliberately does **not** define or modify Bitcoin consensus, Script, opcodes, output/witness semantics, mainnet behavior, production authorization, recovery, trust roots, key custody, or a production ML-DSA parameter choice.

## Goal

Make Phase 2 evidence independently replayable as a deterministic verification exercise without requiring new Bitcoin behavior.

A replay implementation may consume an existing Phase 2 E2E evidence envelope and must:

1. treat the recorded envelope as untrusted input;
2. independently recompute all canonical digests already defined by the Phase 2 validators;
3. verify nested chain, composition, benchmark, provenance, and top-level bindings;
4. verify the recorded candidate-neutral ML-DSA correctness and cross-candidate negative-test evidence without selecting a preferred candidate;
5. fail closed on missing, duplicated, reordered, malformed, or overclaiming safety-boundary fields;
6. emit a deterministic, secret-free replay receipt containing only input digest(s), validator result(s), schema/version identifiers, and explicit research/off-consensus safety flags.

## Non-goals

The replay checkpoint must not:

- modify Bitcoin Core source or binaries;
- define a Bitcoin Script, opcode, output, witness, sighash, soft-fork, hard-fork, activation, or deployment mechanism;
- claim Bitcoin Core validates ML-DSA;
- create a mainnet/testnet integration path;
- choose ML-DSA-44, ML-DSA-65, or ML-DSA-87 for production;
- introduce recovery authority, trust-root, custody, or production authorization semantics;
- persist private/secret key material or raw signatures.

## Acceptance criteria for a future runnable checkpoint

A future implementation is acceptable only when all of the following are demonstrated on its exact PR head:

- deterministic replay receipt for identical evidence;
- independent validator exit 0 for intact evidence;
- non-zero validation result for tampered chain, benchmark, provenance, candidate, and safety-boundary evidence;
- no secret/private key material or raw signatures in the receipt;
- full repository test suite green;
- exact-head CI green with no unresolved blocking review/thread;
- merge only after exact-head verification.

## Decision gates

Stop autonomous work before any change that requires selecting Bitcoin consensus/Script/output/witness semantics, a production ML-DSA parameter, mainnet behavior, recovery authority, trust root, key custody, or production authorization semantics.

This checkpoint is intentionally documentation-only. It establishes a reversible Phase 3 verification direction while preserving the Phase 2 safety boundary.
