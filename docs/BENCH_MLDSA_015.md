# BENCH-MLDSA-015 — structural size adapter

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint maps the named reversible ML-DSA-44/65/87 research-candidate public-key and signature byte sizes into the lab's existing scheme-neutral opaque witness-item structural model.

The adapter reports each public key and signature independently. It does **not** define a Bitcoin transaction layout, witness stack, Script/output commitment, consensus rule, activation path, legacy/lost UTXO treatment, recovery authority, trust root, key custody model, or production security semantics. It also does not select an ML-DSA deployment winner.

The approved isolated research hypothesis remains **ML-DSA + Classical AND PQ**. The size evidence here is only a reproducible comparison input for later experiments; Bitcoin validation behavior remains unchanged.
