# Test vectors and benchmark contract

> **Research only.** This repository is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

This document describes reproducible artifact layers for Axven Bitcoin PQ Lab while keeping high-impact Bitcoin migration and security choices explicitly unresolved.

## Existing authorization-state model vectors

`lab/vectors.py` exports deterministic vectors for an implementation-independent authorization-state **hypothesis model**. The model currently contains LEGACY, HYBRID, and PQ labels and includes a conjunction-style HYBRID example. Those are reversible research hypotheses used to exercise transcript/state machinery; they are **not selected Bitcoin migration semantics**, a consensus proposal, or a recommendation that hybrid authorization must require both legs.

The `cryptographic_scheme` field is deliberately `null`. `legacy_ok` and `pq_ok` are model inputs, not signature implementations. They must not be interpreted as measured cryptographic security or as a selected post-quantum scheme.

Export the deterministic model vectors with:

```bash
python -m scripts.export_vectors
```

The default output is `artifacts/test-vectors-v1.json`. Repeated exports from the same revision must be byte-identical.

## Scheme-neutral research scenario vectors

`vectors/research-scenario-vectors-v1.json` is a second, deliberately scheme-neutral fixture layer. It records expectations for rollback, restart/failure recovery, lab-evidence context replay rejection, and migration decision-gate handling without defining Bitcoin transaction authorization semantics.

Validate the checked-in scenario vectors with:

```bash
python -m scripts.validate_research_vectors
```

The validator fails closed if research-only labeling, regtest/lab scope, upstream-preservation intent, or required high-impact decision gates disappear. It also rejects fields that would silently encode several irreversible choices.

The replay vector is about **lab evidence context**, not Bitcoin transaction replay semantics. It must not be cited as defining transaction validity or authorization behavior.

## Explicit decision gates

Any future migration experiment must stop before implementation if it requires selecting or freezing:

- a post-quantum cryptographic scheme;
- classical+PQ hybrid authorization semantics;
- Bitcoin consensus, activation, or fork deployment;
- treatment of legacy or lost UTXOs;
- recovery authority;
- trust roots;
- key custody;
- production security semantics.

These decisions require separate review. The existing hypothesis model must not be treated as having already answered them.

## Benchmark scope

`scripts/benchmark_model.py` measures only Python authorization-state/transcript overhead. It reports canonical context size, authorization timing, and Python `tracemalloc` peak memory.

```bash
python -m scripts.benchmark_model --iterations 10000 --rounds 7
```

It deliberately does **not** claim to measure Bitcoin Script/tapscript verification, ECDSA/Schnorr verification, any post-quantum signature primitive, transaction/witness expansion from a selected primitive, or node-wide CPU/RAM impact. Those measurements become meaningful only after a candidate and isolated integration boundary are explicitly selected through a decision gate.

## Reproducibility rule

Published performance results must include the exact Git commit, Python/runtime version, operating system, command line, and raw JSON output. Comparative claims must be generated on the same host and revision unless the report says otherwise. Upstream Bitcoin Core behavior outside the isolated experiment remains the reference behavior.
