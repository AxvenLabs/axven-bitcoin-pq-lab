# Failure and rollback research model

> **Research only.** This document describes a test harness for isolated migration experiments. It is not endorsed by Bitcoin Core, is not a mainnet deployment design, and does not select Bitcoin consensus, storage, activation, recovery, or cryptographic semantics.

## Purpose

`FAILURE-001` adds a minimal crash-point harness around the existing abstract authorization-state migration model.

The harness tests one implementation-independent safety property:

> A migration observation is atomic: after an interruption, an observer sees either the complete pre-migration state or the complete committed post-migration state, never a prepared/intermediate state.

This is useful before Bitcoin Core integration because later regtest adapters can be checked against the same old-or-new observation property without changing the abstract oracle.

## Crash points

The test harness injects interruption at four deterministic points:

1. before prepare;
2. after prepare;
3. immediately before commit;
4. immediately after commit.

Pre-commit interruption exposes the original state. Post-commit interruption exposes the migrated state. Invalid transitions fail without visible mutation.

## Non-decisions

The harness deliberately does **not** decide:

- how Bitcoin Core should persist experimental migration metadata;
- whether any migration should exist in Bitcoin consensus;
- activation or deployment semantics;
- script/opcode/transaction commitment design;
- a post-quantum signature scheme or parameter set;
- legacy/lost UTXO treatment;
- recovery authority or trust roots;
- production key custody or recovery semantics.

`MigrationRecord` is therefore a deterministic in-memory research object, not a proposed database or consensus structure.

## Reproduction

```bash
python -m unittest tests.test_failure -v
python -m unittest discover -s tests -v
```

A future Bitcoin Core regtest adapter may consume this contract only behind an explicit experimental boundary. With the experiment disabled, upstream Bitcoin behavior must remain unchanged.
