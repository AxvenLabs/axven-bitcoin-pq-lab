# Threat model

## Assets

- Authorization integrity for a modeled UTXO.
- Unambiguous migration state.
- Resistance to cross-context replay.
- Reproducible evidence of accepted/rejected transitions.

## Adversary model

The initial lab assumes an adversary may:

- Replay a previously valid authorization in a different context.
- Present only one authorization factor during a hybrid stage.
- Attempt to move backward from post-quantum-only state to a weaker state.
- Reorder or repeat migration operations.
- Substitute an authorization transcript from another outpoint or lab-chain identifier.
- Trigger partial failures between validation and state application.

The initial lab does **not** claim resistance to attacks on any specific post-quantum primitive because no primitive is selected yet.

## Security properties

### T1 — State monotonicity

The normal migration path is `LEGACY -> HYBRID -> PQ`. A transition that weakens authorization is rejected by default.

### T2 — Hybrid conjunction

In `HYBRID`, both abstract verifier classes must authorize the spend. This is a research default for the model, not a Bitcoin deployment decision.

### T3 — Context binding

Authorization is bound to a deterministic transcript containing at least:

- lab/chain identifier,
- outpoint,
- migration epoch,
- destination commitment,
- authorization mode.

### T4 — Replay rejection

An authorization from one context must not authorize another context when any bound field differs.

### T5 — Atomic state application

A failed authorization or transition must not partially mutate migration state.

### T6 — Explicit undecided cryptography

The model must not encode a concrete PQ algorithm until that decision is made explicitly.

## Non-claims

Passing these tests does not demonstrate Bitcoin mainnet safety, consensus compatibility, quantum resistance, or suitability of any concrete cryptographic scheme.
