# REGTEST-DEMO-002 — ML-DSA + classical-AND-PQ research contract

> **Research only.** This work is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

This checkpoint records the user-approved **isolated regtest research choices** needed to move beyond the decision-gated preflight:

- post-quantum candidate family: **ML-DSA**;
- hybrid research semantics: **classical AND PQ**.

These are deliberately scoped as reversible experimental choices for the public Axven Bitcoin PQ Lab. They are not Bitcoin consensus rules, a BIP, an activation proposal, a fork plan, or production deployment guidance.

## What is intentionally still undecided

This checkpoint does **not** select:

- an ML-DSA parameter set (ML-DSA-44, ML-DSA-65, or ML-DSA-87);
- a Bitcoin Script or output-commitment design;
- consensus or mainnet activation rules;
- fork deployment policy;
- legacy or lost UTXO treatment;
- recovery authority;
- trust roots;
- key custody;
- production security semantics.

Named ML-DSA parameter sets may be measured as separate research candidates without declaring any one of them the deployment choice.

## Fail-closed policy

`lab/regtest-demo-002-policy.json` is machine-readable and is validated by `scripts/validate_regtest_demo_policy.py`. The validator rejects silent changes to the approved research family/AND semantics and rejects any accidental enabling of the protected high-impact decision fields.

The associated tests verify that changing the research policy to classical-OR-PQ, another PQ family, or any protected high-impact choice fails closed.

## Separation boundary

This repository remains separate from Axven Core and Axven Security Engine. No proprietary Axven Security Engine source or internals are used or copied. Bitcoin Core remains upstream and unmodified outside the isolated lab harness.

## Next safe milestone

The next reversible step is to add **candidate benchmarking adapters** for ML-DSA parameter sets and compare size/verification/CPU/RAM characteristics. Candidate measurement does not itself select a production parameter set. A parameter-set selection, Script/commitment design, consensus change, or deployment policy remains an explicit decision gate.
