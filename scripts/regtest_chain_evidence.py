#!/usr/bin/env python3
"""Canonical public chain evidence for the real-regtest research checkpoint.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This module records observations from an unmodified Bitcoin Core regtest node. It
does not define Bitcoin Script/output/witness semantics, change consensus, select
an ML-DSA deployment parameter set, or make Bitcoin Core validate ML-DSA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, InvalidOperation


def _canonical_sha256(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_chain_evidence(*, txid: str, vout: int, amount_btc: str, confirmations: int,
                         block_hash: str, block_height: int, tx_hex: str,
                         tx_size: int, tx_weight: int, tx_vsize: int) -> dict:
    if len(txid) != 64 or any(c not in "0123456789abcdef" for c in txid):
        raise ValueError("txid must be 64 lowercase hex characters")
    if len(block_hash) != 64 or any(c not in "0123456789abcdef" for c in block_hash):
        raise ValueError("block_hash must be 64 lowercase hex characters")
    if vout < 0 or confirmations < 1 or block_height < 0:
        raise ValueError("invalid confirmed outpoint metadata")
    if len(tx_hex) % 2 or any(c not in "0123456789abcdef" for c in tx_hex):
        raise ValueError("tx_hex must be lowercase even-length hex")
    if tx_size != len(tx_hex) // 2 or tx_size <= 0 or tx_weight <= 0 or tx_vsize <= 0:
        raise ValueError("transaction metrics are inconsistent")
    if tx_vsize != (tx_weight + 3) // 4:
        raise ValueError("vsize must equal ceil(weight/4)")
    try:
        amount = Decimal(amount_btc)
    except InvalidOperation as exc:
        raise ValueError("amount_btc must be decimal") from exc
    if amount <= 0:
        raise ValueError("amount_btc must be positive")

    payload = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "parameter_set_selected": False,
        "outpoint": {"txid": txid, "vout": vout, "amount_btc": format(amount, "f"), "confirmations": confirmations},
        "confirmation": {"block_hash": block_hash, "block_height": block_height},
        "transaction": {
            "raw_tx_sha256": hashlib.sha256(bytes.fromhex(tx_hex)).hexdigest(),
            "serialized_bytes": tx_size,
            "weight": tx_weight,
            "vbytes": tx_vsize,
        },
    }
    return {**payload, "chain_evidence_sha256": _canonical_sha256(payload)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--txid", required=True)
    p.add_argument("--vout", type=int, required=True)
    p.add_argument("--amount-btc", required=True)
    p.add_argument("--confirmations", type=int, required=True)
    p.add_argument("--block-hash", required=True)
    p.add_argument("--block-height", type=int, required=True)
    p.add_argument("--tx-hex", required=True)
    p.add_argument("--tx-size", type=int, required=True)
    p.add_argument("--tx-weight", type=int, required=True)
    p.add_argument("--tx-vsize", type=int, required=True)
    a = p.parse_args()
    report = build_chain_evidence(txid=a.txid, vout=a.vout, amount_btc=a.amount_btc,
        confirmations=a.confirmations, block_hash=a.block_hash, block_height=a.block_height,
        tx_hex=a.tx_hex, tx_size=a.tx_size, tx_weight=a.tx_weight, tx_vsize=a.tx_vsize)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
