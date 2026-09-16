# REGTEST-DEMO-013 — candidate-neutral ML-DSA composition

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This reversible checkpoint composes the existing off-consensus ML-DSA laboratory harness into the real-regtest E2E path introduced by REGTEST-DEMO-012. The runner binds the observed real regtest outpoint to all three candidates (ML-DSA-44/65/87), records valid-signature acceptance and altered-transcript rejection, and records both Classical=true/PQ=true and Classical=false/PQ=true authorization outcomes.

No candidate is selected. The classical result remains an external laboratory boolean oracle. Bitcoin Core does not validate ML-DSA. Bitcoin Core/Script/consensus remain unmodified, and no Script/output/witness semantics, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production authorization semantics are defined.

REGTEST-DEMO-013 does not yet add benchmark timing/CPU/RSS to the final composed evidence report and does not close native Windows `resource` portability. Those remain separate reversible work items; WSL/Linux remains the demonstrated environment.
