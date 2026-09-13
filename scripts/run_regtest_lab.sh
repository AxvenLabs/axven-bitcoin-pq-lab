#!/usr/bin/env bash
set -euo pipefail

# Research-only Bitcoin Core regtest lab entrypoint.
# Experiment-off delegates to the unmodified vanilla baseline.
# Experiment-on is intentionally unavailable until explicit design decisions are made.

BIN_DIR="${1:-}"
MODE="${AXVEN_PQ_EXPERIMENT:-0}"

if [[ -z "${BIN_DIR}" ]]; then
  echo "usage: $0 /path/to/bitcoin-core/build/bin" >&2
  exit 2
fi

case "${MODE}" in
  0|off|OFF|false|FALSE)
    exec bash "$(dirname "$0")/run_vanilla_regtest_baseline.sh" "${BIN_DIR}"
    ;;
  *)
    echo "experimental PQ authorization path is intentionally not implemented; explicit cryptographic/consensus/security-semantics decisions are required first" >&2
    exit 64
    ;;
esac
