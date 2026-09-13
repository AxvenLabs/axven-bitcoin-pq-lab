# Research threat model

> **Research only.** Axven Bitcoin PQ Lab is not endorsed by Bitcoin Core and is not intended for mainnet deployment. It does not create a coin, token, or production network.

This document defines a conservative threat-model boundary for isolated Bitcoin Core regtest experiments. It is a research input, not a Bitcoin deployment proposal and not a claim that any post-quantum construction is safe.

## Scope

The lab investigates how authorization evidence associated with legacy Bitcoin UTXOs can be studied under reversible, isolated hybrid/post-quantum migration experiments. Upstream Bitcoin behavior must remain unchanged whenever the experiment is disabled and outside the isolated experiment boundary.

The machine-readable contract is `lab/threat-model-v1.json`; `scripts/validate_threat_model.py` fails closed if research labels, upstream-preservation requirements, required properties, or explicit decision gates disappear.

## Assets under observation

- integrity of legacy spend-authorization observations;
- integrity of experimental authorization evidence;
- transaction and test-vector provenance;
- benchmark and scenario provenance;
- state consistency across restart and rollback.

These are lab assets only. This document does not define production custody or recovery policy.

## Adversary capabilities to exercise

Future tests may safely model:

- stale lab-evidence replay;
- duplicated or reordered experimental messages;
- malformed or oversized authorization artifacts;
- restart or rollback during an experiment;
- mismatched regtest/network context;
- downgrade or incomplete-evidence attempts;
- CPU/RAM pressure from invalid verification inputs.

These capabilities are deliberately independent of a cryptographic algorithm or final authorization policy.

## Required research properties

Any later experiment should:

- fail closed on malformed experimental evidence;
- bind experimental evidence to explicit regtest context;
- preserve vanilla Bitcoin behavior with the experiment off;
- make replay, rollback, restart, and failure outcomes reproducible;
- record transaction/signature size and verification CPU/RAM cost without presenting them as production-security claims;
- keep every high-impact design choice behind an explicit decision gate.

## Scenario hypotheses are not decisions

The repository may test hypothetical state orders such as `LEGACY -> HYBRID -> PQ`, rollback attempts, or conjunction/disjunction variants for classical and PQ checks. Those are test hypotheses only. They must not be described as the selected Bitcoin migration path, selected hybrid semantics, or a production security policy.

In particular, this threat model does **not** decide that migration must be monotonic, that HYBRID must require both factors, that PQ-only authorization must ever be used, or how legacy/lost UTXOs should be treated. A test fixture may exercise one such hypothesis only when it is clearly labeled as a reversible scenario.

## Explicit decision gates

The following remain undecided and require an explicit user decision before any path treats them as selected semantics:

- Bitcoin consensus or mainnet activation;
- fork deployment;
- cryptographic scheme selection;
- final classical/PQ hybrid authorization semantics;
- legacy UTXO treatment;
- lost-coin treatment;
- recovery authority;
- trust roots;
- key custody;
- production security semantics.

## Non-claims and non-goals

Passing lab tests does not demonstrate Bitcoin mainnet safety, consensus compatibility, quantum resistance, or suitability of a concrete cryptographic scheme. No mainnet software, activation mechanism, fork plan, production wallet, trust authority, recovery service, coin/token, or independent network is created here. Proprietary Axven Security Engine source or internals must never be copied into this repository.

## Next safe work

With this boundary in place, scheme-neutral malformed-input vectors, resource-limit measurements, evidence replay/rollback fixtures, and benchmark harnesses can proceed. Comparing publicly specified candidate primitives by size or verification cost is research; adopting or freezing one remains a separate decision gate.
