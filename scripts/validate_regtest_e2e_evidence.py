#!/usr/bin/env python3
"""Independent fail-closed validator for the public regtest E2E evidence envelope.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
Bitcoin Core/Script/consensus remain unmodified; Bitcoin Core does not validate
ML-DSA. This validator does not select or rank an ML-DSA deployment parameter set.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_CANDIDATES = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_e2e_evidence(evidence: dict) -> str:
    required = {
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
        "bitcoin_core_validates_mldsa": False,
        "native_windows_resource_portability_demonstrated": False,
        "hybrid_research_semantics": "classical-and-pq",
        "candidate_order": EXPECTED_CANDIDATES,
    }
    for key, expected in required.items():
        if evidence.get(key) != expected:
            raise ValueError(f"unexpected {key}")

    for key in ("chain_evidence_sha256", "composition_sha256", "benchmark_evidence_sha256"):
        value = evidence.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError(f"invalid {key}")

    outpoint = evidence.get("outpoint", {})
    txid = outpoint.get("txid")
    if not isinstance(txid, str) or len(txid) != 64 or any(c not in "0123456789abcdef" for c in txid):
        raise ValueError("invalid outpoint txid")
    if not isinstance(outpoint.get("vout"), int) or outpoint["vout"] < 0:
        raise ValueError("invalid outpoint vout")

    confirmation = evidence.get("confirmation", {})
    block_hash = confirmation.get("block_hash")
    if not isinstance(block_hash, str) or len(block_hash) != 64 or any(c not in "0123456789abcdef" for c in block_hash):
        raise ValueError("invalid confirmation block hash")
    if not isinstance(confirmation.get("block_height"), int) or confirmation["block_height"] < 0:
        raise ValueError("invalid confirmation block height")

    tx = evidence.get("transaction", {})
    raw_hash = tx.get("raw_tx_sha256")
    if not isinstance(raw_hash, str) or len(raw_hash) != 64 or any(c not in "0123456789abcdef" for c in raw_hash):
        raise ValueError("invalid raw transaction digest")
    for key in ("serialized_bytes", "weight", "vbytes"):
        if not isinstance(tx.get(key), int) or tx[key] <= 0:
            raise ValueError(f"invalid transaction {key}")
    if tx["vbytes"] != (tx["weight"] + 3) // 4:
        raise ValueError("inconsistent transaction vbytes")

    claimed = evidence.get("e2e_evidence_sha256")
    if not isinstance(claimed, str):
        raise ValueError("missing E2E evidence digest")
    payload = dict(evidence)
    del payload["e2e_evidence_sha256"]
    actual = _digest(payload)
    if claimed != actual:
        raise ValueError("E2E evidence digest mismatch")
    return actual


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("report", type=Path)
    a = p.parse_args()
    evidence = json.loads(a.report.read_text())
    print(validate_e2e_evidence(evidence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
