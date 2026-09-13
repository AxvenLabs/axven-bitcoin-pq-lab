# BENCH-VERIFY-007 — scheme-neutral verifier harness

> **Research only.** This work is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

This checkpoint adds a generic verifier-call benchmark interface before any post-quantum signature candidate is selected. It is deliberately incapable of making a cryptographic choice on its own.

The bundled `calibration_verifier` is **not cryptographic verification**. It exists only to exercise timing, Python allocation measurement, report shape, fail-closed behavior, and byte-length accounting.

## Run

```bash
python -m scripts.benchmark_verifier_harness --iterations 100
```

The JSON report records the generic callable path, input byte lengths, median/min/max wall-clock nanoseconds, and Python peak allocation bytes.

## What the numbers do not mean

Results from the bundled calibration callable are not:

- post-quantum signature verification cost;
- Bitcoin Script verification cost;
- consensus-validation cost;
- evidence for selecting any cryptographic scheme;
- evidence for selecting hybrid AND/OR/threshold semantics.

A real candidate verifier may only be plugged into this interface as an explicitly named research candidate. Comparing candidates does not select one. Any decision to freeze a scheme or production security semantic remains a user decision gate.

## Decision gates left open

This checkpoint does not select or freeze:

- a post-quantum signature scheme;
- hybrid AND/OR/threshold authorization semantics;
- Bitcoin consensus rules, mainnet activation, or fork deployment;
- legacy or lost UTXO treatment;
- recovery authority;
- trust roots or key custody;
- production security semantics.

## Isolation

No Bitcoin Core code is modified or launched by this benchmark. No coin, token, or network is created. Proprietary Axven Security Engine source or internals are neither used nor copied. Upstream Bitcoin behavior outside the isolated experiment remains unchanged.
