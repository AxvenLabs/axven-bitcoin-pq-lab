# BENCH-RUNTIME-005 — neutral CPU/RAM harness calibration

> **Research only.** This work is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

This checkpoint adds a deliberately scheme-neutral local microbenchmark so the lab can validate its CPU/RAM measurement harness before selecting any post-quantum candidate.

It measures a deterministic byte-processing workload and reports wall-clock timing plus Python allocation peaks. These values are **not** post-quantum signature verification results and must not be presented as such.

## Purpose

The lab ultimately needs reproducible measurements for verification cost, CPU pressure and memory impact. Before introducing any cryptographic candidate, this benchmark establishes that the reporting path itself is runnable, deterministic in input/output, and fail-closed around invalid parameters.

Run:

```bash
python -m scripts.benchmark_neutral_runtime --sizes 64,256,1024,4096 --iterations 500 --rounds 5
```

The output is JSON and includes research-scope metadata, per-case timing, Python allocation peaks and a deterministic result digest.

## Interpretation limits

- Timing is host-dependent and should only be compared with recorded environment provenance.
- `tracemalloc` measures Python allocations, not total process RSS or native-library memory.
- The SHA-256 loop is harness calibration only. It is not a proxy for any PQ signature scheme.
- No Bitcoin transaction, Script, witness, consensus or authorization semantics are changed.

## Decision gates left open

This checkpoint does not select or freeze:

- a post-quantum signature scheme;
- hybrid AND/OR/threshold authorization semantics;
- Bitcoin consensus or mainnet activation/fork deployment;
- legacy or lost UTXO treatment;
- recovery authority;
- trust roots or key custody;
- production security semantics.

Any future benchmark that evaluates an actual cryptographic candidate must introduce that candidate as an explicit reviewable research choice rather than inheriting one from this harness.

## Isolation

The benchmark does not patch, launch or connect to Bitcoin Core, does not create a coin/token/network, and does not use or expose proprietary Axven Security Engine source or internals. Upstream Bitcoin behavior outside the isolated experiment remains unchanged.
