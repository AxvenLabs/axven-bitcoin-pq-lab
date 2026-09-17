# Axven Bitcoin PQ Lab

Experimental research on post-quantum migration for Bitcoin UTXO authorization.

> **Research only.** This project is not endorsed by Bitcoin Core, is not intended for mainnet deployment, and does not propose a Bitcoin consensus change in its current form.

The lab studies how a legacy authorization path could migrate through an explicitly modeled hybrid stage toward a post-quantum authorization path while preserving auditability, replay resistance, rollback safety, and deterministic testability.

## Safety boundaries

- No new coin or token.
- No production network launch.
- No mainnet deployment instructions.
- No silent choice of post-quantum signature scheme.
- No silent policy for legacy/lost UTXOs, recovery authority, trust roots, or activation.
- No Axven Security Engine proprietary code or internals.
- Bitcoin behavior outside isolated research experiments must remain unchanged.

## Research plan

1. Specify threat model and non-goals.
2. Build an implementation-independent authorization-state model.
3. Add deterministic replay, rollback, failure, and migration tests.
4. Add regtest-only Bitcoin integration behind explicit experimental boundaries.
5. Add reproducible benchmarks for transaction/signature size, verification cost, CPU, and memory.
6. Publish test vectors and documented assumptions.

## Status

Phase 2 has reached an evidence-complete research checkpoint. On evaluated main commit `901a1fbe7b98cf41d16dd67a3218fc8d54374f5d`, the final WSL/Linux suite completed **239/239 tests successfully**. The independent E2E validator reproduced canonical evidence SHA-256 `d3fdb272903fb6112db18ec6ad044fbe268937a3302da626914e540cdf863540` exactly.

The off-consensus experiment records candidate-neutral ML-DSA-44/65/87 measurements and tested Classical AND PQ laboratory semantics against real Bitcoin Core v31.1 regtest transaction evidence. Bitcoin Core, consensus and Script remain unmodified by the experiment; Bitcoin Core does not validate ML-DSA. No production ML-DSA parameter set, Script/output/witness semantics, activation/fork deployment, recovery authority, trust root, key custody or production authorization semantics are selected.

See [`docs/PHASE2_FINAL_RESULTS.md`](docs/PHASE2_FINAL_RESULTS.md) for the final Phase 2 evidence, provenance, benchmark scope, validation result and limitations.

Phase 3 now has a live deterministic replay evidence checkpoint. A fresh Bitcoin Core v31.1 regtest evidence envelope was independently validated, replayed twice to byte-identical receipts, accepted by an independent replay-receipt validator, and a controlled receipt-digest tamper was rejected fail-closed. This remains research-only and off-consensus; it does not add or select Bitcoin Script, opcode, output/witness, activation, mainnet, recovery, trust-root, custody, production authorization, or production ML-DSA semantics.

See [`docs/PHASE3_LIVE_REPLAY_RESULTS.md`](docs/PHASE3_LIVE_REPLAY_RESULTS.md) for the exact tested checkpoint, provenance, fresh evidence digests, deterministic replay result, independent receipt validation, controlled tamper rejection, and limitations. Historical checkpoint documents remain unchanged as an auditable research trail.

## Project structure

```text
docs/        research scope, threat model, decision records
lab/         implementation-independent research model
scripts/     reproducible experiment/benchmark entry points
tests/       deterministic tests and vector contracts
```

## Relationship to Axven

This is an independent public research lab maintained by AxvenLabs. It may inform Axven research, but it is deliberately separated from Axven Core and Axven Security Engine.
