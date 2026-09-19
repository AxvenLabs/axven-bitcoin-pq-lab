# Phase 4A Baseline and Reproducibility

Status: research-only, off-consensus baseline gate.

This checkpoint starts Phase 4 from current main without regenerating or overwriting historical Phase 2/3 evidence.

## Exact repository baseline

- Phase 4A base main: `da1e00631b7ab718671279602950cb3ede55ccb3`
- Historical Phase 2 final-results document is preserved unchanged.
- Historical Phase 3 live-replay-results document is preserved unchanged.

## Pinned research environment

Repository pins used by the baseline gate:

- Bitcoin Core tag: `v31.1`
- Bitcoin Core source commit: `9be056a8a72b624dae9623b2f7bded92c2a21c91`
- Bitcoin Core annotated tag object: `bfa6a4b79cd4c1562fd32857e3147763efae37fb`
- CI Python: `3.12`
- ML-DSA research backend: `cryptography==48.0.0`
- CI OS/architecture: GitHub-hosted Ubuntu x86-64 runner; exact runner image details remain execution metadata rather than a hard-coded research claim.

The existing provenance evidence format separately records runtime Python, cryptography, OpenSSL, OS, machine, repository commit, Bitcoin binary digests, and Bitcoin source identity for live evidence runs.

## Baseline reproducibility gate

The Phase 4A workflow installs the already-pinned ML-DSA backend and runs the complete Python regression discovery so backend-dependent tests are executed rather than skipped. It then rebuilds and independently validates the existing deterministic public regtest vector manifest twice and requires byte-identical canonical JSON plus identical validated digests.

This gate does not regenerate or overwrite Phase 2 or Phase 3 historical evidence files.

## Scope boundary

- research-only
- regtest/off-consensus
- Bitcoin Core remains unmodified
- no Script, opcode, output, witness, consensus, activation, or mainnet behavior change
- no production PQ signature scheme or parameter set selection
- no custody, recovery, trust-root, or production authorization policy
- Bitcoin Core does not validate ML-DSA in this lab

## Phase 4 direction

Phase 4 will add adversarial/reproducibility evidence only after this baseline remains green. Existing vector/bundle infrastructure will be extended rather than replaced.

Before proposal-specific conformance work, the exact upstream proposal revision must be pinned and reviewed. No proposal is adopted or ranked by this checkpoint.
