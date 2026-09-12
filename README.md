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

The scheme-neutral authorization model, deterministic migration/replay tests, canonical test-vector generator, and a non-cryptographic benchmark harness are now implemented. See [`docs/TEST_VECTORS.md`](docs/TEST_VECTORS.md).

Cryptographic scheme selection and Bitcoin consensus/activation choices remain intentionally **undecided**. No benchmark currently claims Bitcoin Script, Schnorr/ECDSA, or post-quantum signature performance.

## Project structure

```text
docs/        research scope, threat model, decision records
lab/         implementation-independent research model
scripts/     reproducible experiment/benchmark entry points
tests/       deterministic tests and vector contracts
```

## Relationship to Axven

This is an independent public research lab maintained by AxvenLabs. It may inform Axven research, but it is deliberately separated from Axven Core and Axven Security Engine.
