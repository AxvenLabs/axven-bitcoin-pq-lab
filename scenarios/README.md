# Neutral regtest scenario catalog

> **Research only.** Axven Bitcoin PQ Lab is not endorsed by Bitcoin Core, is not intended for mainnet deployment, and does not create or launch a coin, token, or network.

These manifests instantiate the fail-closed migration scenario contract with safe, reversible test choreography. They deliberately avoid selecting a post-quantum signature scheme, defining hybrid authorization semantics, changing Bitcoin consensus, choosing activation or fork deployment, deciding legacy/lost-UTXO treatment, assigning recovery authority, establishing trust roots, defining key custody, or freezing production security semantics.

Current catalog:

- `rollback_equivalence.json` — records experiment-off evidence, prepares reversible lab state, and requires experiment-off rollback equivalence.
- `restart_reconstruction.json` — exercises local process restart and lab-state reconstruction without assigning production recovery authority.
- `replay_context_mismatch.json` — tests replay of **lab evidence/provenance only** across mismatched experiment contexts; it does not define Bitcoin transaction replay or authorization behavior.

Every manifest is restricted to local `regtest`, declares `research_only: true`, requires upstream behavior outside the isolated experiment to remain preserved, and retains explicit high-impact decision gates.

The catalog is intentionally data-only. Later checkpoints may attach executable regtest harnesses to these manifests, but only where that can be done without crossing a deferred design decision. Any scenario requiring new Bitcoin authorization, consensus, activation, legacy-UTXO, recovery, trust-root, or custody semantics must stop at the decision gate instead of encoding a choice in test data.
