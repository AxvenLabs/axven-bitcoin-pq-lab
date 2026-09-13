#!/usr/bin/env bash
set -euo pipefail

# Research-only structural benchmark for an unmodified Bitcoin Core regtest
# transaction. This does not benchmark PQ cryptography and does not define any
# Bitcoin consensus, activation, recovery, key-custody, or mainnet behavior.

BIN_DIR="${1:-}"
if [[ -z "${BIN_DIR}" ]]; then
  echo "usage: $0 /path/to/bitcoin-core/build/bin" >&2
  exit 2
fi

BITCOIND="${BIN_DIR}/bitcoind"
BITCOIN_CLI="${BIN_DIR}/bitcoin-cli"
[[ -x "${BITCOIND}" ]] || { echo "missing executable: ${BITCOIND}" >&2; exit 2; }
[[ -x "${BITCOIN_CLI}" ]] || { echo "missing executable: ${BITCOIN_CLI}" >&2; exit 2; }

DATADIR="$(mktemp -d -t axven-btc-bench-XXXXXX)"
TX_JSON="${DATADIR}/tx.json"
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
"${CLI[@]}" createwallet benchmark >/dev/null
MINER_ADDRESS="$("${CLI[@]}" -rpcwallet=benchmark getnewaddress "miner" "bech32")"
"${CLI[@]}" generatetoaddress 101 "${MINER_ADDRESS}" >/dev/null
DESTINATION="$("${CLI[@]}" -rpcwallet=benchmark getnewaddress "destination" "bech32")"
TXID="$("${CLI[@]}" -rpcwallet=benchmark sendtoaddress "${DESTINATION}" 1.0)"
"${CLI[@]}" generatetoaddress 1 "${MINER_ADDRESS}" >/dev/null

# getrawtransaction without txindex is not guaranteed to locate a confirmed
# transaction by txid alone. Resolve the containing block from the wallet and
# pass that exact block hash so this benchmark works with the same unmodified
# Bitcoin Core build and does not weaken the node configuration by enabling
# an extra index solely for measurement.
BLOCKHASH="$("${CLI[@]}" -rpcwallet=benchmark gettransaction "${TXID}" | python3 -c 'import json, sys; obj=json.load(sys.stdin); blockhash=obj.get("blockhash"); confirmations=obj.get("confirmations", 0); assert isinstance(blockhash, str) and len(blockhash) == 64 and confirmations > 0, "transaction must be confirmed with a blockhash"; print(blockhash)')"
"${CLI[@]}" getrawtransaction "${TXID}" true "${BLOCKHASH}" >"${TX_JSON}"

python3 -m scripts.transaction_metrics "${TX_JSON}"
