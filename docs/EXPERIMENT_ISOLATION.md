# Experiment isolation contract

> **Research only.** This lab is not endorsed by Bitcoin Core, is not intended for mainnet deployment, and does not define a Bitcoin consensus change.

## Purpose

Before any post-quantum experiment exists, the lab establishes a fail-closed boundary between vanilla Bitcoin Core behavior and future experimental behavior.

`--mode off` is the only supported lab mode. It delegates to the pinned vanilla Bitcoin Core regtest baseline without patching Bitcoin Core. `--mode on` is intentionally unavailable and must fail before invoking Bitcoin binaries.

This checkpoint does **not** choose a post-quantum signature scheme, hybrid authorization rule, activation mechanism, legacy UTXO policy, lost-coin policy, recovery authority, trust root, key-custody design, or other consensus/security semantic.

## Equivalence check

CI executes two isolated runs against the same pinned upstream Bitcoin Core build:

1. the direct vanilla baseline;
2. the lab entry point with `--mode off`.

The comparator requires the following observable fields to match exactly:

- chain;
- block height;
- transaction confirmation count;
- upstream version;
- research-only marker;
- successful transaction creation/mining marker.

Transaction IDs are not compared because each isolated wallet run creates fresh keys and therefore fresh transactions.

## Fail-closed rule

Any experimental mode is rejected until a separately reviewed implementation exists. Adding such an implementation must remain isolated and must not silently redefine cryptographic, activation, recovery, or legacy-UTXO semantics.
