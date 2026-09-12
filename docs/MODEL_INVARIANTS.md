# Abstract model invariant audit

> **Research only.** This checkpoint audits the implementation-independent state model used by the Axven Bitcoin PQ Lab. It is not endorsed by Bitcoin Core, is not intended for mainnet deployment, and does not select a post-quantum signature scheme, Bitcoin consensus rule, activation mechanism, legacy/lost UTXO policy, recovery authority, trust root, key-custody design, or production security semantic.

## Purpose

`MODEL-AUDIT-001` strengthens the model oracle before any Bitcoin Core regtest adapter is allowed to depend on it.

The audit deliberately stays below cryptographic and Bitcoin-consensus design. It checks deterministic state-machine properties over a bounded but exhaustive small state/event space so later integration work has a sharper regression oracle.

## Checked properties

The test suite asserts that:

- every rejected event leaves the complete visible state unchanged;
- accepted events never decrease the epoch;
- repeated execution of every event sequence of length 0 through 4 is deterministic for representative LEGACY, HYBRID, and PQ starting states;
- repeating a rejected event remains rejected and state-preserving;
- only an accepted `ADVANCE` event may change visible mode/epoch state, and any such change advances the epoch by exactly one.

These are research-model invariants only. They do not define how Bitcoin should authorize spends or how a future hybrid mode must combine classical and post-quantum signatures.

## Reproduction

```bash
python -m unittest tests.test_model_invariants -v
python -m unittest discover -s tests -v
```

## Integration gate

A future regtest adapter may use this model only as a test oracle behind an isolated experiment boundary. The adapter must separately demonstrate that disabling the experiment preserves upstream Bitcoin behavior.
