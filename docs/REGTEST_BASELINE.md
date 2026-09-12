# Vanilla Bitcoin Core regtest baseline

> **Research only.** This lab is not endorsed by Bitcoin Core, is not intended for mainnet deployment, and this baseline does not propose or implement a Bitcoin consensus change.

This checkpoint establishes an upstream behavior oracle before any post-quantum experiment is connected to Bitcoin Core.

## Pinned upstream

The exact upstream identity is defined in `upstream/bitcoin-core.json` and verified before the baseline is built or run.

## Baseline scenario

`scripts/run_vanilla_regtest_baseline.sh` runs an unmodified pinned Bitcoin Core build and:

1. starts an isolated regtest node with networking disabled;
2. creates a local wallet;
3. mines 101 blocks so a coinbase output becomes spendable;
4. creates a 1 BTC wallet transaction;
5. mines the transaction into one additional block;
6. asserts that the chain is `regtest`, the height is 102, and the transaction is confirmed;
7. emits a compact JSON result.

The transaction id is intentionally not treated as a deterministic test vector because the wallet generates fresh keys. The contract is behavioral: a vanilla pinned node can create, mine, and confirm the transaction in an isolated regtest environment.

## Why this matters

Future experimental integration must be able to demonstrate that, when the experiment is disabled, this upstream baseline remains unchanged. This checkpoint therefore creates a reference behavior before any experimental adapter exists.

## Explicit non-decisions

This baseline does **not** select a post-quantum signature primitive, define hybrid signature semantics, change Script or transaction consensus, select an activation mechanism, define legacy/lost UTXO treatment, create a recovery authority, choose trust roots or key custody, launch a network, or modify mainnet behavior.
