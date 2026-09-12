# Test vectors and benchmark contract

This document describes the first reproducible artifact layer for Axven Bitcoin PQ Lab.

> **Research only.** These artifacts do not select a post-quantum primitive, do not propose a Bitcoin consensus change, and are not evidence of mainnet readiness.

## Test-vector scope

`lab/vectors.py` exports deterministic vectors for the implementation-independent authorization-state model. The vectors cover:

- valid and invalid LEGACY authorization;
- HYBRID requiring both modeled authorization legs;
- valid and invalid PQ-mode authorization;
- chain binding;
- outpoint binding;
- destination binding;
- epoch/mode behavior through the underlying state model.

The `cryptographic_scheme` field is deliberately `null`. `legacy_ok` and `pq_ok` are model inputs, not signature implementations. They must not be interpreted as measured cryptographic security.

Export a canonical JSON document with:

```bash
python scripts/export_vectors.py
```

The default output is `artifacts/test-vectors-v1.json`. Repeated exports from the same revision must be byte-identical.

## Benchmark scope

`scripts/benchmark_model.py` measures only Python authorization-state/transcript overhead. It reports canonical context size, authorization timing, and Python `tracemalloc` peak memory.

```bash
python scripts/benchmark_model.py --iterations 10000 --rounds 7
```

It deliberately does **not** claim to measure:

- Bitcoin Script or tapscript verification;
- ECDSA or Schnorr verification;
- any post-quantum signature primitive;
- transaction or witness expansion from a selected primitive;
- node-wide CPU/RAM impact.

Those measurements become meaningful only after a cryptographic candidate and an isolated Bitcoin integration boundary are explicitly selected. Selecting either remains a gated design decision.

## Reproducibility rule

Published performance results must include the exact Git commit, Python/runtime version, operating system, command line, and raw JSON output. Comparative claims must be generated on the same host and revision unless the report says otherwise.
