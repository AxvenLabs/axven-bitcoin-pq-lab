#!/usr/bin/env bash
set -euo pipefail

# Research-only vanilla Bitcoin Core regtest baseline.
# This script does not patch Bitcoin Core and does not define any PQ, consensus,
# activation, recovery, or mainnet behavior.

BIN_DIR="${1:-}"
if [[ -z "${BIN_DIR}" ]]; then
  echo "usage: $0 /path/to/bitcoin-core/build/bin" >&2
  exit 2
fi

BITCOIND="${BIN_DIR}/bitcoind"
BITCOIN_CLI="${BIN_DIR}/bitcoin-cli"
[[ -x "${BITCOIND}" ]] || { echo "missing executable: ${BITCOIND}" >&2; exit 2; }
[[ -x "${BITCOIN_CLI}" ]] || { echo "missing executable: ${BITCOIN_CLI}" >&2; exit 2; }

DATADIR="$(mktemp -d -t axven-btc-regtest-XXXXXX)"
cleanup() {
  "${BITCOIN_CLI}" -regtest -datadir="${DATADIR}" stop >/dev/null 2>&1 || true
  rm -rf "${DATADIR}"
}
trap cleanup EXIT

"${BITCOIND}" \
  -regtest \
  -datadir="${DATADIR}" \
  -daemonwait \
  -server \
  -listen=0 \
  -dnsseed=0 \
  -fixedseeds=0 \
  -fallbackfee=0.0002 >/dev/null

CLI=("${BITCOIN_CLI}" -regtest -datadir="${DATADIR}" -rpcwait)

"${CLI[@]}" createwallet baseline >/dev/null
MINER_ADDRESS="$("${CLI[@]}" -rpcwallet=baseline getnewaddress "miner")"
"${CLI[@]}" generatetoaddress 101 "${MINER_ADDRESS}" >/dev/null

DESTINATION="$("${CLI[@]}" -rpcwallet=baseline getnewaddress "destination")"
TXID="$("${CLI[@]}" -rpcwallet=baseline sendtoaddress "${DESTINATION}" 1.0)"
"${CLI[@]}" generatetoaddress 1 "${MINER_ADDRESS}" >/dev/null

CHAIN="$("${CLI[@]}" getblockchaininfo | python3 -c 'import json,sys; print(json.load(sys.stdin)["chain"])')"
BLOCKS="$("${CLI[@]}" getblockcount)"
CONFIRMATIONS="$("${CLI[@]}" -rpcwallet=baseline gettransaction "${TXID}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["confirmations"])')"
VERSION="$("${CLI[@]}" getnetworkinfo | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])')"

[[ "${CHAIN}" == "regtest" ]]
[[ "${BLOCKS}" -eq 102 ]]
[[ "${CONFIRMATIONS}" -ge 1 ]]

python3 - "${VERSION}" "${BLOCKS}" "${TXID}" "${CONFIRMATIONS}" <<'PY'
import json
import sys

version, blocks, txid, confirmations = sys.argv[1:]
print(json.dumps({
    "blocks": int(blocks),
    "chain": "regtest",
    "confirmations": int(confirmations),
    "research_only": True,
    "transaction_created_and_mined": True,
    "txid": txid,
    "upstream_version": int(version),
}, sort_keys=True))
PY
