# Regtest experiment isolation

> **Research only.** This lab is not endorsed by Bitcoin Core and is not intended for mainnet deployment.

REGTEST-002 introduces an explicit lab gate around the already-pinned, unmodified Bitcoin Core regtest baseline.

## Contract

- `AXVEN_PQ_EXPERIMENT=0` (and equivalent off values) delegates directly to `run_vanilla_regtest_baseline.sh`.
- Any experiment-on value fails closed with exit code 64.
- No Bitcoin Core source is patched by this checkpoint.
- No PQ primitive, hybrid authorization rule, Script/transaction consensus change, activation plan, fork deployment, legacy/lost UTXO treatment, recovery authority, trust root, key custody model, or production security semantic is selected here.

The purpose of this gate is to make the future experimental boundary explicit before implementation begins. A later experiment-on path must not be added until the relevant high-impact design decisions are made explicitly and reviewed separately.

## CI evidence

CI builds the exact pinned upstream Bitcoin Core source, runs the vanilla baseline, runs the experiment-off entrypoint, and separately proves that experiment-on currently fails closed.
