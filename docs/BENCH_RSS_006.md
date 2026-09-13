# BENCH-RSS-006 — process max-RSS calibration

> **Research only.** This work is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

This checkpoint extends the neutral benchmark harness with a process-memory measurement path based on `resource.getrusage().ru_maxrss`.

It exists only to calibrate memory evidence collection before any post-quantum cryptographic candidate is selected. It is not a post-quantum verification benchmark and does not claim to measure Bitcoin Script or signature-verification memory cost.

## Run

```bash
python -m scripts.benchmark_process_memory --mebibytes 8
```

The tool records process max-RSS before and after touching a deterministic local allocation and emits JSON suitable for later reproducibility checks.

## Platform handling

`ru_maxrss` has different units on common Unix platforms. The harness normalizes Linux KiB and macOS bytes into bytes. Unknown platforms fail closed instead of silently generating incomparable evidence.

## Interpretation limits

- max-RSS is a high-water mark, not instantaneous RSS;
- allocator/runtime behavior can affect the observed delta;
- this checkpoint measures only the measurement path itself;
- results must be paired with benchmark environment provenance before comparison;
- the workload is not a proxy for any cryptographic scheme.

## Decision gates left open

This checkpoint does not select or freeze:

- a post-quantum signature scheme;
- hybrid AND/OR/threshold authorization semantics;
- Bitcoin consensus or mainnet activation/fork deployment;
- legacy or lost UTXO treatment;
- recovery authority;
- trust roots or key custody;
- production security semantics.

## Isolation

No Bitcoin Core code is patched or launched by this benchmark. No coin, token, or network is created. Proprietary Axven Security Engine source or internals are neither used nor copied. Upstream Bitcoin behavior outside the isolated experiment remains unchanged.
