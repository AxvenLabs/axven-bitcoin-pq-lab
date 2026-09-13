# Vanilla regtest transaction baseline

This checkpoint records transaction-structure metrics from an **unmodified**, exactly pinned Bitcoin Core regtest build before any experiment-on authorization work exists.

> Research only. This project is not endorsed by Bitcoin Core, is not intended for mainnet deployment, and this baseline does not define or recommend a Bitcoin consensus change.

## Purpose

A future experimental authorization path needs a classical reference point that can be reproduced independently. `scripts/run_vanilla_transaction_benchmark.sh` creates and confirms a normal regtest transaction, asks Bitcoin Core for the verbose decoded transaction, and passes that observation through a fail-closed metric extractor.

The current baseline reports:

- serialized transaction bytes;
- virtual size in vbytes;
- transaction weight units;
- input and output counts;
- number of inputs carrying witness data;
- witness item count and individual witness item byte lengths;
- total bytes carried by witness stack items.

These are **structural Bitcoin transaction measurements**, not post-quantum measurements. They do not claim signature-verification timing, cryptographic security, memory cost, or production throughput.

## Reproducibility and comparison rules

The benchmark runs only against the exact upstream source identity in `upstream/bitcoin-core.json`. CI verifies that identity before the Bitcoin Core build and benchmark are executed.

The output is JSON so later experiment-on runs can use the same metric vocabulary. Future comparison code must keep the vanilla observation separate from the experimental observation rather than replacing the baseline.

Transaction identifiers and exact signature bytes are intentionally not treated as deterministic golden values because isolated wallets create fresh keys and signatures. Structural fields are measured from each run.

## Deferred decisions

This checkpoint intentionally does **not** choose:

- a post-quantum signature scheme;
- classical+PQ hybrid authorization semantics;
- a Bitcoin Script or transaction commitment design;
- consensus or mainnet activation/fork deployment;
- treatment of legacy or lost UTXOs;
- recovery authority, trust roots, or key custody.

Those decisions remain explicit gates. Benchmarking a future cryptographic candidate will require a separate, reviewable research decision and must not silently change the meaning of this vanilla baseline.
