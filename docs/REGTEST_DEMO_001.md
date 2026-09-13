# REGTEST-DEMO-001 — decision-gated real regtest preflight

> **Research only.** This work is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

This checkpoint is the first step from isolated benchmark infrastructure toward an experiment-on regtest demo while preserving every high-impact decision gate.

It runs an **unmodified pinned Bitcoin Core regtest node**, creates and confirms a real wallet transaction, identifies a real spendable UTXO, restarts the node against the same datadir, verifies the UTXO remains observable after reconstruction, and emits a machine-readable research report.

The demo also verifies that `scripts.run_regtest_lab --mode on` still **fails closed**. No experimental authorization is allowed to run until explicit security decisions are made.

## Run

After building the pinned Bitcoin Core version described by this repository:

```bash
bash scripts/run_regtest_demo_preflight.sh /path/to/bitcoin-core/build/bin
```

The final line is JSON describing the observed regtest UTXO and the still-open decision gates.

## What this proves

- the lab can bind research evidence to a real Bitcoin Core regtest UTXO;
- Bitcoin Core remains unmodified;
- restart/state reconstruction is exercised against the real regtest datadir;
- experiment-on remains fail-closed;
- upstream behavior is not replaced by the lab;
- no coin, token, or new network is created.

## What this does **not** prove

This is not a post-quantum authorization implementation and is not evidence that any particular migration design is safe. It does not benchmark a PQ signature scheme, define Bitcoin Script behavior, or establish consensus rules.

## Explicit decision gate reached

A true experiment-on authorization path now requires at least these user-approved research decisions:

1. **Post-quantum candidate scheme** to evaluate. Choosing a candidate for testing does not imply production selection, but the implementation must name what it is measuring.
2. **Hybrid authorization semantics** for the isolated experiment, such as classical **AND** PQ, classical **OR** PQ, or another explicitly defined research policy.

The following remain open even after those two research choices and must not be silently selected: Bitcoin consensus changes, activation/fork deployment, legacy UTXO treatment, lost-coin treatment, recovery authority, trust roots, key custody, and production security semantics.

## Separation boundary

This repository is separate from Axven Core and Axven Security Engine. Proprietary Axven Security Engine source or internals are neither used nor copied.
