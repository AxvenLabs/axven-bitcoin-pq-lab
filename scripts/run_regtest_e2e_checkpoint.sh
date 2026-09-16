#!/usr/bin/env bash
set -euo pipefail
# Research only; unmodified Bitcoin Core regtest; off-consensus ML-DSA laboratory evidence.
BIN_DIR="${1:-}"; ITER="${2:-25}"; SOURCE_DIR="${3:-}"; OUT="${4:-}"
[[ -n "$BIN_DIR" && -n "$SOURCE_DIR" && -n "$OUT" ]] || { echo "usage: $0 BITCOIN_BIN_DIR ITERATIONS BITCOIN_SOURCE_DIR ARTIFACT_DIR" >&2; exit 2; }
[[ "$ITER" =~ ^[0-9]+$ && "$ITER" -ge 3 ]] || { echo "iterations must be >=3" >&2; exit 2; }
BITCOIND="$BIN_DIR/bitcoind"; BITCOIN_CLI="$BIN_DIR/bitcoin-cli"; [[ -x "$BITCOIND" && -x "$BITCOIN_CLI" ]] || exit 2
SOURCE_COMMIT="$(git -C "$SOURCE_DIR" rev-parse HEAD)"; TAG_OBJECT="$(git -C "$SOURCE_DIR" rev-parse 'refs/tags/v31.1^{tag}')"; TAG_COMMIT="$(git -C "$SOURCE_DIR" rev-list -n1 v31.1)"
[[ "$SOURCE_COMMIT" == "9be056a8a72b624dae9623b2f7bded92c2a21c91" && "$TAG_COMMIT" == "$SOURCE_COMMIT" && "$TAG_OBJECT" == "bfa6a4b79cd4c1562fd32857e3147763efae37fb" ]] || { echo "Bitcoin Core source provenance mismatch" >&2; exit 3; }
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"; DATADIR="$(mktemp -d -t axven-btc-pq-e2e-XXXXXX)"
cleanup(){ "$BITCOIN_CLI" -regtest -datadir="$DATADIR" stop >/dev/null 2>&1 || true; rm -rf "$DATADIR"; }; trap cleanup EXIT
"$BITCOIND" -regtest -datadir="$DATADIR" -daemonwait -server -listen=0 -dnsseed=0 -fixedseeds=0 -fallbackfee=0.0002 >/dev/null
CLI=("$BITCOIN_CLI" -regtest -datadir="$DATADIR" -rpcwait); "${CLI[@]}" createwallet e2e >/dev/null; MINER="$("${CLI[@]}" -rpcwallet=e2e getnewaddress miner)"; "${CLI[@]}" generatetoaddress 101 "$MINER" >/dev/null
DEST="$("${CLI[@]}" -rpcwallet=e2e getnewaddress observed-utxo)"; TXID="$("${CLI[@]}" -rpcwallet=e2e sendtoaddress "$DEST" 1.0)"; BLOCK_HASH="$("${CLI[@]}" generatetoaddress 1 "$MINER"|python3 -c 'import json,sys;print(json.load(sys.stdin)[0])')"
BLOCK_HEIGHT="$("${CLI[@]}" getblockheader "$BLOCK_HASH"|python3 -c 'import json,sys;print(json.load(sys.stdin)["height"])')"; TX="$("${CLI[@]}" getrawtransaction "$TXID" true "$BLOCK_HASH")"
read -r VOUT CONFIRMATIONS AMOUNT < <("${CLI[@]}" -rpcwallet=e2e listunspent 1 9999999 "[\"$DEST\"]"|python3 -c 'import json,sys;t=sys.argv[1];r=[x for x in json.load(sys.stdin) if x["txid"]==t];assert len(r)==1;x=r[0];print(x["vout"],x["confirmations"],x["amount"])' "$TXID")
read -r TX_HEX TX_SIZE TX_WEIGHT TX_VSIZE < <(printf '%s' "$TX"|python3 -c 'import json,sys;x=json.load(sys.stdin);print(x["hex"],x["size"],x["weight"],x["vsize"])'); MSG="$(printf '%s:%s' "$TXID" "$VOUT"|sha256sum|awk '{print $1}')"
python3 -m scripts.regtest_chain_evidence --txid "$TXID" --vout "$VOUT" --amount-btc "$AMOUNT" --confirmations "$CONFIRMATIONS" --block-hash "$BLOCK_HASH" --block-height "$BLOCK_HEIGHT" --tx-hex "$TX_HEX" --tx-size "$TX_SIZE" --tx-weight "$TX_WEIGHT" --tx-vsize "$TX_VSIZE" > "$OUT/chain.json"
python3 -m scripts.regtest_mldsa_composition --txid "$TXID" --vout "$VOUT" --message-digest "$MSG" > "$OUT/composition.json"
python3 -m scripts.regtest_benchmark_evidence --iterations "$ITER" > "$OUT/benchmark.json"
REPO_COMMIT="$(git rev-parse HEAD)"; VERSION="$("$BITCOIND" --version|head -n1)"; PY="$(python3 -c 'import platform;print(platform.python_version())')"; CRYPTO="$(python3 -c 'import cryptography;print(cryptography.__version__)')"; OPENSSL="$(python3 -c 'from cryptography.hazmat.backends.openssl.backend import backend;print(backend.openssl_version_text())')"; OS="$(python3 -c 'import platform;print(platform.platform())')"; MACHINE="$(python3 -c 'import platform;print(platform.machine())')"
BD_SHA="$(sha256sum "$BITCOIND"|awk '{print $1}')"; CLI_SHA="$(sha256sum "$BITCOIN_CLI"|awk '{print $1}')"
python3 -m scripts.regtest_provenance_evidence --repo-commit "$REPO_COMMIT" --bitcoin-version "$VERSION" --source-commit "$SOURCE_COMMIT" --tag v31.1 --tag-object "$TAG_OBJECT" --bitcoind-sha256 "$BD_SHA" --bitcoin-cli-sha256 "$CLI_SHA" --python-version "$PY" --cryptography-version "$CRYPTO" --openssl-version "$OPENSSL" --os-name "$OS" --machine "$MACHINE" > "$OUT/provenance.json"
python3 -m scripts.validate_regtest_provenance_evidence "$OUT/provenance.json" > "$OUT/provenance-validator.txt"
python3 -m scripts.regtest_e2e_evidence --chain "$OUT/chain.json" --composition "$OUT/composition.json" --benchmark "$OUT/benchmark.json" --provenance "$OUT/provenance.json" > "$OUT/e2e.json"
python3 -m scripts.validate_regtest_e2e_evidence "$OUT/e2e.json" | tee "$OUT/e2e-validator.txt"
sha256sum "$OUT/e2e.json" > "$OUT/e2e-file.sha256"
echo "ARTIFACT_DIR=$OUT"; echo "CANONICAL_EVIDENCE_SHA256=$(cat "$OUT/e2e-validator.txt")"; echo "E2E_FILE_SHA256=$(awk '{print $1}' "$OUT/e2e-file.sha256")"
