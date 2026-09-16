# REGTEST-DEMO-015 — compose benchmark evidence into the real-regtest E2E runner

**Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.**

This checkpoint composes the already-reviewed raw ML-DSA benchmark/resource evidence path into `scripts/run_regtest_e2e_checkpoint.sh`. After the unmodified Bitcoin Core regtest chain evidence and candidate-neutral ML-DSA/Classical-AND-PQ composition steps, the runner now invokes `scripts.regtest_benchmark_evidence` for ML-DSA-44, ML-DSA-65, and ML-DSA-87.

The benchmark output records raw verification wall-clock and process-CPU samples plus Python peak allocation and process max RSS. Correctness-oracle checks remain separate. The evidence is descriptive and does not rank candidates or select a Bitcoin deployment parameter set.

The optional second runner argument controls benchmark iterations and must be an integer >= 3; the default remains 25.

Bitcoin Core/Script/consensus remain unmodified. Bitcoin Core does not validate ML-DSA. No Script/output/witness semantics, parameter-set selection, activation/fork deployment, legacy/lost UTXO treatment, recovery authority, trust roots, key custody, or production authorization semantics are defined. Native Windows Python `resource` portability remains open; Linux/WSL remains the demonstrated resource-measurement environment.
