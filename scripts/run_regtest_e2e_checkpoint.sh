#!/usr/bin/env bash
set -euo pipefail

# Research only. Not endorsed by Bitcoin Core. Not intended for mainnet.
# Runs an unmodified Bitcoin Core regtest node and emits observed chain evidence.
# ML-DSA is an off-consensus laboratory layer; Bitcoin Core does not validate it.
BIN_DIR="${1:-}"
[[ -n "${BIN_DIR}" ]] || { echo "usage: $0 /path/to/bitcoin-core/build/bin [benchmark-iterations]" >&2; exit 2; }
BENCHMARK_ITERATIONS="${2:-25}"
[[ "${BENCHMARK_ITERATIONS}" =~ ^[0-9]+$ && "${BENCHMARK_ITERATIONS}" -ge 3 ]] || { echo "benchmark iterations must be an integer >= 3" >&2; exit 2; }
BITCOIND="${BIN_DIR}/bitcoind"; BITCOIN_CLI="${BIN_DIR}/bitcoin-cli"
[[ -x "${BITCOIND}" && -x "${BITCOIN_CLI}" ]] || { echo "missing Bitcoin Core executables" >&2; exit 2; }

DATADIR="$(mktemp -d -t axven-btc-pq-e2e-XXXXXX)"
EVIDENCE_DIR="$(mktemp -d -t axven-btc-pq-evidence-XXXXXX)"
cleanup() { "${BITCOIN_CLI}" -regtest -datadir="${DATADIR}" stop >/dev/null 2>&1 || true; rm -rf "${DATADIR}" "${EVIDENCE_DIR}"; }
trap cleanup EXIT
"${BITCOIND}" -regtest -datadir="${DATADIR}" -daemonwait -server -listen=0 -dnsseed=0 -fixedseeds=0 -fallbackfee=0.0002 >/dev/null
CLI=("${BITCOIN_CLI}" -regtest -datadir="${DATADIR}" -rpcwait)

"${CLI[@]}" createwallet e2e >/dev/null
MINER="$("${CLI[@]}" -rpcwallet=e2e getnewaddress miner)"
"${CLI[@]}" generatetoaddress 101 "${MINER}" >/dev/null
DEST="$("${CLI[@]}" -rpcwallet=e2e getnewaddress observed-utxo)"
TXID="$("${CLI[@]}" -rpcwallet=e2e sendtoaddress "${DEST}" 1.0)"
BLOCK_HASH="$("${CLI[@]}" generatetoaddress 1 "${MINER}" | python3 -c 'import json,sys; print(json.load(sys.stdin)[0])')"
BLOCK_HEIGHT="$("${CLI[@]}" getblockheader "${BLOCK_HASH}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["height"])')"
TX="$("${CLI[@]}" getrawtransaction "${TXID}" true "${BLOCK_HASH}")"
read -r VOUT CONFIRMATIONS AMOUNT < <("${CLI[@]}" -rpcwallet=e2e listunspent 1 9999999 "[\"${DEST}\"]" | python3 -c 'import json,sys; t=sys.argv[1]; r=[x for x in json.load(sys.stdin) if x["txid"]==t]; assert len(r)==1; x=r[0]; print(x["vout"],x["confirmations"],x["amount"])' "${TXID}")
read -r TX_HEX TX_SIZE TX_WEIGHT TX_VSIZE < <(printf '%s' "${TX}" | python3 -c 'import json,sys; x=json.load(sys.stdin); print(x["hex"],x["size"],x["weight"],x["vsize"])')
MESSAGE_DIGEST="$(printf '%s:%s' "${TXID}" "${VOUT}" | sha256sum | awk '{print $1}')"

python3 -m scripts.regtest_chain_evidence \
  --txid "${TXID}" --vout "${VOUT}" --amount-btc "${AMOUNT}" --confirmations "${CONFIRMATIONS}" \
  --block-hash "${BLOCK_HASH}" --block-height "${BLOCK_HEIGHT}" --tx-hex "${TX_HEX}" \
  --tx-size "${TX_SIZE}" --tx-weight "${TX_WEIGHT}" --tx-vsize "${TX_VSIZE}" > "${EVIDENCE_DIR}/chain.json"

python3 -m scripts.regtest_mldsa_composition \
  --txid "${TXID}" --vout "${VOUT}" --message-digest "${MESSAGE_DIGEST}" > "${EVIDENCE_DIR}/composition.json"

# Descriptive raw benchmark/resource evidence for all three candidates. This is
# deliberately separate from the correctness oracle and does not rank/select a
# deployment parameter set. Linux/WSL is the demonstrated resource environment;
# native Windows `resource` portability remains open.
python3 -m scripts.regtest_benchmark_evidence --iterations "${BENCHMARK_ITERATIONS}" > "${EVIDENCE_DIR}/benchmark.json"

# Emit one canonical top-level envelope that binds the independently generated
# chain, correctness/composition, and benchmark evidence digests.
python3 -m scripts.regtest_e2e_evidence \
  --chain "${EVIDENCE_DIR}/chain.json" \
  --composition "${EVIDENCE_DIR}/composition.json" \
  --benchmark "${EVIDENCE_DIR}/benchmark.json"
