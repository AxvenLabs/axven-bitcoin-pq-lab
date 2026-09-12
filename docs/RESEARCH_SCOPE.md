# Research scope

## Objective

Study authorization migration for Bitcoin-style UTXOs in an isolated, reproducible lab before considering any Bitcoin integration proposal.

The initial model is deliberately cryptography-agnostic. `legacy` and `pq` are abstract verifier classes, not concrete algorithms.

## In scope

- Legacy -> hybrid -> post-quantum authorization-state transitions.
- Domain-separated authorization transcripts.
- Replay rejection across chain/lab identifiers, outpoints, and migration epochs.
- Rollback and partial-failure behavior.
- Deterministic test vectors.
- Regtest-only integration experiments after the abstract model is stable.
- Size, verification-cost, CPU, and memory measurements.

## Out of scope unless explicitly decided later

- Bitcoin mainnet deployment.
- A BIP or activation mechanism.
- Hard/soft fork selection.
- Treatment of lost or dormant coins.
- Recovery authorities or trust roots.
- Key-custody policy.
- Selection of a concrete post-quantum signature scheme.
- Changes to Bitcoin monetary policy.
- A new coin, token, or production network.

## Isolation rule

Experiments must be additive and isolated. Upstream Bitcoin behavior outside an explicitly enabled regtest/lab path must remain unchanged.

## Decision gates

The following require an explicit design decision before implementation is locked to them:

1. Concrete PQ signature scheme and parameter set.
2. Exact Bitcoin script/transaction commitment mechanism.
3. Consensus deployment/activation semantics.
4. Legacy UTXO migration and expiry policy.
5. Lost-coin/recovery policy.
6. Trust roots or privileged recovery actors.
7. Production key lifecycle/custody semantics.
