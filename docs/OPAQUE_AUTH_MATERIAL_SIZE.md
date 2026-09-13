# Opaque authorization material structural size model

> **Research only.** This work is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

This checkpoint adds a deliberately scheme-neutral way to quantify one narrow question: if a future laboratory experiment represents authorization evidence as an opaque witness item of *N* bytes, what is the item's serialized byte cost and marginal witness weight?

It does **not** claim that Bitcoin should place post-quantum signatures in a witness item, does not choose a post-quantum algorithm, and does not define classical+PQ hybrid authorization semantics. The witness-item representation is only a reversible structural hypothesis used to expose byte-size pressure before any high-impact design decision is made.

## What is measured

For each requested opaque payload size, the model reports:

- payload bytes;
- Bitcoin CompactSize length-prefix bytes;
- serialized witness-item bytes (`prefix + payload`);
- marginal weight units for those witness bytes;
- the ceiling of that isolated marginal weight expressed in virtual-byte units.

The last value is **not** a full transaction vsize. A complete transaction has additional non-witness and witness serialization, input/output structure, script data and other overhead. Later transaction-template experiments must report that separately against the pinned vanilla-regtest baseline.

## Default size sweep

The executable defaults to neutral byte buckets rather than named cryptographic schemes: 64, 128, 256, 512, 1024, 2048 and 4096 bytes. These buckets are measurement points, not recommendations or mappings to any candidate algorithm.

Run:

```bash
python -m scripts.benchmark_auth_material_size
```

Or provide explicit reversible research points:

```bash
python -m scripts.benchmark_auth_material_size --sizes 96,512,1536,3072
```

## Decision gates deliberately left open

This checkpoint does not select or freeze:

- a post-quantum signature scheme;
- hybrid AND/OR/threshold authorization semantics;
- Bitcoin Script, witness or transaction commitment semantics;
- consensus or mainnet activation/fork deployment;
- legacy or lost UTXO treatment;
- recovery authority;
- trust roots or key custody;
- production security semantics.

Any experiment that needs one of those choices must introduce it as an explicit reviewable decision rather than silently inheriting it from this size model.

## Isolation

The script is a pure structural calculator. It does not patch, launch, or connect to Bitcoin Core, does not create a coin/token/network, and does not alter the pinned upstream regtest baseline. Proprietary Axven Security Engine source or internals are neither required nor used.
