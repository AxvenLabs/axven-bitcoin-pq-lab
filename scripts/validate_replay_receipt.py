#!/usr/bin/env python3
"""Validate deterministic Phase 3 evidence-replay receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_KEYS = {
    "schema_version",
    "input_e2e_sha256",
    "validator_result",
    "validator_schema_version",
    "research_only",
    "off_consensus",
    "bitcoin_core_modified",
    "mainnet_intended",
    "parameter_set_selected",
    "replay_receipt_sha256",
}


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_replay_receipt(receipt: dict) -> str:
    """Fail closed unless a receipt is canonical, complete, and research-only."""
    if not isinstance(receipt, dict) or set(receipt) != EXPECTED_KEYS:
        raise ValueError("unexpected replay receipt fields")
    if receipt["schema_version"] != 1:
        raise ValueError("unsupported replay receipt schema")
    if not isinstance(receipt["validator_schema_version"], int):
        raise ValueError("invalid validator schema version")
    digest = receipt["input_e2e_sha256"]
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("invalid input evidence digest")
    try:
        bytes.fromhex(digest)
    except ValueError as exc:
        raise ValueError("invalid input evidence digest") from exc
    if receipt["validator_result"] != "accepted":
        raise ValueError("replay receipt is not accepted")
    expected_safety = {
        "research_only": True,
        "off_consensus": True,
        "bitcoin_core_modified": False,
        "mainnet_intended": False,
        "parameter_set_selected": False,
    }
    for key, expected in expected_safety.items():
        if receipt[key] is not expected:
            raise ValueError(f"invalid safety boundary: {key}")

    claimed = receipt["replay_receipt_sha256"]
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("invalid replay receipt digest")
    unsigned = dict(receipt)
    del unsigned["replay_receipt_sha256"]
    actual = _canonical_digest(unsigned)
    if claimed != actual:
        raise ValueError("replay receipt digest mismatch")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    print(validate_replay_receipt(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
