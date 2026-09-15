# REGTEST-DEMO-011 — fail-closed transcript tamper regression

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint converts the independently observed real-regtest evidence-tamper behavior into regression tests. An untampered ML-DSA-44 laboratory report must validate, while changing only the bound outpoint `vout` or only the bound message digest without rebuilding the evidence must fail closed as a non-canonical research transcript.

The checkpoint tests public report/evidence integrity and transcript binding. It does **not** claim Bitcoin Core validates ML-DSA, does not define network-level replay protection, does not expose raw signatures or private material, and does not select an ML-DSA deployment parameter set.

Bitcoin Core remains unmodified and the experiment remains off-consensus on regtest. No Bitcoin Script/output/witness semantics, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production security semantics are selected. No coin/token/network is created, and no Axven Security Engine source or internals are used or copied.
