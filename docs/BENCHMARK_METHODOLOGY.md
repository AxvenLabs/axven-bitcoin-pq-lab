# Benchmark methodology and report contract

This document defines a reproducible reporting contract for future Axven Bitcoin PQ Lab measurements.

> **Research only.** This project is not endorsed by Bitcoin Core, is not intended for mainnet deployment, and this methodology does not define or recommend a Bitcoin consensus change.

## Why a report contract exists

A benchmark result is useful only when another researcher can tell what was measured, against which source identity, on what machine, and with enough raw observations to recompute the summary. The lab therefore keeps benchmark methodology separate from cryptographic or consensus design choices.

The contract applies to future structural, verification-cost, CPU, and memory experiments. It does **not** make a post-quantum scheme selection and does not define hybrid authorization semantics.

## Required provenance

Every report produced under this contract must record:

- a human-readable benchmark name;
- a category describing the measurement rather than a cryptographic recommendation;
- the exact source identity under test;
- a UTC timestamp for the run;
- operating-system and machine architecture identifiers;
- CPU model and logical CPU count;
- total memory visible to the benchmark process;
- tool/runtime version information relevant to the runner;
- warm-up count, repetition count, unit, and raw samples.

Source identity must be an immutable commit or release identity where possible. A report that cannot identify its tested source must fail closed rather than be presented as comparable evidence.

## Sampling rules

Timed or resource-cost benchmarks must use an explicit warm-up phase followed by repeated measured samples. The current report helper requires at least three measured samples; later benchmark-specific checkpoints may require more.

Reports retain the raw samples. Median and p95 are derived values and must be recomputable from those samples. The helper uses the nearest-rank definition for p95 and the standard median definition. No single sample is presented as representative performance.

Machine-to-machine comparisons must not be described as speedups unless the environments are controlled or the limitation is explicitly stated. Structural measurements such as serialized transaction size can be compared independently of CPU speed, but cryptographic timing cannot.

## Baseline separation

Vanilla Bitcoin Core observations remain distinct from experiment-on observations. Experimental results must never overwrite or relabel the vanilla baseline. A later comparison may join two reports only after verifying that their provenance and metric units are compatible.

The existing vanilla transaction-structure checkpoint remains a structural baseline. It is **not** a post-quantum verification benchmark.

## Failure rules

The benchmark tooling must reject reports when:

- provenance is absent or malformed;
- research-only labeling is absent;
- warm-up/repetition counts are invalid;
- raw samples are missing, non-numeric, boolean, negative, or non-finite;
- the declared repetition count differs from the sample count;
- a unit is empty;
- a derived median or p95 does not match the raw samples.

Fail-closed validation is intentional: malformed benchmark evidence should not silently enter later comparison tables.

## Deferred decisions

This methodology intentionally does **not** choose:

- a post-quantum signature scheme;
- classical+PQ hybrid authorization semantics;
- Bitcoin Script or transaction commitment semantics;
- consensus or mainnet activation/fork deployment;
- treatment of legacy or lost UTXOs;
- recovery authority, trust roots, or key custody.

Those remain explicit decision gates. A future cryptographic benchmark must name its candidate and assumptions in a separate reviewable checkpoint rather than changing this generic methodology silently.
