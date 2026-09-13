#!/usr/bin/env bash
set -euo pipefail

# Research only. Not endorsed by Bitcoin Core. Not intended for mainnet.
# This runs an unmodified Bitcoin Core regtest node, observes one real UTXO,
# restarts the node, verifies the UTXO survives reconstruction, and emits a
# decision-gated report. It does not implement PQ or hybrid authorization.

BIN_DIR="${1:-}"
if [[ -z "${BIN_DIR}" ]]; then
  echo "usage: $0 /path/to/bitcoin-core/build/bin" >&2
  exit 2
fi

BITCOIND="${BIN_DIR}/bitcoind"
BITCOIN_CLI="${BIN_DIR}/bitcoin-cli"
[[ -x "${BITCOIND}" ]] || { echo "missing executable: ${BITCOIND}" >&2; exit 2; }
[[ -x "${BITCOIN_CLI}" ]] || { echo "missing executable: ${BITCOIN_CLI}" >&2; exit 2; }

DATADIR="$(mktemp -d -t axven-btc-pq-preflight-XXXXXX)"
cleanup() {
  "${BITCOIN_CLI}" -regtest -datadir="${DATADIR}" stop >/dev/null 2>&1 || true
  rm -rf "${DATADIR}"
}
trap cleanup EXIT

start_node() {
  "${BITCOIND}" \
    -regtest \
    -datadir="${DATADIR}" \
    -daemonwait \
    -server \
    -listen=0 \
    -dnsseed=0 \
    -fixedseeds=0 \
    -fallbackfee=0.0002 >/dev/null
}

start_node
CLI=("${BITCOIN_CLI}" -regtest -datadir="${DATADIR}" -rpcwait)

"${CLI[@]}" createwallet preflight >/dev/null
MINER_ADDRESS="$("${CLI[@]}" -rpcwallet=preflight getnewaddress "miner")"
"${CLI[@]}" generatetoaddress 101 "${MINER_ADDRESS}" >/dev/null
DESTINATION="$("${CLI[@]}" -rpcwallet=preflight getnewaddress "observed-utxo")"
TXID="$("${CLI[@]}" -rpcwallet=preflight sendtoaddress "${DESTINATION}" 1.0)"
"${CLI[@]}" generatetoaddress 1 "${MINER_ADDRESS}" >/dev/null

read -r VOUT CONFIRMATIONS AMOUNT_BTC < <(
  "${CLI[@]}" -rpcwallet=preflight listunspent 1 9999999 "[\"${DESTINATION}\"]" |
    python3 -c 'import json,sys; txid=sys.argv[1]; rows=[r for r in json.load(sys.stdin) if r["txid"] == txid]; assert len(rows)==1; r=rows[0]; print(r["vout"], r["confirmations"], r["amount"])' "${TXID}"
)

[[ "$("${CLI[@]}" getblockchaininfo | python3 -c 'import json,sys; print(json.load(sys.stdin)["chain"])')" == "regtest" ]]
[[ "${CONFIRMATIONS}" -ge 1 ]]

# Restart against the same datadir to exercise real state reconstruction.
"${CLI[@]}" stop >/dev/null
for _ in $(seq 1 50); do
  if ! kill -0 "$(cat "${DATADIR}/regtest/bitcoind.pid" 2>/dev/null || echo 0)" 2>/dev/null; then
    break
  fi
  sleep 0.1
done
start_node

UTXO_AFTER_RESTART="$("${CLI[@]}" gettxout "${TXID}" "${VOUT}")"
[[ -n "${UTXO_AFTER_RESTART}" ]]
RESTART_CONFIRMATIONS="$(printf '%s' "${UTXO_AFTER_RESTART}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["confirmations"])')"
[[ "${RESTART_CONFIRMATIONS}" -ge 1 ]]

# The experiment-on path must still fail closed until security decisions are explicit.
if python3 -m scripts.run_regtest_lab --mode on --bin-dir "${BIN_DIR}" >/tmp/axven-pq-on.out 2>/tmp/axven-pq-on.err; then
  echo "experiment-on unexpectedly succeeded" >&2
  exit 1
fi
grep -q "experimental mode is intentionally unavailable" /tmp/axven-pq-on.err

python3 -m scripts.regtest_demo_preflight \
  --txid "${TXID}" \
  --vout "${VOUT}" \
  --confirmations "${RESTART_CONFIRMATIONS}" \
  --amount-btc "${AMOUNT_BTC}"
