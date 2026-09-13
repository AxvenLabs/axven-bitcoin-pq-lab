# Migration scenario contract

> **Research only.** Axven Bitcoin PQ Lab is not endorsed by Bitcoin Core, is not intended for mainnet deployment, and does not launch a new coin, token, or network.

This contract defines a machine-checkable envelope for future migration, rollback, replay, and failure scenarios before any cryptographic or consensus design is selected.

## Purpose

A migration experiment should state what it is trying to observe without silently deciding Bitcoin policy. Scenario manifests therefore separate **measurement and failure choreography** from **high-impact design choices**.

Every accepted scenario must:

- be restricted to `regtest`;
- declare `research_only: true`;
- preserve upstream Bitcoin behavior outside the isolated experiment path;
- provide explicit assumptions, ordered steps, expected observations, and evidence names;
- retain explicit decision gates for cryptographic, consensus, activation, legacy-UTXO, recovery, trust-root, and key-custody questions.

The validator fails closed if a scenario attempts to embed a high-impact decision field such as a PQ scheme, hybrid authorization semantics, mainnet activation, fork deployment, legacy/lost-UTXO policy, recovery authority, trust root, or key-custody rule.

## Scenario phases

The neutral phase vocabulary is deliberately limited:

- `baseline` — capture vanilla/regtest evidence before the experiment;
- `prepare` — arrange reversible lab state;
- `exercise` — execute a bounded experiment without implying production semantics;
- `rollback` — disable/revert the isolated experiment and record the result;
- `recovery` — exercise a lab failure-recovery path without assigning production recovery authority.

These phase labels are test choreography only. They do not imply a Bitcoin deployment lifecycle.

## Expectations

Each step records one of four neutral expectations:

- `accept` — a lab assertion expects acceptance under already-defined experimental rules;
- `reject` — a lab assertion expects rejection under already-defined experimental rules;
- `unchanged` — the compared baseline must remain behaviorally unchanged;
- `observe` — collect evidence without prescribing an authorization outcome.

A future scenario that needs new authorization semantics must first cross an explicit design decision gate; this contract cannot be used to smuggle that choice into test data.

## Replay, rollback, and failure coverage

The same manifest shape can describe safe future tests for:

- replaying an experimental artifact against an incompatible lab state and observing rejection;
- disabling an isolated experiment and confirming vanilla-regtest equivalence;
- process restart and state reconstruction;
- interrupted migration preparation followed by rollback;
- malformed or incomplete experimental evidence failing closed.

The contract does not yet define the cryptographic artifact being replayed or migrated. That remains intentionally deferred.

## Deferred decisions

The following remain out of scope until explicitly reviewed:

1. post-quantum signature scheme selection;
2. classical+PQ hybrid authorization semantics;
3. Bitcoin transaction/script/commitment or consensus changes;
4. mainnet activation or fork deployment;
5. treatment of legacy UTXOs or lost coins;
6. recovery authority and exceptional-spend policy;
7. trust roots and key custody;
8. production security semantics.

Until those gates are resolved, scenario work remains reversible regtest research only.
