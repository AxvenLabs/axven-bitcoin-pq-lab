# Migration and failure-state model

> Research only. This repository is not endorsed by Bitcoin Core and this document is not a Bitcoin mainnet deployment proposal.

This checkpoint studies a deliberately abstract authorization-state machine. It does **not** select a post-quantum algorithm, define a Bitcoin soft fork or hard fork, decide how legacy UTXOs should be treated, create a recovery authority, or modify Bitcoin Core consensus behavior.

## Abstract path

The model exposes only the research sequence:

`LEGACY -> HYBRID -> PQ`

A successful transition increments an abstract epoch by exactly one. The epoch exists to make stale-state and replay experiments explicit. It is not a proposed Bitcoin field or consensus rule.

## Fail-closed cases

The simulator rejects the following without mutating state:

- rollback toward an earlier authorization mode;
- replay of stale migration state;
- skipping directly across a migration stage;
- attempting to advance past the terminal `PQ` state in this abstract model.

Rejected events must preserve both mode and epoch. This lets tests distinguish a clean rejection from accidental partial state mutation.

## What this checkpoint proves

Only properties of the local research model are tested: monotonic state progression, single-step epoch advancement, and non-mutation on rejected failure paths.

It does **not** prove that any Bitcoin deployment mechanism is safe, that a hybrid or PQ construction is cryptographically secure, that lost or inactive coins can be migrated safely, or that a particular activation policy is desirable.

Those questions are explicit decision gates and remain out of scope until separately reviewed.
